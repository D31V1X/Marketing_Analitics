# -*- coding: utf-8 -*-
"""
Created on Wed Sep 10 00:49:54 2025

@author: cesar
"""

import streamlit as st
import pandas as pd
import altair as alt

# ======================
# 1. Cargar archivo Excel
# ======================
st.title("📊 Storytelling Dashboard con Altair + Excel")

st.sidebar.header("Configuración")
uploaded_file = st.sidebar.file_uploader("📂 Sube tu archivo Excel", type=["xlsx", "xls"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.write("### Vista previa de los datos")
    st.dataframe(df.head())

    # ======================
    # 2. Seleccionar columnas
    # ======================
    st.sidebar.subheader("Selección de columnas")
    col_x = st.sidebar.selectbox("Columna para eje X", df.columns)
    col_y = st.sidebar.selectbox("Columna para eje Y", df.columns)

    # ======================
    # 3. Gráfico de Barras
    # ======================
    st.subheader("📊 Gráfico de Barras con anotación")
    bar_chart = alt.Chart(df).mark_bar(color="steelblue").encode(
        x=alt.X(f"{col_x}:O", title=col_x),
        y=alt.Y(f"{col_y}:Q", title=col_y),
        tooltip=[col_x, col_y]
    ).properties(width=600, height=400)

    # anotación automática: valor máximo
    max_row = df.loc[df[col_y].idxmax()]
    anot_bar = alt.Chart(pd.DataFrame({
        col_x: [max_row[col_x]],
        col_y: [max_row[col_y]],
        "label": ["Máximo valor"]
    })).mark_text(dy=-10, color="red").encode(x=f"{col_x}:O", y=f"{col_y}:Q", text="label")

    st.altair_chart(bar_chart + anot_bar, use_container_width=True)

    # ======================
    # 4. Gráfico de Sectores
    # ======================
    st.subheader("🥧 Gráfico de Sectores (Pie Chart)")
    pie_chart = alt.Chart(df).mark_arc().encode(
        theta=alt.Theta(f"{col_y}:Q", stack=True),
        color=alt.Color(f"{col_x}:N", legend=alt.Legend(title=col_x)),
        tooltip=[col_x, col_y]
    ).properties(width=400, height=400)

    st.altair_chart(pie_chart, use_container_width=True)

    # ======================
    # 5. Gráfico de Líneas
    # ======================
    st.subheader("📈 Serie de Tiempo con anotación")
    line_chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X(f"{col_x}:O", title=col_x),
        y=alt.Y(f"{col_y}:Q", title=col_y),
        tooltip=[col_x, col_y]
    ).properties(width=600, height=400)

    # anotación: primer y último punto
    start_point = alt.Chart(df.head(1)).mark_text(dy=-10, color="green").encode(
        x=f"{col_x}:O", y=f"{col_y}:Q", text=alt.value("Inicio")
    )
    end_point = alt.Chart(df.tail(1)).mark_text(dy=-10, color="blue").encode(
        x=f"{col_x}:O", y=f"{col_y}:Q", text=alt.value("Final")
    )

    st.altair_chart(line_chart + start_point + end_point, use_container_width=True)

    # ======================
    # 6. Gráfico de Dispersión
    # ======================
    st.subheader("🔀 Gráfico de Dispersión (X vs Y)")
    scatter_chart = alt.Chart(df).mark_circle(size=80).encode(
        x=alt.X(f"{col_x}:Q", title=col_x),
        y=alt.Y(f"{col_y}:Q", title=col_y),
        tooltip=[col_x, col_y],
        color=alt.Color(f"{col_x}:N")
    ).properties(width=600, height=400)

    st.altair_chart(scatter_chart, use_container_width=True)

else:
    st.info("📂 Sube un archivo Excel en la barra lateral para comenzar.")





# =======================================================================
# cd  "C:\Users\Sala_\Downloads\rematerialdeclasemarketinganalytics"
# py -m streamlit run Ejemplo_7_Storytelling.py



