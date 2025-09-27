import os, re, uuid
from datetime import datetime
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ------------------------------
# Conexión a Google Sheets
# ------------------------------
# Crea un proyecto en Google Cloud, habilita la API de Google Sheets y descarga credenciales JSON.
# Guarda el archivo como `credentials.json` en el repo (NO lo subas público, usa secrets en Streamlit Cloud).

SCOPE = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
CREDS_FILE = "credentials.json"

@st.cache_resource
def get_gs_client():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
    return gspread.authorize(creds)

# IDs de Google Sheets (crear manualmente dos hojas vacías en tu Drive y pegar IDs)
SHEET_ID_INTERACCIONES = "<ID_DE_TU_HOJA_INTERACCIONES>"
SHEET_ID_RADICADOS = "<ID_DE_TU_HOJA_RADICADOS>"

def append_to_sheet(sheet_id, values):
    client = get_gs_client()
    sh = client.open_by_key(sheet_id)
    ws = sh.sheet1
    ws.append_row(values)

# ------------------------------
# Validaciones
# ------------------------------
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^[+\d][\d\s-]{6,}$")
DOC_RE = re.compile(r"^[A-Za-z0-9.-]{4,}$")
TIPOS_VALIDOS = {
    "p": "Petición", "peticion": "Petición",
    "q": "Queja", "queja": "Queja",
    "r": "Reclamo", "reclamo": "Reclamo",
    "s": "Sugerencia", "sugerencia": "Sugerencia"
}

def is_valid_email(x): return bool(EMAIL_RE.match(x or ""))
def is_valid_phone(x): return bool(PHONE_RE.match(x or ""))
def is_valid_doc(x): return bool(DOC_RE.match(x or ""))

# ------------------------------
# Persistencia en Google Sheets
# ------------------------------
def save_interaction(user_msg, bot_response):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    append_to_sheet(SHEET_ID_INTERACCIONES, [ts, user_msg, bot_response])

def save_radicado(form):
    rid = f"PQR-{datetime.now():%Y%m%d%H%M%S}-{str(uuid.uuid4())[:6].upper()}"
    row = [rid, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), form.get("tipo"), form.get("nombre"), form.get("documento"),
           form.get("email"), form.get("telefono"), form.get("departamento"), form.get("municipio"),
           form.get("canal"), form.get("descripcion"), form.get("autorizo")]
    append_to_sheet(SHEET_ID_RADICADOS, row)
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
_nn = NearestNeighbors(n_neighbors=1,metric="cosine").fit(X)

def retrieve_faq(msg,th=0.35):
    if not msg.strip(): return None
    dist,idx = _nn.kneighbors(_vec.transform([msg]))
    sim = 1-float(dist[0][0])
    return FAQ_QA[int(idx[0][0])][1] if sim>=th else None

# ------------------------------
# Conversación
# ------------------------------
INIT_STATE = {"step":"welcome","form":{}}
WELCOME = ("¡Hola! Soy tu asistente de PQR.\n" "Escribe P, Q, R o S para empezar.")

def build_summary(f):
    return (f"**Resumen**\nTipo:{f.get('tipo','-')} Nombre:{f.get('nombre','-')} Documento:{f.get('documento','-')}\n"
            f"Email:{f.get('email','-')} Tel:{f.get('telefono','-')} Dpto:{f.get('departamento','-')} Mun:{f.get('municipio','-')}\n"
            f"Canal:{f.get('canal','-')} Autorizo:{f.get('autorizo','-')} Descripción:{f.get('descripcion','-')}")

# ------------------------------
# Streamlit App
# ------------------------------
st.set_page_config(page_title="Chatbot PQR", page_icon="📨")
st.title("📨 Chatbot PQR")
st.write("Radica tu Petición, Queja, Reclamo o Sugerencia.")

if "state" not in st.session_state:
    st.session_state["state"] = INIT_STATE.copy()
    st.session_state["history"] = [("assistant", WELCOME)]

user_input = st.chat_input("Escribe tu mensaje...")
if user_input:
    state = st.session_state["state"]
    form = state.get("form",{})
    step = state.get("step")
    low = user_input.lower().strip()

    if low in {"reiniciar","reset","/reset"}:
        st.session_state["state"] = INIT_STATE.copy()
        st.session_state["history"] = [("assistant", WELCOME)]
        save_interaction(user_input, WELCOME)
    else:
        faq = retrieve_faq(user_input)
        bot = ""
        if step=="welcome":
            t=TIPOS_VALIDOS.get(low)
            if not t:
                bot=(f"{faq}\n\n" if faq else "")+"Indica el tipo: P,Q,R o S."
            else:
                form["tipo"]=t;state["step"]="nombre";bot=f"Tipo {t}. Tu nombre completo?"
        elif step=="nombre": form["nombre"]=user_input;state["step"]="documento";bot="Número de documento?"
        elif step=="documento":
            if not is_valid_doc(user_input): bot="Documento no válido. Ingresa de nuevo:";state["step"]="documento"
            else: form["documento"]=user_input;state["step"]="email";bot="Correo electrónico?"
        elif step=="email":
            if not is_valid_email(user_input): bot="Email inválido. Intenta otra vez:";state["step"]="email"
            else: form["email"]=user_input;state["step"]="telefono";bot="Teléfono de contacto?"
        elif step=="telefono":
            if not is_valid_phone(user_input): bot="Teléfono inválido. Intenta de nuevo:";state["step"]="telefono"
            else: form["telefono"]=user_input;state["step"]="departamento";bot="Departamento?"
        elif step=="departamento": form["departamento"]=user_input;state["step"]="municipio";bot="Municipio?"
        elif step=="municipio": form["municipio"]=user_input;state["step"]="canal";bot="¿Prefieres respuesta por correo o teléfono?"
        elif step=="canal": form["canal"]=user_input;state["step"]="descripcion";bot="Describe tu caso brevemente."
        elif step=="descripcion": form["descripcion"]=user_input;state["step"]="autorizo";bot="¿Autorizas uso de datos (sí/no)?"
        elif step=="autorizo":
            form["autorizo"]=user_input;state["step"]="confirmar";bot=f"Gracias. Confirma para radicar:\n{build_summary(form)}\nEscribe 'confirmar' o 'reiniciar'."
        elif step=="confirmar":
            if low.startswith("confirmar"):
                rid=save_radicado(form);bot=f"✅ Radicado generado: {rid}"
                st.session_state["state"]=INIT_STATE.copy()
            else: bot="Debes escribir 'confirmar' para finalizar o 'reiniciar'."
        else: bot="No entendí."

        save_interaction(user_input, bot)
        st.session_state["history"].append(("user", user_input))
        st.session_state["history"].append(("assistant", bot))
        st.session_state["state"]["form"]=form

for role, msg in st.session_state["history"]:
    with st.chat_message(role):
        st.markdown(msg)
