import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai

# --- CONFIGURATION ---
st.set_page_config(page_title="Veille Stratégique Pyxis", page_icon="⚖️", layout="wide")

# --- CLE API GEMINI ---
API_KEY = st.secrets["API_KEY"] if "API_KEY" in st.secrets else "VOTRE_CLE_ICI"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- INITIALISATION DES SUJETS (DIVISIONS) ---
if 'mes_sujets' not in st.session_state:
    st.session_state['mes_sujets'] = [
        "Mobilités (Ferroviaire & Aéroportuaire)",
        "Externalisation (Marchés Publics & AMO)",
        "IT & Systèmes d'Information",
        "Digitalisation & IA",
        "Vente SaaS & Commerciaux MA-IA",
        "Développement Software",
        "Administration, RH & DAF"
    ]

# --- DESIGN HAUT CONTRASTE ---
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF; }
        .main-title { text-align: center; color: #000000; font-weight: 800; font-size: 2.5em; margin-bottom: 20px; }
        .article-card {
            background-color: #ffffff; padding: 20px; border: 1px solid #EEE;
            border-top: 5px solid #C5A059; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px;
        }
        h1, h2, h3, p, span, label { color: #000000 !important; }
        div.stButton > button { background-color: #000 !important; color: #fff !important; font-weight: bold; width: 100%; }
    </style>
""", unsafe_allow_html=True)

# --- LOGIQUE IA AVEC CONTEXTE PYXIS ---
def analyser_ia(sujet, articles):
    if not articles: return "Aucun article trouvé."
    txt = "\n".join([f"- {a['title']} (Source: {a['source']})" for a in articles])
    prompt = f"""
    Tu es l'expert stratégique de Pyxis Support (AMO Marchés Publics, IT, Mobilités).
    Sujet : {sujet}
    TACHE : Sélectionne les 4 articles les plus critiques pour le cabinet.
    FILTRE : Rejette le Canada, le Québec et les marchés physiques (alimentaire).
    RÉPONSE : Une liste avec le titre et pourquoi c'est important pour Pyxis (1 phrase).
    ARTICLES : {txt}
    """
    try:
        return model.generate_content(prompt).text
    except:
        return "Erreur d'analyse IA."

# --- INTERFACE ---
with st.sidebar:
    st.markdown("<div style='color:#00A3C1; font-size:22px; font-weight:bold;'>PYXIS <span style='color:#777;'>Support</span></div>", unsafe_allow_html=True)
    st.write("---")
    st.subheader("⚙️ Configurer les flux")
    nouveau = st.text_input("Ajouter un mot-clé :")
    if st.button("Ajouter +"):
        st.session_state['mes_sujets'].append(nouveau)
        st.rerun()
    st.write("---")
    st.subheader("📍 Divisions & Sujets")
    for s in st.session_state['mes_sujets']:
        c1, c2 = st.columns([5,1])
        c1.write(f"• {s}")
        if c2.button("X", key=s):
            st.session_state['mes_sujets'].remove(s)
            st.rerun()

st.markdown("<h1 class='main-title'>Veille Stratégique Opérationnelle</h1>", unsafe_allow_html=True)

if st.button("LANCER L'ANALYSE DES DIVISIONS 🚀"):
    with DDGS() as ddgs:
        for sujet in st.session_state['mes_sujets']:
            st.markdown(f"### 📌 {sujet}")
            with st.spinner("Tri par IA..."):
                raw = list(ddgs.news(sujet, region="fr-fr", timelimit="d", max_results=8))
                if raw:
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.info(analyser_ia(sujet, raw))
                    with col2:
                        for a in raw[:4]:
                            st.markdown(f"<div class='article-card'><a href='{a['url']}' target='_blank'><b>{a['title']}</b></a><br><small>{a['source']}</small></div>", unsafe_allow_html=True)
                else:
                    st.write("Pas d'actualité aujourd'hui.")
