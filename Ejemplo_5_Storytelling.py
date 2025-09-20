# -*- coding: utf-8 -*-
"""
Created on Tue Sep  9 23:50:53 2025

@author: cesar
"""



import plotly.express as px
import plotly.graph_objects as go

# Dataset de ejemplo
df = px.data.gapminder().query("year == 2007")

fig = px.scatter(df, x="gdpPercap", y="lifeExp", size="pop", color="continent",
                 hover_name="country", log_x=True, size_max=60,color_discrete_sequence=px.colors.qualitative.Dark24)

# Agregar anotación elegante
fig.add_annotation(
    x=30000, y=80,
    text="Países con alto PIB y esperanza de vida",
    showarrow=True,
    arrowhead=1,
    ax=-40,
    ay=-40,
    font=dict(size=14, color="blue"),
    bgcolor="white",
    bordercolor="blue",
    borderwidth=1
)

st.plotly_chart(fig, use_container_width=True)


import altair as alt
import pandas as pd
import streamlit as st
import plotly


df = pd.DataFrame({
    "x": [10, 20, 30],
    "y": [100, 200, 300],
    "label": ["Inicio", "Crecimiento", "Pico"]
})

chart = alt.Chart(df).mark_point(size=100).encode(
    x="x",
    y="y",
    tooltip=["label", "x", "y"]
)

text = alt.Chart(df).mark_text(
    align="left", dx=5, dy=-5, fontSize=14, color="blue"
).encode(
    x="x",
    y="y",
    text="label"
)

    
import streamlit as st
st.altair_chart((chart + text).interactive(), use_container_width=True)







# cd  "C:\Users\Sala_\Downloads\rematerialdeclasemarketinganalytics"
# py -m streamlit run Ejemplo_5_Storytelling.py





