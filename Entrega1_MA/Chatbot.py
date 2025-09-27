# app.py
import os, re, uuid
import pandas as pd
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import streamlit as st

# ------------------------------
# Configuración inicial
# ------------------------------
st.set_page_config(page_title="Chatbot PQR", page_icon="📨")
EXCEL_FILE_INTERACCIONES = "interacciones_chatbot.xlsx"
EXCEL_FILE_RADICADOS = "radicados_pqr.xlsx"

# Regex validaciones
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^[+\d][\d\s-]{6,}$")
DOC_RE = re.compile(r"^[A-Za-z0-9.-]{4,}$")
TIPOS_VALIDOS = {"p":"Petición","peticion":"Petición",
                 "q":"Queja","queja":"Queja",
                 "r":"Reclamo","reclamo":"Reclamo",
                 "s":"Sugerencia","sugerencia":"Sugerencia"}

def is_valid_email(x): return bool(EMAIL_RE.match(x or ""))
def is_valid_phone(x): return bool(PHONE_RE.match(x or ""))
def is_valid_doc(x): return bool(DOC_RE.match(x or ""))

# ------------------------------
# Persistencia
# ------------------------------
def save_interaction(user_msg, bot_response):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df_new = pd.DataFrame({"timestamp":[ts],"usuario":[user_msg],"bot":[bot_response]})
    if os.path.exists(EXCEL_FILE_INTERACCIONES):
        try:
            df_exist = pd.read_excel(EXCEL_FILE_INTERACCIONES)
            df_final = pd.concat([df_exist, df_new], ignore_index=True)
        except: df_final = df_new
    else: df_final = df_new
    df_final.to_excel(EXCEL_FILE_INTERACCIONES, index=False)

def save_radicado(form):
    rid = f"PQR-{datetime.now():%Y%m%d%H%M%S}-{str(uuid.uuid4())[:6].upper()}"
    row = {
        "radicado": rid, "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **form
    }
    df_new = pd.DataFrame([row])
    if os.path.exists(EXCEL_FILE_RADICADOS):
        try:
            df_exist = pd.read_excel(EXCEL_FILE_RADICADOS)
            df_final = pd.concat([df_exist, df_new], ignore_index=True)
        except: df_final = df_new
    else: df_final = df_new
    df_final.to_excel(EXCEL_FILE_RADICADOS, index=False)
    return rid

# ------------------------------
# FAQ mínima
# ------------------------------
FAQ_QA = [
    ("¿Qué es una PQR?","PQR significa Petición, Queja, Reclamo o Sugerencia."),
    ("¿Cómo radicar una PQR?","Te guiaré paso a paso con tus datos y descripción."),
    ("¿Cuánto tardan en responder?","Entre 15 y 30 días hábiles normalmente."),
]
_vec = TfidfVectorizer()
X = _vec.fit_transform([q for q,_ in FAQ_QA])
_nn = NearestNeighbors(n_neighbors=1, metric="cosine").fit(X)

def retrieve_faq(msg, th=0.35):
    if not msg.strip(): return None
    dist, idx = _nn.kneighbors(_vec.transform([msg]))
    sim = 1 - float(dist[0][0])
    return FAQ_QA[int(idx[0][0])][1] if sim >= th else None

# ------------------------------
# Estado inicial
# ------------------------------
if "chat" not in st.session_state:
    st.session_state.chat = []
if "state" not in st.session_state:
    st.session_state.state = {"step":"welcome","form":{}}

WELCOME = "¡Hola! Soy tu asistente de PQR.\nEscribe P, Q, R o S para empezar."

# ------------------------------
# Conversación
# ------------------------------
def handle_message(user_msg):
    state = st.session_state.state
    form = state["form"]
    step = state["step"]
    txt, low = (user_msg or ""), (user_msg or "").lower()

    faq = retrieve_faq(txt)
    bot = ""

    if low in {"reiniciar","reset","/reset"}:
        st.session_state.state = {"step":"welcome","form":{}}
        return "Reiniciado. " + WELCOME

    if step == "welcome":
        t = TIPOS_VALIDOS.get(low)
        if not t:
            return (faq + "\n\n" if faq else "") + "Indica el tipo: P,Q,R o S."
        form["tipo"] = t; state["step"] = "nombre"; bot = f"Tipo {t}. Tu nombre completo?"
    elif step == "nombre":
        form["nombre"] = txt; state["step"] = "documento"; bot = "Número de documento?"
    elif step == "documento":
        if not is_valid_doc(txt): bot = "Documento no válido. Ingresa de nuevo:"
        else: form["documento"]=txt; state["step"]="email"; bot="Correo electrónico?"
    elif step == "email":
        if not is_valid_email(txt): bot="Email inválido. Intenta otra vez:"
        else: form["email"]=txt; state["step"]="telefono"; bot="Teléfono de contacto?"
    elif step == "telefono":
        if not is_valid_phone(txt): bot="Teléfono inválido. Intenta de nuevo:"
        else: form["telefono"]=txt; state["step"]="departamento"; bot="Departamento?"
    elif step == "departamento":
        form["departamento"]=txt; state["step"]="municipio"; bot="Municipio?"
    elif step == "municipio":
        form["municipio"]=txt; state["step"]="canal"; bot="¿Prefieres respuesta por correo o teléfono?"
    elif step == "canal":
        form["canal"]=txt; state["step"]="descripcion"; bot="Describe tu caso brevemente."
    elif step == "descripcion":
        form["descripcion"]=txt; state["step"]="autorizo"; bot="¿Autorizas uso de datos (sí/no)?"
    elif step == "autorizo":
        form["autorizo"]=txt; state["step"]="confirmar"
        bot = f"Gracias. Confirma para radicar:\n{form}\nEscribe 'confirmar' o 'reiniciar'."
    elif step == "confirmar":
        if low.startswith("confirmar"):
            rid = save_radicado(form)
            st.session_state.state = {"step":"welcome","form":{}}
            bot = f"✅ Radicado generado: {rid}"
        else: bot = "Debes escribir 'confirmar' para finalizar o 'reiniciar'."
    else:
        bot = "No entendí."

    return bot

# ------------------------------
# Interfaz Streamlit
# ------------------------------
st.title("📨 Chatbot PQR")
st.write("Radica tu Petición, Queja, Reclamo o Sugerencia.")

if not st.session_state.chat:
    st.session_state.chat.append(("bot", WELCOME))

# Mostrar historial
for role, msg in st.session_state.chat:
    with st.chat_message(role):
        st.markdown(msg)

# Entrada de usuario
if prompt := st.chat_input("Escribe tu mensaje..."):
    st.session_state.chat.append(("user", prompt))
    bot_response = handle_message(prompt)
    st.session_state.chat.append(("bot", bot_response))
    save_interaction(prompt, bot_response)
    st.rerun()
