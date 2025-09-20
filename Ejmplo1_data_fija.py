import streamlit as st
import pandas as pd
import pynarrative as pn
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

        # Historia con línea + puntos
        story = (
            pn.Story(df, width=700, height=400)
              .layer(
                  pn.Layer()  # Línea azul
                    .mark_line(color="steelblue")
                    .encode(x="Year:O", y="Sales:Q"),
                  pn.Layer()  # Puntos coloreados
                    .mark_point(size=80)
                    .encode(x="Year:O", y="Sales:Q", color="Color:N")
              )
              .add_title("Tendencia de Ventas", "Evolución anual", title_color="#2c3e50")
              .add_context("Las ventas reflejan el desempeño anual del retail", position="top")
        )

    elif opcion == "💰 Utilidades":
        story = (
            pn.Story(df, width=700, height=400)
              .mark_bar(color="orange")
              .encode(x="Year:O", y="Profit:Q")
              .add_title("Utilidad por Año", "Margen de ganancia", title_color="#8e44ad")
              .add_context("Las utilidades están influenciadas por costos e inversión en campañas", position="top")
        )

    elif opcion == "👥 Clientes":
        story = (
            pn.Story(df, width=700, height=400)
              .mark_area(color="green", opacity=0.5)
              .encode(x="Year:O", y="Customers:Q")
              .add_title("Evolución de Clientes", "2018-2023", title_color="#16a085")
              .add_context("El número de clientes muestra fidelización y atracción de nuevos compradores", position="top")
        )

    # ===========================
    # 4. Renderizar historia
    # ===========================
    st.altair_chart(story.render(), use_container_width=True)
