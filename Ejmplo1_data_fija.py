import streamlit as st
import pandas as pd
import altair as alt
import openpyxl
import os  # Import necesario para manejar archivos locales

st.set_page_config(page_title="Storytelling Retail", layout="wide")

# ===========================
# 1. Cargar archivo
# ===========================
st.title("📊 Storytelling de Retail con PyNarrative")

uploaded_file = st.file_uploader("📂 Sube tu archivo Excel o CSV", type=["csv", "xlsx"])

# Si no se sube archivo, intentar usar data_retail.xlsx por defecto
if uploaded_file is None:
    default_file_path = "data_retail.xlsx"
    if os.path.exists(default_file_path):
        uploaded_file = open(default_file_path, "rb")
        st.info("📄 No se subió archivo. Usando archivo por defecto: `data_retail.xlsx`")
    else:
        st.warning("⚠️ No se ha subido un archivo y el archivo por defecto `data_retail.xlsx` no fue encontrado.")
        st.stop()

# Leer datos
if uploaded_file.name.endswith(".csv"):
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_excel(uploaded_file)

st.success("✅ Archivo cargado correctamente")
st.dataframe(df.head())

# ===========================
# 2. Selección de historia
# ===========================
opcion = st.radio(
    "Elige la historia que quieres visualizar:",
    ["📈 Ventas", "💰 Utilidades", "👥 Clientes"]
)

# ===========================
# 3. Crear historias
# ===========================
if "Year" not in df.columns:
    st.error("⚠️ Tu archivo debe tener una columna 'Year'.")
else:
    if opcion == "📈 Ventas":
        # Detectar subidas y caídas
        df["Sales_diff"] = df["Sales"].diff()
        df["Color"] = df["Sales_diff"].apply(lambda x: "green" if x > 0 else ("red" if x < 0 else "gray"))

        # Línea azul
        line = alt.Chart(df).mark_line(color="steelblue").encode(
            x=alt.X("Year:O", title="Año"),
            y=alt.Y("Sales:Q", title="Ventas")
        )

        # Puntos de colores
        points = alt.Chart(df).mark_point(size=80).encode(
            x="Year:O",
            y="Sales:Q",
            color=alt.Color("Color:N", legend=alt.Legend(title="Tendencia"))
        )

        # Combinar ambos
        chart = (line + points).properties(
            width=700,
            height=400,
            title={
                "text": "Tendencia de Ventas",
                "subtitle": ["Evolución anual"],
                "color": "#2c3e50"
            }
        )

        st.altair_chart(chart, use_container_width=True)
        st.markdown("**Las ventas reflejan el desempeño anual del retail**")

    elif opcion == "💰 Utilidades":
        chart = alt.Chart(df).mark_bar(color="orange").encode(
            x=alt.X("Year:O", title="Año"),
            y=alt.Y("Profit:Q", title="Utilidad")
        ).properties(
            width=700,
            height=400,
            title={
                "text": "Utilidad por Año",
                "subtitle": ["Margen de ganancia"],
                "color": "#8e44ad"
            }
        )

        st.altair_chart(chart, use_container_width=True)
        st.markdown("**Las utilidades están influenciadas por costos e inversión en campañas**")

    elif opcion == "👥 Clientes":
        chart = alt.Chart(df).mark_area(color="green", opacity=0.5).encode(
            x=alt.X("Year:O", title="Año"),
            y=alt.Y("Customers:Q", title="Clientes")
        ).properties(
            width=700,
            height=400,
            title={
                "text": "Evolución de Clientes",
                "subtitle": ["2018-2023"],
                "color": "#16a085"
            }
        )

        st.altair_chart(chart, use_container_width=True)
        st.markdown("**El número de clientes muestra fidelización y atracción de nuevos compradores**")
