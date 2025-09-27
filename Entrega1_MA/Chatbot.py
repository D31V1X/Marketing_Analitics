#Chatbot
import os, re, uuid, importlib
from datetime import datetime

# ------------------------------
# Verificación de dependencias
# ------------------------------
DEPENDENCIAS = [
    ("gradio", "gradio"),
    ("pandas", "pandas"),
    ("openpyxl", "openpyxl"),
    ("sklearn", "scikit-learn"),
]
_missing = []
for mod, _pip in DEPENDENCIAS:
    try:
        importlib.import_module(mod)
    except Exception:
        _missing.append((mod, _pip))
if _missing:
    mods = ", ".join(m for m, _ in _missing)
    pips = " ".join(p for _, p in _missing)
    raise RuntimeError(
        f"Faltan dependencias: {mods}. Instálalas en Colab con: !pip install {pips}"
    )

# ------------------------------
# Imports confirmados
# ------------------------------
import gradio as gr
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

# ------------------------------
# Archivos Excel
# ------------------------------
EXCEL_FILE_INTERACCIONES = "interacciones_chatbot.xlsx"
EXCEL_FILE_RADICADOS = "radicados_pqr.xlsx"

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
# Persistencia
# ------------------------------
def save_interaction(user_msg, bot_response):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df_new = pd.DataFrame({"timestamp":[ts],"usuario":[user_msg],"bot":[bot_response]})
    if os.path.exists(EXCEL_FILE_INTERACCIONES):
        try:
            df_exist = pd.read_excel(EXCEL_FILE_INTERACCIONES)
            df_final = pd.concat([df_exist, df_new], ignore_index=True)
        except Exception: df_final = df_new
    else: df_final = df_new
    df_final.to_excel(EXCEL_FILE_INTERACCIONES,index=False)

def save_radicado(form):
    rid = f"PQR-{datetime.now():%Y%m%d%H%M%S}-{str(uuid.uuid4())[:6].upper()}"
    row = {
        "radicado": rid, "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipo": form.get("tipo"), "nombre": form.get("nombre"), "documento": form.get("documento"),
        "email": form.get("email"), "telefono": form.get("telefono"),
        "departamento": form.get("departamento"), "municipio": form.get("municipio"),
        "canal_respuesta": form.get("canal"), "descripcion": form.get("descripcion"),
        "autorizacion_datos": form.get("autorizo")
    }
    df_new = pd.DataFrame([row])
    if os.path.exists(EXCEL_FILE_RADICADOS):
        try:
            df_exist = pd.read_excel(EXCEL_FILE_RADICADOS)
            df_final = pd.concat([df_exist, df_new], ignore_index=True)
        except Exception: df_final = df_new
    else: df_final = df_new
    df_final.to_excel(EXCEL_FILE_RADICADOS,index=False)
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

def _fmt(u,b): return {"role":"user","content":u},{"role":"assistant","content":b}

def handle_message(user_msg,chat_history,state):
    txt,low=(user_msg or ""),(user_msg or "").lower()
    if not state: state=INIT_STATE.copy()
    if low in {"reiniciar","reset","/reset"}:
        bot="Reiniciado. "+WELCOME
        u,b=_fmt(txt,bot);chat_history+=[u,b];save_interaction(txt,bot)
        return chat_history,INIT_STATE.copy()
    step,form=state.get("step"),state.get("form",{})
    faq=retrieve_faq(txt)
    bot=""
    if step=="welcome":
        t=TIPOS_VALIDOS.get(low)
        if not t:
            bot=(f"{faq}\n\n" if faq else "")+"Indica el tipo: P,Q,R o S."
            u,b=_fmt(txt,bot);chat_history+=[u,b];save_interaction(txt,bot)
            return chat_history,state
        form["tipo"]=t;state["step"]="nombre";bot=f"Tipo {t}. Tu nombre completo?"
    elif step=="nombre": form["nombre"]=txt;state["step"]="documento";bot="Número de documento?"
    elif step=="documento":
        if not is_valid_doc(txt): bot="Documento no válido. Ingresa de nuevo:";state["step"]="documento"
        else: form["documento"]=txt;state["step"]="email";bot="Correo electrónico?"
    elif step=="email":
        if not is_valid_email(txt): bot="Email inválido. Intenta otra vez:";state["step"]="email"
        else: form["email"]=txt;state["step"]="telefono";bot="Teléfono de contacto?"
    elif step=="telefono":
        if not is_valid_phone(txt): bot="Teléfono inválido. Intenta de nuevo:";state["step"]="telefono"
        else: form["telefono"]=txt;state["step"]="departamento";bot="Departamento?"
    elif step=="departamento": form["departamento"]=txt;state["step"]="municipio";bot="Municipio?"
    elif step=="municipio": form["municipio"]=txt;state["step"]="canal";bot="¿Prefieres respuesta por correo o teléfono?"
    elif step=="canal": form["canal"]=txt;state["step"]="descripcion";bot="Describe tu caso brevemente."
    elif step=="descripcion": form["descripcion"]=txt;state["step"]="autorizo";bot="¿Autorizas uso de datos (sí/no)?"
    elif step=="autorizo":
        form["autorizo"]=txt;state["step"]="confirmar";bot=f"Gracias. Confirma para radicar:\n{build_summary(form)}\nEscribe 'confirmar' o 'reiniciar'."
    elif step=="confirmar":
        if low.startswith("confirmar"):
            rid=save_radicado(form);bot=f"✅ Radicado generado: {rid}"
            state=INIT_STATE.copy()
        else: bot="Debes escribir 'confirmar' para finalizar o 'reiniciar'."
    else: bot="No entendí."
    u,b=_fmt(user_msg,bot);chat_history+=[u,b];save_interaction(user_msg,bot);state["form"]=form
    return chat_history,state

# ------------------------------
# UI Gradio
# ------------------------------
with gr.Blocks(title="Chatbot PQR") as demo:
    gr.Markdown("""# 📨 Chatbot PQR\nRadica tu Petición, Queja, Reclamo o Sugerencia.\nArchivos: interacciones_chatbot.xlsx y radicados_pqr.xlsx""")
    state=gr.State(INIT_STATE.copy())
    chat=gr.Chatbot(type="messages")
    msg=gr.Textbox(label="Tu mensaje")
    clear_btn=gr.Button("Reiniciar")
    def _init():
        hist=[];bot=WELCOME;u,b=_fmt("/init",bot);hist+=[u,b];save_interaction("/init",bot)
        return hist,INIT_STATE.copy()
    demo.load(_init,outputs=[chat,state])
    msg.submit(handle_message,inputs=[msg,chat,state],outputs=[chat,state])
    def _clear():
        hist=[];bot="Reiniciado. "+WELCOME;u,b=_fmt("/reset",bot);hist+=[u,b];save_interaction("/reset",bot)
        return hist,INIT_STATE.copy()
    clear_btn.click(_clear,outputs=[chat,state])

demo.launch(share=True)
