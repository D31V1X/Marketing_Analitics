# storytelling_app.py
# ======================================
# Mini demo de Storytelling con Streamlit
# ======================================

import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import tempfile, os

st.set_page_config(page_title="📊 Storytelling Demo", layout="wide")

# ======================
# 1. Dashboard interactivo con Plotly
# ======================
st.header("📈 Dashboard Interactivo")

df = pd.DataFrame({
    "Mes": ["Ene", "Feb", "Mar", "Abr", "May"],
    "Ventas": [120, 150, 180, 130, 200]
})

fig = px.line(df, x="Mes", y="Ventas", title="Evolución de Ventas", markers=True)
st.plotly_chart(fig, use_container_width=True)

# ======================
# 2. Infografía narrativa con Seaborn
# ======================
st.header("🖼️ Infografía Narrativa")

data = {"Segmento": ["Jóvenes", "Adultos", "Mayores"],
        "Compras": [300, 500, 200]}
sns.set(style="whitegrid")
fig2, ax = plt.subplots()
sns.barplot(x=data["Segmento"], y=data["Compras"], ax=ax, palette="viridis")
ax.set_title("Compras por Segmento")
st.pyplot(fig2)

# ======================
# 3. Video corto con Matplotlib Animation
# ======================
st.header("🎥 Video Corto con Insights")

ventas = [100, 150, 180, 220, 260]
meses = ["Ene", "Feb", "Mar", "Abr", "May"]

fig3, ax3 = plt.subplots()
line, = ax3.plot([], [], 'r-o')
ax3.set_xlim(0, len(meses)-1)
ax3.set_ylim(0, max(ventas)+50)
ax3.set_xticks(range(len(meses)))
ax3.set_xticklabels(meses)

def init():
    line.set_data([], [])
    return line,

def update(frame):
    line.set_data(range(frame+1), ventas[:frame+1])
    return line,

ani = animation.FuncAnimation(fig3, update, frames=len(ventas), init_func=init, blit=True)

# Guardar animación como video temporal
tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
ani.save(tmpfile.name, writer="ffmpeg")

st.video(tmpfile.name)

# ======================
# Footer
# ======================
st.markdown("---")
st.markdown("✅ Demo de Storytelling en Marketing Analytics con Python + Streamlit")
