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

# ============================================================
# TAB 1 – REGISTRAR PRODUCTO TERMINADO
# ============================================================

with tab1:

    # Contenedor centrado (para que no se vea tan ancho)
    col_izq, col_centro, col_der = st.columns([1, 2, 1])

    with col_centro:

        st.header("Registrar Producto Terminado")

        # ----------------------------------------------------
        # Inicializar session_state (SOLO UNA VEZ)
        # ----------------------------------------------------
        if "form_cuarto" not in st.session_state:
            st.session_state.form_cuarto = lista_cuartos[0]

        if "form_numero_parte" not in st.session_state:
            st.session_state.form_numero_parte = ""

        if "form_numero_orden" not in st.session_state:
            st.session_state.form_numero_orden = ""

        if "form_cantidad" not in st.session_state:
            st.session_state.form_cantidad = 1

        if "msg_ok" not in st.session_state:
            st.session_state.msg_ok = False

        # ----------------------------------------------------
        # FORMULARIO
        # ----------------------------------------------------
        cuarto = st.selectbox(
            "Cuarto",
            lista_cuartos,
            key="form_cuarto"
        )

        numero_parte = st.text_input(
            "Número de Parte",
            key="form_numero_parte"
        )

        numero_orden = st.text_input(
            "Número de Orden",
            key="form_numero_orden"
        )

        cantidad = st.number_input(
            "Cantidad",
            min_value=1,
            step=1,
            key="form_cantidad"
        )

        # ----------------------------------------------------
        # BOTÓN GUARDAR
        # ----------------------------------------------------
        if st.button("Guardar Registro"):

            if not numero_parte or not numero_orden:
                st.error("❌ Número de parte y número de orden son obligatorios")

            else:
                try:
                    # -----------------------------
                    # GUARDAR EN SMARTSHEET
                    # -----------------------------
                    new_row = smartsheet.models.Row()
                    new_row.to_bottom = True

                    new_row.cells.append({
                        "column_id": COL_ID["cuarto"],
                        "value": cuarto
                    })
                    new_row.cells.append({
                        "column_id": COL_ID["numero_parte"],
                        "value": numero_parte
                    })
                    new_row.cells.append({
                        "column_id": COL_ID["numero_orden"],
                        "value": numero_orden
                    })
                    new_row.cells.append({
                        "column_id": COL_ID["cantidad"],
                        "value": cantidad
                    })
                    new_row.cells.append({
                        "column_id": COL_ID["fecha_hora"],
                        "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

                    client.Sheets.add_rows(SHEET_ID, [new_row])

                    st.session_state.msg_ok = True

                    # -----------------------------
                    # RESET SEGURO DEL FORMULARIO
                    # -----------------------------
                    for k in [
                        "form_cuarto",
                        "form_numero_parte",
                        "form_numero_orden",
                        "form_cantidad"
                    ]:
                        if k in st.session_state:
                            del st.session_state[k]

                    st.rerun()

                except Exception as e:
                    st.error("❌ Error al guardar en Smartsheet")
                    st.write(e)

        # ----------------------------------------------------
        # MENSAJE DE ÉXITO
        # ----------------------------------------------------
        if st.session_state.msg_ok:
            st.success("✅ Registro guardado correctamente")
            st.session_state.msg_ok = False
    
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





















