import streamlit as st
import smartsheet
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(page_title="Registro de Producto Terminado", layout="wide")

ALMACEN_PASSWORD = st.secrets["ALMACEN_PASSWORD"]

# ============================================================
# CONSTANTES SMARTSHEET
# ============================================================
SHEET_ID = 3463316224561028

COL_ID = {
    "cuarto": 4253122231488388,
    "numero_parte": 8756721858858884,
    "numero_orden": 171735069183876,
    "cantidad": 4675334696554372,
    "fecha_hora": 5596968911589252,
    "recolectado": 3345169097904004,
    "empaque": 7848768725274500,
    "checklist": 2219269191061380,
    "cierre": 6722868818431876,
    "notas": 4471069004746628,
}

# ============================================================
# FUNCIÓN → CARGAR DATOS DESDE SMARTSHEET
# ============================================================

def cargar_desde_smartsheet():
    try:
        client = smartsheet.Smartsheet(st.secrets["SMARTSHEET_TOKEN"])
        response = client.Sheets.get_sheet(SHEET_ID)
        sheet = response 
        
        rows_data = []

        for row in sheet.rows:
            data = {"row_id": row.id}

            for cell in row.cells:
                cid = cell.column_id
                val = cell.value

                for key, col_id in COL_ID.items():
                    if cid == col_id:
                        data[key] = val

            rows_data.append(data)

        df = pd.DataFrame(rows_data).fillna("")
        return df

    except Exception as e:
        st.error(f"❌ Error cargando Smartsheet: {e}")
        st.stop()

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

# ============================================================
# TABS
# ============================================================

tab1, tab2 = st.tabs(["➕ Registrar Orden", "📦 Almacén"])

# ===========================
# TAB 1 – Registrar Producto
# ===========================

with tab1:

    # contenedor centrado para que Tab1 no se vea tan ancho
    col_izq, col_centro, col_der = st.columns([1, 2, 1])

        # aquí va TODO lo que ya tenías del formulario:
        # selects, text_input, number_input, botón, etc.

    # contenedor centrado para que Tab1 no se vea tan ancho
    col_izq, col_centro, col_der = st.columns([1, 2, 1])

    st.header("Registrar Producto Terminado")

    # Inicializar session_state
    if "cuarto" not in st.session_state:
        st.session_state.cuarto = ""
        st.session_state.numero_parte = ""
        st.session_state.numero_orden = ""
        st.session_state.cantidad = 1

    if "msg_ok" not in st.session_state:
        st.session_state.msg_ok = False


    # ------------------------------
    # FORMULARIO
    # ------------------------------
    lista_cuartos = [
        "INTRODUCER","PU1","PU2","PU3","PU4","PVC1","PVC2","PVC3A","PVC3B",
        "PVC6","PVC7","PVC8","PVC9","PVCS","PAK1","MGLY","MASM1","MMCL",
        "MM MOLD","MMFP","RESORTES"
    ]

    col1, col2 = st.columns(2)

    with col1:
        st.selectbox("Cuarto", lista_cuartos, key="cuarto")
        st.text_input("Número de Parte", key="numero_parte")

    with col2:
        st.text_input("Número de Orden", key="numero_orden")
        st.number_input("Cantidad", min_value=1, step=1, key="cantidad")


    # ------------------------------
    # MENSAJE DE ÉXITO
    # ------------------------------
    if st.session_state.msg_ok:
        st.success("✔ Registro enviado correctamente.")
        st.session_state.msg_ok = False

    # ------------------------------
    # BOTÓN GUARDAR
    # ------------------------------
    if st.button("Guardar Registro"):

        # Obtener hora local UTC-7
        hora_local = datetime.utcnow() - timedelta(hours=7)

        # Crear nuevo registro
        nueva_fila = {
            "cuarto": st.session_state.cuarto,
            "numero_parte": st.session_state.numero_parte,
            "numero_orden": st.session_state.numero_orden,
            "cantidad": st.session_state.cantidad,
            "fecha_hora": hora_local.strftime("%Y-%m-%d %H:%M:%S"),
            "recolectado": False,
            "empaque": False,
            "checklist": False,
            "cierre": False,
            "notas": "",
        }

        # Enviar a Smartsheet
        try:
            client = smartsheet.Smartsheet(st.secrets["SMARTSHEET_TOKEN"])

            new_row = smartsheet.models.Row()
            new_row.to_top = True

            # Función para agregar celdas
            def add(col, val):
                cell = smartsheet.models.Cell()
                cell.column_id = COL_ID[col]
                cell.value = val
                new_row.cells.append(cell)

            # Crear celdas
            for campo, valor in nueva_fila.items():
                add(campo, valor)

            # Enviar fila
            client.Sheets.add_rows(SHEET_ID, [new_row])

            # Limpiar formulario
            st.session_state.cuarto = ""
            st.session_state.numero_parte = ""
            st.session_state.numero_orden = ""
            st.session_state.cantidad = 1

            st.session_state.msg_ok = True
            st.rerun()

        except Exception as e:
            st.error("❌ Error al guardar en Smartsheet.")
            st.write(e)
    
# ============================================================
# TAB 2 — PANEL DE ALMACÉN
# ============================================================

with tab2:

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

    # ---------------------------------------
    # CARGAR DATOS DE SMARTSHEET
    # ---------------------------------------
    client = smartsheet.Smartsheet(st.secrets["SMARTSHEET_TOKEN"])
    sheet = client.Sheets.get_sheet(SHEET_ID)

    rows = []
    for row in sheet.rows:
        data = {"row_id": row.id}

        for cell in row.cells:
            cid = cell.column_id
            val = cell.value

            # Detectar a qué columna pertenece
            for k, v in COL_ID.items():
                if cid == v:
                    data[k] = val

        rows.append(data)

    df = pd.DataFrame(rows).fillna("")

    # Asegurar tipos booleanos correctos
    for col in ["recolectado", "empaque", "checklist", "cierre"]:
        df[col] = df[col].apply(lambda x: True if x is True else False)
        
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

    df_editable = df[[
        "cuarto", "numero_parte", "numero_orden", "cantidad", "fecha_hora",
        "recolectado", "empaque", "checklist", "cierre", "notas"
    ]]

    edited = st.data_editor(
        df_editable,
        hide_index=True,
        use_container_width=True,
        column_config={
            "recolectado": st.column_config.CheckboxColumn("Recolectado"),
            "empaque": st.column_config.CheckboxColumn("Empaque"),
            "checklist": st.column_config.CheckboxColumn("Checklist"),
            "cierre": st.column_config.CheckboxColumn("Cierre"),
            "notas": st.column_config.TextColumn("Notas"),
        }
    )

    edited["row_id"] = df["row_id"]

    # ---------------------------------------
    # DETECTAR CAMBIOS
    # ---------------------------------------
    cambios = edited.merge(df, indicator=True, how="outer")
    cambios = cambios[cambios["_merge"] != "both"]

    if not cambios.empty:
        st.warning("⚠ Se detectaron cambios. Guardando...")

        try:
            updates = []

            for idx, row in edited.iterrows():
                original = df[df["row_id"] == row["row_id"]].iloc[0]

                # checkboxes
                cambios_checkbox = {
                    "recolectado": row["recolectado"],
                    "empaque": row["empaque"],
                    "checklist": row["checklist"],
                    "cierre": row["cierre"],
                }

                # notas
                cambios_notas = row["notas"]

                update_row = smartsheet.models.Row()
                update_row.id = int(row["row_id"])
                update_row.cells = []

                for col, val in cambios_checkbox.items():
                    cell = smartsheet.models.Cell()
                    cell.column_id = COL_ID[col]
                    cell.value = val
                    update_row.cells.append(cell)

                cell = smartsheet.models.Cell()
                cell.column_id = COL_ID["notas"]
                cell.value = cambios_notas
                update_row.cells.append(cell)

                updates.append(update_row)

            client.Sheets.update_rows(SHEET_ID, updates)
            st.success("✔ Cambios guardados correctamente")
            st.rerun()

        except Exception as e:
            st.error("❌ Error al guardar los cambios")
            st.write(e)
















