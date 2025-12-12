import streamlit as st
import smartsheet
from datetime import datetime, timedelta, timezone
import pandas as pd
import time

st.set_page_config(page_title="Registro de Producto Terminado", layout="wide")

ALMACEN_PASSWORD = st.secrets["ALMACEN_PASSWORD"]

# ============================================================
# SMARTSHEET CLIENT (GLOBAL)
# ============================================================

SMARTSHEET_TOKEN = st.secrets["SMARTSHEET_TOKEN"]
SHEET_ID = int(st.secrets["SHEET_ID"])

client = smartsheet.Smartsheet(SMARTSHEET_TOKEN)
client.errors_as_exceptions(True)

def cargar_sheet_y_col_ids():
    sheet = client.Sheets.get_sheet(SHEET_ID)

    # Mapa: "titulo_columna" -> columnId
    col_ids = {c.title.strip().lower(): c.id for c in sheet.columns}

    # Valida que existan (ajusta nombres si tus columnas se llaman distinto)
    requeridas = ["cuarto", "numero_parte", "numero_orden", "cantidad", "fecha_hora",
                  "recolectado", "empaque", "checklist", "cierre", "notas"]
    faltan = [x for x in requeridas if x not in col_ids]
    if faltan:
        st.error(f"Faltan columnas en Smartsheet: {faltan}. Revisa títulos exactos.")
        st.stop()

    return sheet, col_ids

sheet, COL_ID = cargar_sheet_y_col_ids()

# ============================================================
# FUNCIÓN → CARGAR DATOS DESDE SMARTSHEET
# ============================================================

@st.cache_data(ttl=30) # 🔄 cache inteligente (30 segundos)
def cargar_desde_smartsheet():
    sheet = client.Sheets.get_sheet(SHEET_ID)

    rows_data = []

    for row in sheet.rows:
        data = {"row_id": row.id}

        for cell in row.cells:
            for key, col_id in COL_ID.items():
                if cell.column_id == col_id:
                    data[key] = cell.value

        # ⛔ descartar filas completamente vacías
        valores = [v for k, v in data.items() if k != "row_id"]
        if any(v not in [None, ""] for v in valores):
            rows_data.append(data)

    return pd.DataFrame(rows_data).fillna("")

# =============================
# ENCABEZADO CORPORATIVO
# =============================

st.markdown("""
    <style>
        .encabezado-container {
            width: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 25px 0 20px 0;
            margin-bottom: -10px;
        }
        .titulo-nordson {
            font-size: 38px;
            font-weight: 600;
            color: #0072CE; /* Azul Nordson */
            font-family: Arial, Helvetica, sans-serif;
            letter-spacing: 1px;
        }
        .subtitulo-nordson {
            font-size: 20px;
            font-weight: 400;
            color: #555555;
            font-family: Arial, Helvetica, sans-serif;
            margin-top: -8px;
            letter-spacing: 0.5px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="encabezado-container">
    <div class="titulo-nordson">NORDSON MEDICAL</div>
    <div class="subtitulo-nordson">Registro de Producto Terminado</div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# ESTILOS VISUALES - MODO CLARO
# ============================================================

st.markdown(
    """
    <style>
        body, .stApp { background-color: #f4f4f4 !important; }

        .stButton>button {
            background-color: #004A99;
            color: white;
            border-radius: 6px;
            padding: 8px 15px;
        }
        .stButton>button:hover {
            background-color: #003A77;
        }

        .success-message {
            padding: 12px;
            background-color: #d8ffd8;
            border-left: 5px solid #2ecc71;
            border-radius: 5px;
            color: #256d2a;
            font-weight: bold;
            font-size: 16px;
        }

        .titulo-seccion {
            font-size: 30px;
            font-weight: bold;
            margin-top: 10px;
            color: #222;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("""
    <style>

        /* Fuerza la tabla editable a ocupar todo el ancho del contenedor */
        div[data-testid="stDataEditor"] > div {
            width: 100% !important;
        }

        /* Ajusta la tabla interna y evita que quede comprimida */
        div[data-testid="stDataEditor-Viewport"] {
            width: 100% !important;
            overflow-x: auto !important;
        }

        /* Fuerza el contenedor del bloque donde vive el editor */
        div[data-testid="stVerticalBlock"] {
            width: 100% !important;
        }

    </style>
    """, unsafe_allow_html=True)

lista_cuartos = [
    "INTRODUCER","PU1","PU2","PU3","PU4","PVC1","PVC2","PVC3A","PVC3B",
    "PVC6","PVC7","PVC8","PVC9","PVCS","PAK1","MGLY","MASM1","MMCL",
    "MM MOLD","MMFP","RESORTES"
]

# ============================================================
# TABS
# ============================================================

tab1, tab2 = st.tabs(["➕ Registrar Orden", "📦 Almacén"])

# ============================================================
# TAB 1 – REGISTRAR PRODUCTO TERMINADO (CORREGIDO)
# ============================================================

with tab1:

    col_izq, col_centro, col_der = st.columns([1, 2, 1])

    with col_centro:

        st.header("Registrar Producto Terminado")

        # ----------------------------------------------------
        # FORMULARIO (manejo automático del estado)
        # ----------------------------------------------------
        with st.form("form_registro_pt", clear_on_submit=True):

            cuarto = st.selectbox(
                "Cuarto",
                lista_cuartos
            )

            numero_parte = st.text_input(
                "Número de Parte"
            )

            numero_orden = st.text_input(
                "Número de Orden"
            )

            cantidad = st.number_input(
                "Cantidad",
                min_value=1,
                step=1,
                value=1
            )

            guardar = st.form_submit_button("Guardar Registro")

        # ----------------------------------------------------
        # GUARDAR EN SMARTSHEET
        # ----------------------------------------------------
        if guardar:

            if not numero_parte or not numero_orden:
                st.error("❌ Número de parte y número de orden son obligatorios")

            else:
                try:
                    # Fecha con ajuste horario
                    fecha_hora = datetime.now() - timedelta(hours=7)

                    # Crear fila
                    new_row = smartsheet.models.Row()
                    new_row.to_top = True # 👈 se agrega al INICIO

                    new_row.cells = [
                        {"column_id": COL_ID["cuarto"], "value": cuarto},
                        {"column_id": COL_ID["numero_parte"], "value": numero_parte},
                        {"column_id": COL_ID["numero_orden"], "value": numero_orden},
                        {"column_id": COL_ID["cantidad"], "value": cantidad},
                        {
                            "column_id": COL_ID["fecha_hora"],
                            "value": fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
                        }
                    ]

                    client.Sheets.add_rows(SHEET_ID, [new_row])

                    st.success("✅ Registro guardado correctamente")

                except Exception as e:
                    st.error("❌ Error al guardar en Smartsheet")
                    st.write(e)

# ============================================================
# TAB 2 — PANEL DE ALMACÉN
# ============================================================

with tab2:

    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = time.time()

    now = time.time()

    #Forzar refresh cada 30 segundos
    if now - st.session_state.last_refresh > 30:
        cargar_desde_smartsheet.clear() # limpia cache
        st.session_state.last_refresh = now

    df = cargar_desde_smartsheet()

    st.caption(
        f"🔄 Última actualización automática: {time.strftime('%H:%M:%S', time.localtime(st.session_state.last_refresh))}"
    )

    st.markdown("## 📦 Producto Terminado")

    # ---------------------------------------
    # AUTENTICACIÓN
    # ---------------------------------------
    if "auth_pt" not in st.session_state:
        st.session_state.auth_pt = False

    if not st.session_state.auth_pt:
        pwd = st.text_input("Ingrese contraseña del almacén:", type="password")
        if pwd == st.secrets["ALMACEN_PASSWORD"]:
            st.session_state.auth_pt = True
            st.rerun()
        elif pwd:
            st.error("❌ Contraseña incorrecta")
        st.stop()

    st.success("🔓 Acceso concedido")

    for col in ["recolectado", "empaque", "checklist", "cierre"]:
        if col in df.columns:
            df[col] = df[col].astype(bool).astype(int)

    # ---------------------------------------
    # INDICADORES RÁPIDOS
    # ---------------------------------------
    st.markdown("### 📊 Indicadores rápidos")

    total = len(df)
    recolectados = df["recolectado"].sum()
    empaques = df["empaque"].sum()
    checklists = df["checklist"].sum()
    cerrados = df["cierre"].sum()
    pendientes = total - cerrados

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric("Total", total)
    c2.metric("Recolectado", int(recolectados))
    c3.metric("Empaque", int(empaques))
    c4.metric("Checklist", int(checklists))
    c5.metric("Cerrado", int(cerrados))
    c6.metric("Pendiente", int(pendientes))
        
    # ---------------------------------------
    # COLUMNA VISUAL DE COLOR VERDE
    # ---------------------------------------
    def verde(x):
        return "🟩" if x else "⬜"

    df["R"] = df["recolectado"].apply(verde)
    df["E"] = df["empaque"].apply(verde)
    df["C"] = df["checklist"].apply(verde)
    df["F"] = df["cierre"].apply(verde)

    # ---------------------------------------
    # TABLA EDITABLE
    # ---------------------------------------
    st.markdown("### ✏️ Editar registros")

    COLUMNAS_TABLA = [
        "cuarto", "numero_parte", "numero_orden", "cantidad", "fecha_hora",
        "recolectado", "empaque", "checklist", "cierre", "notas"
    ]

    for col in COLUMNAS_TABLA:
        if col not in df.columns:
            if col in ["recolectado", "empaque", "checklist", "cierre"]:
                df[col] = False
            else:
                df[col] = ""

    df_editable = df[COLUMNAS_TABLA]

    df_original = df.copy()

    edited = st.data_editor(
        df_editable,
        hide_index=True,
        use_container_width=True,
        key="editor_almacen",
        column_config={
            "recolectado": st.column_config.CheckboxColumn("Recolectado"),
            "empaque": st.column_config.CheckboxColumn("Empaque"),
            "checklist": st.column_config.CheckboxColumn("Checklist"),
            "cierre": st.column_config.CheckboxColumn("Cierre"),
            "notas": st.column_config.TextColumn("Notas"),
        }
    )

    # Si no hay filas, salimos
    if df.empty:
        st.info("No hay registros para mostrar")
        st.stop()

    # Necesitamos row_id para guardar
    edited["row_id"] = df["row_id"]

    # Detectar cambios comparando contra el original (solo columnas editables)
    cols_editables = ["recolectado", "empaque", "checklist", "cierre", "notas"]

    # Asegurar que existan (por si alguna no vino en el df)
    for c in cols_editables:
        if c not in edited.columns:
            edited[c] = False if c in ["recolectado","empaque","checklist","cierre"] else ""
        if c not in df_original.columns:
            df_original[c] = False if c in ["recolectado","empaque","checklist","cierre"] else ""

    hubo_cambios = not edited[cols_editables].equals(df_original[cols_editables])

    if hubo_cambios:
        st.warning("⚠️ Se detectaron cambios. Guardando...")

        try:
            updates = []

            for i, row in edited.iterrows():
                original_row = df_original.iloc[i]

                # ¿Cambió esta fila?
                if not row[cols_editables].equals(original_row[cols_editables]):

                    update_row = smartsheet.models.Row()
                    update_row.id = int(row["row_id"])
                    update_row.cells = []

                    for col in cols_editables:
                        cell = smartsheet.models.Cell()
                        cell.column_id = COL_ID[col]
                        cell.value = row[col]
                        update_row.cells.append(cell)

                    updates.append(update_row)

            if updates:
                client.Sheets.update_rows(SHEET_ID, updates)

                # Refresh inteligente
                cargar_desde_smartsheet.clear()
                st.session_state.last_refresh = time.time()

                st.success("✅ Cambios guardados y actualizados")

                st.rerun()

        except Exception as e:
            st.error("❌ Error al guardar cambios")
            st.write(e)











