# -*- coding: utf-8 -*-
"""
Created on Wed Sep 10 01:00:58 2025

@author: cesar
"""

import streamlit as st
import pandas as pd
import altair as alt

# ======================
# 1. Configuración inicial
# ======================
st.set_page_config(page_title="📊 Storytelling Dashboard", layout="wide")

st.title("📊 Storytelling Dashboard con Altair + Excel")
st.markdown("Sube tu archivo de Excel y genera gráficos interactivos con anotaciones.")

# ======================
# 2. Cargar archivo Excel
# ======================
uploaded_file = st.sidebar.file_uploader("📂 Sube tu archivo Excel", type=["xlsx", "xls"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.write("### Vista previa de los datos")
    st.dataframe(df.head())

    # ======================
    # 3. Selección de columnas
    # ======================
    st.sidebar.header("⚙️ Configuración de columnas")
    col_x = st.sidebar.selectbox("Columna para eje X", df.columns)
    col_y = st.sidebar.selectbox("Columna para eje Y", df.columns)

    # Si hay columnas categóricas, permitir filtrarlas
    cat_cols = df.select_dtypes(include=["object"]).columns.tolist()
    num_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    date_cols = df.select_dtypes(include=["datetime64[ns]"]).columns.tolist()

    # ======================
    # 4. Filtros interactivos
    # ======================
    st.sidebar.header("🔍 Filtros")

    # Filtro por categoría
    if cat_cols:
        cat_filter = st.sidebar.selectbox("Filtrar por categoría", ["Ninguno"] + cat_cols)
        if cat_filter != "Ninguno":
            options = df[cat_filter].unique().tolist()
            selected_opts = st.sidebar.multiselect(f"Selecciona {cat_filter}", options, default=options[:3])
            df = df[df[cat_filter].isin(selected_opts)]

    # Filtro por fecha
    if date_cols:
        date_filter = st.sidebar.selectbox("Columna de fecha", ["Ninguno"] + date_cols)
        if date_filter != "Ninguno":
            min_date, max_date = df[date_filter].min(), df[date_filter].max()
            start, end = st.sidebar.date_input("Rango de fechas", [min_date, max_date])
            df = df[(df[date_filter] >= pd.to_datetime(start)) & (df[date_filter] <= pd.to_datetime(end))]

    # Top N
    top_n = st.sidebar.slider("Top N registros (por Y)", min_value=5, max_value=50, value=10)
    df = df.sort_values(by=col_y, ascending=False).head(top_n)

    # ======================
    # 5. Paleta de colores
    # ======================
    color_scheme = st.sidebar.selectbox("🎨 Paleta de colores", ["category10", "tableau10", "dark2", "set1"])

    # ======================
    # 6. Gráficos con storytelling
    # ======================
    st.subheader("📊 Gráfico de Barras")
    bar_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X(f"{col_x}:O", sort="-y"),
        y=alt.Y(f"{col_y}:Q"),
        color=alt.Color(f"{col_x}:N", scale=alt.Scale(scheme=color_scheme)),
        tooltip=[col_x, col_y]
    ).properties(width=600, height=400)

    # anotación máximo
    max_row = df.loc[df[col_y].idxmax()]
    anot_bar = alt.Chart(pd.DataFrame({
        col_x: [max_row[col_x]],
        col_y: [max_row[col_y]],
        "label": ["⬆ Máximo"]
    })).mark_text(dy=-10, color="red", fontWeight="bold").encode(
        x=f"{col_x}:O", y=f"{col_y}:Q", text="label"
    )

    st.altair_chart(bar_chart + anot_bar, use_container_width=True)

    # ======================
    st.subheader("🥧 Gráfico de Sectores (Pie)")
    pie_chart = alt.Chart(df).mark_arc().encode(
        theta=alt.Theta(f"{col_y}:Q"),
        color=alt.Color(f"{col_x}:N", scale=alt.Scale(scheme=color_scheme)),
        tooltip=[col_x, col_y]
    ).properties(width=400, height=400)
    st.altair_chart(pie_chart, use_container_width=True)

    # ======================
    st.subheader("📈 Gráfico de Líneas (Time series)")
    line_chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X(f"{col_x}:O"),
        y=alt.Y(f"{col_y}:Q", scale=alt.Scale(zero=False)),
        tooltip=[col_x, col_y],
        color=alt.value("steelblue")
    ).properties(width=600, height=400)

    # Anotar mínimo y máximo
    min_row = df.loc[df[col_y].idxmin()]
    end_row = df.loc[df[col_y].idxmax()]
    anot_line = alt.Chart(pd.DataFrame({
        col_x: [min_row[col_x], end_row[col_x]],
        col_y: [min_row[col_y], end_row[col_y]],
        "label": ["⬇ Mínimo", "⬆ Máximo"]
    })).mark_text(dy=-10, color="red").encode(
        x=f"{col_x}:O", y=f"{col_y}:Q", text="label"
    )

    st.altair_chart(line_chart + anot_line, use_container_width=True)

    # ======================
    st.subheader("🔀 Gráfico de Dispersión (X vs Y)")
    scatter_chart = alt.Chart(df).mark_circle(size=80).encode(
        x=alt.X(f"{col_x}:Q", scale=alt.Scale(zero=False)),
        y=alt.Y(f"{col_y}:Q", scale=alt.Scale(zero=False)),
        tooltip=[col_x, col_y],
        color=alt.Color(f"{col_x}:N", scale=alt.Scale(scheme=color_scheme))
    ).properties(width=600, height=400)

    st.altair_chart(scatter_chart, use_container_width=True)

else:
    st.info("📂 Sube un archivo Excel en la barra lateral para comenzar.")



# =======================================================================
# cd  "C:\Users\Sala_\Downloads\rematerialdeclasemarketinganalytics"
# py -m streamlit run Ejemplo_8_Storytelling.py