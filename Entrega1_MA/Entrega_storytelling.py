# ==============================================
# Storytelling de Ventas y Rentabilidad (Superstore)
# ==============================================
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st


url = "Entrega1_MA/superstore_base.csv"
df = pd.read_csv(url, encoding="latin1", sep=";", engine="python")

#df = pd.read_csv("/content/superstore.csv", encoding="latin1", sep=";", engine="python")
# Asegurarse de que las fechas estén en formato datetime
df["Order Date"] = pd.to_datetime(df["Order Date"])
df["Ship Date"] = pd.to_datetime(df["Ship Date"])

# Crear la columna Delivery Days (diferencia en días)
df["Delivery Days"] = (df["Ship Date"] - df["Order Date"]).dt.days
# Crear la columna Year (diferencia en días)
df["Year"] = df["Order Date"].dt.year


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
# 3. Crear historias (basadas en los 3 slides previos)
# ===========================

# ---------------------------
# SLIDE 1 – Panorama Ventas y Profit
# ---------------------------
if opcion == "📈 Panorama Ventas & Profit":
    cat_summary = df.groupby("Category")[["Sales", "Profit"]].sum().reset_index()

    df_melt = cat_summary.melt(
        id_vars="Category",
        value_vars=["Sales", "Profit"],
        var_name="Métrica",
        value_name="Valor"
    )

    fig1 = px.bar(
        df_melt,
        x="Category",
        y="Valor",
        color="Métrica",
        barmode="group",
        text="Valor",
        title="Panorama de Ventas y Rentabilidad por Categoría"
    )
    fig1.update_traces(
        texttemplate="%{text:.2s}",
        textposition="outside",
        marker=dict(line=dict(width=1, color="black"))
    )
    fig1.update_layout(
        yaxis_title="Monto (USD)",
        xaxis_title="Categoría",
        uniformtext_minsize=10,
        uniformtext_mode="hide",
        legend_title_text="Métrica",
        yaxis=dict(tickformat=".2s")
    )

    st.plotly_chart(fig1, use_container_width=True)
    st.info("Indicador: La categoría tecnología, tiene ventas inferiores a muebles en un 46%  pero el profit (Beneficio) de tecnologia es 15 veces superior al de muebles")

# ---------------------------
# SLIDE 2 – Segmentación de Clientes
# ---------------------------
elif opcion == "👥 Segmentación de Clientes":
    seg_summary = df.groupby("Segment")[["Sales", "Profit"]].sum().reset_index()

    fig2 = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "domain"}, {"type": "domain"}]],
        subplot_titles=("Ventas por Segmento", "Rentabilidad por Segmento")
    )

    fig_sales = px.pie(seg_summary, names="Segment", values="Sales")
    for trace in fig_sales.data:
        fig2.add_trace(trace, row=1, col=1)

    fig_profit = px.pie(seg_summary, names="Segment", values="Profit")
    for trace in fig_profit.data:
        fig2.add_trace(trace, row=1, col=2)

    fig2.update_layout(
        title_text="Segmentación de Clientes",
        width=1000,
        height=500
    )

    st.plotly_chart(fig2, use_container_width=True)
    st.info("""1. El segmento Consumer domina tanto en ventas como en rentabilidad

Representa 53.3% de las ventas y 50.7% de la rentabilidad.

Esto confirma que el cliente final (Consumer) es el principal motor del negocio, no solo por volumen, sino también por su aporte directo a las utilidades.

Estrategia: reforzar campañas de fidelización y ofertas dirigidas a este segmento puede maximizar el retorno.

2. Home Office es el segmento con mayor brecha positiva en rentabilidad

En ventas aporta 17.4%, pero en rentabilidad sube a 21%.

Esto indica que, aunque su volumen de compra es más pequeño, sus márgenes son más altos.

Estrategia: vale la pena potenciar este nicho con soluciones especializadas, ya que genera un impacto proporcionalmente mayor en la utilidad.

3. Corporate es menos rentable en proporción a sus ventas

Aporta 29.3% de las ventas, pero solo 28.3% en rentabilidad.

Esto refleja que el segmento corporativo requiere descuentos o tiene menores márgenes.

Estrategia: revisar políticas comerciales, condiciones de crédito y costos asociados para mejorar la rentabilidad de este segmento sin perder volumen.""")

# ---------------------------
# SLIDE 3 – Ventas por Región
# ---------------------------

# --- Columna Year para el filtro ---
elif opcion == "🌎 Ventas por Región":
    # --- Filtro por año ---
    years = df["Year"].unique()
    selected_year = st.selectbox("Selecciona un año", sorted(years))

    # Filtrar por el año elegido
    df_year = df[df["Year"] == selected_year]

    # --- Línea: tiempo de entrega ---
    delivery_trend = (df_year.groupby("Order Date")["Delivery Days"]
                      .mean()
                      .reset_index())

    fig_line = px.line(
        delivery_trend,
        x="Order Date",
        y="Delivery Days",
        title=f"Tiempo promedio de entrega ({selected_year})"
    )
    fig_line.update_traces(mode="lines+markers")

    # --- Barras: ventas y profit por región ---
    region_summary = (df_year.groupby("Region")[["Sales", "Profit"]]
                      .sum()
                      .reset_index()
                      .sort_values("Sales", ascending=True))

    df_melt = region_summary.melt(
        id_vars="Region",
        value_vars=["Sales", "Profit"],
        var_name="Métrica",
        value_name="Valor"
    )

    fig_bar = px.bar(
        df_melt,
        x="Valor",
        y="Region",
        color="Métrica",
        orientation="h",
        barmode="group",
        text="Valor",
        title=f"Ventas y Rentabilidad por Región ({selected_year})"
    )
    fig_bar.update_traces(
        texttemplate="%{text:.2s}",
        textposition="outside",
        marker=dict(line=dict(width=1, color="black"))
    )
    fig_bar.update_layout(
        xaxis_title="Monto (USD)",
        yaxis_title="Región",
        uniformtext_minsize=10,
        uniformtext_mode="hide",
        legend_title_text="Métrica",
        xaxis=dict(tickformat=".2s")
    )

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_line, use_container_width=True)
    with col2:
        st.plotly_chart(fig_bar, use_container_width=True)

    st.info("💡 Insight: El Oeste concentra las mayores ventas, mientras que algunas regiones presentan pérdidas o bajo desempeño. Esto orienta estrategias regionales.")
