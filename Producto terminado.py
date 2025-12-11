import streamlit as st
import smartsheet

TOKEN = RPRG2Wx6jeoVISCWo03UWnDBWbSSixedmbc5d
SHEET_ID = 3463316224561028 # Tu Sheet ID numérico correcto

client = smartsheet.Smartsheet(TOKEN)

st.title("Obtener Column IDs")

try:
    sheet = client.Sheets.get_sheet(SHEET_ID)

    st.write("### Column IDs encontrados:")
    for col in sheet.columns:
        st.write(f"**{col.title}** → {col.id}")

except Exception as e:
    st.error("Error al obtener columnas:")
    st.write(e)


