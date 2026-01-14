import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Veille Pyxis Support", page_icon="⚖️", layout="wide")

# --- 2. CONNEXION IA ---
API_KEY = st.secrets.get("API_KEY", "")

def initialiser_ia():
    if not API_KEY: return None
    try:
        genai.configure(api_key=API_KEY)
        # On utilise le nom de modèle le plus stable
        return genai.GenerativeModel('gemini-1.5-flash')
    except: return None

model = initialiser_ia()

# --- 3. DIVISIONS PYXIS ---
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

# --- 4. DESIGN CONTRASTE NOIR/BLANC ---
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF !important; }
        [data-testid="stSidebar"] { background-color: #F1F3F6 !important; border-right: 1px solid #DDD; }
        [data-testid="stSidebar"] * { color: #000000 !important; font-weight: 600 !important; }
        h1, h2, h3 { color: #000000 !important; }
        .article-card {
            background-color: #ffffff; padding: 15px; border: 1px solid #EEE;
            border-left: 6px solid #C5A059; border-radius: 8px; margin-bottom: 15px;
        }
        div.stButton > button { background-color: #000000 !important; color: #FFFFFF !important; }
    </style>
""", unsafe_allow_html=True)

# --- 5. LOGIQUE D'ANALYSE ---
def generer_analyse(sujet, articles):
    if not model: return "⚠️ IA non configurée."
    titres = "\n".join([f"- {a['title']}" for a in articles[:3]])
    prompt = f"Expert Pyxis Support : Analyse brièvement l'intérêt de ces actus pour '{sujet}' (Infrastructures, IT, Marchés publics). Rejette le Canada. 2 points clés.\n\n{titres}"
    try:
        response = model.generate_content(prompt)
        return response.text if response.text else "Analyse indisponible."
    except: return "L'IA analyse les données..."

# --- 6. INTERFACE ---
with st.sidebar:
    st.markdown("<h2 style='color:#00A3C1; margin-bottom:0;'>PYXIS</h2><h4 style='color:#777; margin-top:0;'>Support</h4>", unsafe_allow_html=True)
    st.write("---")
    nouveau = st.text_input("Ajouter un mot-clé :")
    if st.button("Ajouter +"):
        if nouveau and nouveau not in st.session_state['mes_sujets']:
            st.session_state['mes_sujets'].append(nouveau); st.rerun()
    st.write("---")
    for s in st.session_state['mes_sujets']:
        c1, c2 = st.columns([5, 1])
        c1.write(s)
        if c2.button("X", key=f"del_{s}"):
            st.session_state['mes_sujets'].remove(s); st.rerun()

st.markdown("<h1 style='text-align:center;'>Veille Stratégique Opérationnelle</h1>", unsafe_allow_html=True)

if st.button("LANCER L'ANALYSE GLOBALE 🚀", use_container_width=True):
    # On utilise un seul gestionnaire DuckDuckGo pour toute la boucle
    with DDGS() as ddgs:
        for sujet in st.session_state['mes_sujets']:
            st.write("---")
            st.subheader(f"📌 {sujet}")
            
            try:
                # Petite pause pour éviter le blocage DuckDuckGo
                time.sleep(1.5)
                results = list(ddgs.news(sujet, region="fr-fr", timelimit="d", max_results=4))
                
                if results:
                    col1, col2 = st.columns([1, 1.2])
                    with col1:
                        st.markdown("**Synthèse Pyxis :**")
                        st.info(generer_analyse(sujet, results))
                    with col2:
                        for art in results[:3]:
                            st.markdown(f"<div class='article-card'><a href='{art['url']}' target='_blank' style='text-decoration:none; color:#000;'><b>{art['title']}</b></a><br><small>{art['source']}</small></div>", unsafe_allow_html=True)
                else:
                    st.write("Aucune actualité détectée ce jour.")
            except Exception as e:
                st.error(f"Le moteur de recherche est saturé. Réessayez dans 1 minute.")
                break # On arrête la boucle si on est bloqué
