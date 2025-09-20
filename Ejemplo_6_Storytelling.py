# -*- coding: utf-8 -*-
"""
Created on Wed Sep 10 00:36:38 2025

@author: cesar
"""

# ===================================================================
import streamlit as st
import pandas as pd
import altair as alt

# ==========================
# 1. Dataset de ejemplo
# ==========================
df = pd.DataFrame({
    "Year": [2018, 2019, 2020, 2021, 2022],
    "Sales": [120, 150, 90, 180, 220]
})

# ==========================
# 2. Gráfico base
# ==========================
chart = alt.Chart(df).mark_line(point=True, color="steelblue").encode(
    x=alt.X("Year:O", title="Año"),
    y=alt.Y("Sales:Q", title="Ventas"),
    tooltip=["Year", "Sales"]
).properties(
    width=600, height=400, title="Tendencia de Ventas 2018-2022"
)

# ==========================
# 3. Anotaciones elegantes
# ==========================
# Caída en 2020
anotacion1 = alt.Chart(pd.DataFrame({
    "Year": [2020],
    "Sales": [90],
    "label": ["Caída por pandemia"]
})).mark_text(
    align="left",
    dx=10, dy=-10,
    fontSize=12,
    color="red"
).encode(
    x="Year:O", y="Sales:Q", text="label"
)

# Flecha hacia 2020
flecha1 = alt.Chart(pd.DataFrame({
    "Year": [2020],
    "Sales": [90]
})).mark_point(
    shape="triangle-down", size=200, color="red"
).encode(x="Year:O", y="Sales:Q")

# Recuperación en 2021-2022
anotacion2 = alt.Chart(pd.DataFrame({
    "Year": [2022],
    "Sales": [220],
    "label": ["Crecimiento post-pandemia"]
})).mark_text(
    align="right",
    dx=-10, dy=-10,
    fontSize=12,
    color="green"
).encode(
    x="Year:O", y="Sales:Q", text="label"
)

# ==========================
# 4. Mostrar en Streamlit
# ==========================
st.title("📊 Storytelling con Altair + Streamlit")
st.write("Ejemplo de cómo contar historias con datos usando **anotaciones elegantes**.")

st.altair_chart(chart + anotacion1 + flecha1 + anotacion2, use_container_width=True)


# =======================================================================
# cd  "C:\Users\Sala_\Downloads\rematerialdeclasemarketinganalytics"
# py -m streamlit run Ejemplo_6_Storytelling.py



