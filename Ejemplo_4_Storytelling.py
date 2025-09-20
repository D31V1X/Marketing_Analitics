# -*- coding: utf-8 -*-
"""
Created on Tue Sep  9 23:02:33 2025

@author: cesar
"""

import streamlit as st
import pandas as pd
import pynarrative as pn

# ------------------------------
# 1. Cargar datos desde Excel
# ------------------------------
EXCEL_FILE = "data_retail.xlsx"

@st.cache_data
def load_data():
    return pd.read_excel(EXCEL_FILE)

df = load_data()

# Validación de columnas mínimas
required_cols = {"Year", "Sales", "Customers"}
if not required_cols.issubset(df.columns):
    st.error(f"El archivo debe contener estas columnas: {required_cols}")
    st.stop()

# ------------------------------
# 2. Storytelling con múltiples vistas
# ------------------------------

# Vista 1: Línea de Ventas
story_sales = (
    pn.Story(df, width=600, height=400)
      .mark_line(color="steelblue", point=True)
      .encode(x="Year:O", y="Sales:Q")
      .add_title("Evolución de Ventas", "2018-2022", title_color="#2c3e50")
      .add_context("Las ventas cayeron en 2020 (pandemia)", position="top", color="red")
      .add_annotation(2020, df.loc[df["Year"] == 2020, "Sales"].values[0],
                      "Impacto COVID-19", arrow_direction="left", arrow_color="red")
      .add_context("Recuperación fuerte en 2021-2022", position="bottom", color="green")
      .add_source("Fuente: Datos reales de Retail")
      .render()
)

# Vista 2: Barras de Clientes
story_customers = (
    pn.Story(df, width=600, height=400)
      .mark_bar(color="orange")
      .encode(x="Year:O", y="Customers:Q")
      .add_title("Número de Clientes", "2018-2022", title_color="#8e44ad")
      .add_context("Caída de clientes en 2020", position="top", color="red")
      .add_annotation(2020, df.loc[df["Year"] == 2020, "Customers"].values[0],
                      "Clientes afectados", arrow_direction="up", arrow_color="red")
      .add_context("Crecimiento acelerado en 2021-2022", position="bottom", color="green")
      .add_source("Fuente: Datos reales de CRM")
      .render()
)

# ------------------------------
# 3. Streamlit UI
# ------------------------------
st.set_page_config(page_title="Storytelling con Datos Reales", layout="wide")

st.title("📊 Storytelling en Marketing Analytics")
st.markdown("Ejemplo con **datos reales de Excel** (`ventas_clientes.xlsx`).")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Ventas")
    st.altair_chart(story_sales, use_container_width=True)

with col2:
    st.subheader("Clientes")
    st.altair_chart(story_customers, use_container_width=True)





# cd  "C:\Users\Sala_\Downloads\rematerialdeclasemarketinganalytics"
# py -m streamlit run Ejemplo_4_Storytelling.py




















