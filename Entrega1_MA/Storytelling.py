# ==============================================
# Storytelling de Ventas y Rentabilidad (Superstore)
# ==============================================
import pandas as pd
import plotly.express as px
import streamlit as st

# ===========================
# 1. Título
# ===========================
st.title("📊 Storytelling Superstore – Ventas y Rentabilidad")

# ===========================
# 2. Selección de historia
# ===========================
opcion = st.radio(
    "Elige la historia que quieres visualizar:",
    ["📈 Panorama Ventas & Profit", "👥 Segmentación de Clientes", "🌎 Ventas por Región"]
)

# ===========================
# 3. Crear historias
# ===========================

if opcion == "📈 Panorama Ventas & Profit":
    cat_summary = df.groupby("Category")[["Sales", "Profit"]].sum().reset_index()
    df_melt = cat_summary.melt(id_vars="Category",
                               value_vars=["Sales", "Profit"],
                               var_name="Métrica", value_name="Valor")
    fig = px.bar(
        df_melt,
        x="Category", y="Valor", color="Métrica",
        barmode="group", text="Valor",
        title="Panorama de Ventas y Rentabilidad por Categoría"
    )
    fig.update_traces(texttemplate="%{text:.2s}", textposition="outside")
    fig.update_layout(yaxis=dict(tickformat=".2s"))
    st.plotly_chart(fig, use_container_width=True)

    st.info("💡 Insight: Algunas categorías venden mucho, pero generan pérdidas o márgenes bajos.")

elif opcion == "👥 Segmentación de Clientes":
    seg_summary = df.groupby("Segment")[["Sales", "Profit"]].sum().reset_index()

    col1, col2 = st.columns(2)

    with col1:
        fig_sales = px.pie(seg_summary, names="Segment", values="Sales", title="Ventas por Segmento")
        st.plotly_chart(fig_sales, use_container_width=True)

    with col2:
        fig_profit = px.pie(seg_summary, names="Segment", values="Profit", title="Rentabilidad por Segmento")
        st.plotly_chart(fig_profit, use_container_width=True)

    st.info("💡 Insight: El segmento dominante en ventas puede no ser el más rentable. Esto orienta campañas personalizadas.")

elif opcion == "🌎 Ventas por Región":
    # --- Línea: tiempo de entrega ---
    delivery_trend = (df.groupby("Order Date")["Delivery Days"]
                      .mean()
                      .reset_index())
    fig_line = px.line(delivery_trend, x="Order Date", y="Delivery Days",
                       title="Tiempo promedio de entrega (Order vs Ship Date)")
    fig_line.update_traces(mode="lines+markers")

    # --- Barras: ventas y profit por región ---
    region_summary = (df.groupby("Region")[["Sales", "Profit"]]
                      .sum()
                      .reset_index()
                      .sort_values("Sales", ascending=True))
    df_melt = region_summary.melt(id_vars="Region", value_vars=["Sales", "Profit"],
                                  var_name="Métrica", value_name="Valor")

    fig_bar = px.bar(df_melt, x="Valor", y="Region", color="Métrica",
                     orientation="h", barmode="group", text="Valor",
                     title="Ventas y Rentabilidad por Región")
    fig_bar.update_traces(texttemplate="%{text:.2s}", textposition="outside")
    fig_bar.update_layout(xaxis=dict(tickformat=".2s"))

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_line, use_container_width=True)
    with col2:
        st.plotly_chart(fig_bar, use_container_width=True)

    st.info("💡 Insight: Identifica las regiones con más ventas y aquellas con pérdidas. Esto guía la estrategia comercial regional.")
