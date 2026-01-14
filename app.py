import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai

# --- CONFIGURATION ---
st.set_page_config(page_title="Veille Pyxis Support", page_icon="⚖️", layout="wide")

# --- CONNEXION IA ---
API_KEY = st.secrets.get("API_KEY", "")

def configurer_ia():
    if API_KEY:
        try:
            genai.configure(api_key=API_KEY)
            return genai.GenerativeModel('gemini-1.5-flash')
        except: return None
    return None

model = configurer_ia()

# --- INITIALISATION DIVISIONS ---
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

# --- DESIGN PYXIS ---
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF !important; }
        [data-testid="stSidebar"] { background-color: #F0F2F6 !important; border-right: 1px solid #DDD; }
        [data-testid="stSidebar"] * { color: #000000 !important; font-weight: 600 !important; }
        h1, h2, h3 { color: #000000 !important; }
        .article-card {
            background-color: #ffffff; padding: 15px; border: 1px solid #EEE;
            border-left: 6px solid #C5A059; border-radius: 8px; margin-bottom: 15px;
        }
        div.stButton > button { background-color: #000000 !important; color: #FFFFFF !important; }
    </style>
""", unsafe_allow_html=True)

# --- LOGIQUE IA AMÉLIORÉE ---
def analyser_ia(sujet, articles):
    if not model:
        return "⚠️ Erreur de configuration de la clé API."
    
    # On simplifie la liste pour l'IA
    liste_titres = "\n".join([f"- {a['title']}" for a in articles[:4]])
    
    prompt = f"""
    En tant qu'expert pour Pyxis Support, analyse brièvement ces actus pour la division '{sujet}'.
    Focalise sur : Marchés publics, Infrastructure, IT. 
    Exclus : Canada, alimentation.
    Donne 2 ou 3 puces d'analyse stratégique.
    Titres :
    {liste_titres}
    """
    
    try:
        # Ajout d'une sécurité pour éviter le blocage indéfini
        response = model.generate_content(prompt, safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        ])
        return response.text if response.text else "L'IA n'a pas pu générer de texte pour ces sources."
    except Exception as e:
        return f"Note : Analyse indisponible pour ce sujet (Raisons techniques)."

# --- INTERFACE ---
with st.sidebar:
    st.markdown("<h2 style='color:#00A3C1;'>PYXIS</h2><p>Support</p>", unsafe_allow_html=True)
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

if st.button("LANCER L'ANALYSE INTELLIGENTE 🚀", use_container_width=True):
    with DDGS() as ddgs:
        for sujet in st.session_state['mes_sujets']:
            st.markdown(f"### 📌 {sujet}")
            with st.spinner("Analyse en cours..."):
                raw = list(ddgs.news(sujet, region="fr-fr", timelimit="d", max_results=5))
                if raw:
                    col1, col2 = st.columns([1, 1.2])
                    with col1:
                        st.markdown("**Synthèse Pyxis :**")
                        # L'appel à l'IA est ici
                        synthese = analyser_ia(sujet, raw)
                        st.info(synthese)
                    with col2:
                        for a in raw[:3]:
                            st.markdown(f"<div class='article-card'><a href='{a['url']}' target='_blank' style='text-decoration:none; color:#000;'><b>{a['title']}</b></a><br><small>{a['source']}</small></div>", unsafe_allow_html=True)
                else:
                    st.write("Pas d'actualité aujourd'hui.")
