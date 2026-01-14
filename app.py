import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai

# --- CONFIGURATION INITIALE ---
st.set_page_config(page_title="Veille Pyxis Support", page_icon="⚖️", layout="wide")

# --- CLE API GEMINI ---
API_KEY = st.secrets.get("API_KEY", "")
if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

# --- INITIALISATION DES DIVISIONS ---
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

# --- DESIGN "ULTRA-LISIBLE" ---
st.markdown(f"""
    <style>
        /* Fond global blanc */
        .stApp {{ background-color: #FFFFFF !important; }}
        
        /* BARRE LATÉRALE : On force le texte en NOIR PUR */
        [data-testid="stSidebar"] {{
            background-color: #F8F9FA !important;
            border-right: 1px solid #DDD;
            min-width: 300px;
        }}
        [data-testid="stSidebar"] * {{
            color: #000000 !important; /* Noir pur pour tout le monde */
        }}
        
        /* Titre Principal */
        .main-title {{
            text-align: center;
            color: #000000 !important;
            font-weight: 800;
            font-size: 2.5em;
            margin-bottom: 30px;
        }}

        /* Cartes d'articles */
        .article-card {{
            background-color: #ffffff;
            padding: 15px;
            border: 1px solid #EEE;
            border-top: 5px solid #C5A059;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            margin-bottom: 10px;
        }}
        .article-card b {{ color: #000000 !important; }}
        
        /* Boutons Noirs */
        div.stButton > button {{
            background-color: #000000 !important;
            color: #FFFFFF !important;
            border: none;
            font-weight: bold;
        }}
    </style>
""", unsafe_allow_html=True)

# --- LOGIQUE IA ---
def analyser_ia(sujet, articles):
    if not API_KEY: return "⚠️ Mode dégradé : Veuillez configurer la clé API dans les Secrets."
    txt = "\n".join([f"- {a['title']} (Source: {a['source']})" for a in articles])
    prompt = f"Expert Pyxis Support : Analyse ces articles pour la division '{sujet}'. Garde les 3 plus stratégiques (secteur public/infra/IT). Rejette le Canada et l'alimentaire. Donne une synthèse ultra-courte."
    try:
        return model.generate_content(prompt + "\nArticles:\n" + txt).text
    except: return "Analyse IA indisponible."

# --- INTERFACE ---

with st.sidebar:
    # Logo Texte Pyxis (Plus fiable que l'image pour le moment)
    st.markdown("<h2 style='color:#00A3C1; margin-bottom:0;'>PYXIS</h2><h4 style='color:#777; margin-top:0;'>Support</h4>", unsafe_allow_html=True)
    st.write("---")
    
    st.markdown("### ⚙️ Configuration")
    nouveau = st.text_input("Ajouter un mot-clé :", key="new_topic")
    if st.button("Ajouter +"):
        if nouveau and nouveau not in st.session_state['mes_sujets']:
            st.session_state['mes_sujets'].append(nouveau)
            st.rerun()
            
    st.write("---")
    st.markdown("### 📍 Divisions")
    for s in st.session_state['mes_sujets']:
        c1, c2 = st.columns([5, 1])
        c1.markdown(f"**{s}**")
        if c2.button("X", key=f"del_{s}"):
            st.session_state['mes_sujets'].remove(s)
            st.rerun()

# CONTENU CENTRAL
st.markdown("<h1 class='main-title'>Veille Stratégique Opérationnelle</h1>", unsafe_allow_html=True)

if not API_KEY:
    st.warning("⚡ **Action requise :** Ajoutez votre 'API_KEY' dans les Secrets de Streamlit pour activer l'analyse intelligente.")

if st.button("LANCER L'ANALYSE DU JOUR 🚀", use_container_width=True):
    with DDGS() as ddgs:
        for sujet in st.session_state['mes_sujets']:
            st.markdown(f"### 📌 {sujet}")
            with st.spinner("Analyse..."):
                raw = list(ddgs.news(sujet, region="fr-fr", timelimit="d", max_results=6))
                if raw:
                    col1, col2 = st.columns([1, 1.2])
                    with col1:
                        st.markdown("**Synthèse IA :**")
                        st.info(analyser_ia(sujet, raw))
                    with col2:
                        for a in raw[:3]:
                            st.markdown(f"""
                                <div class="article-card">
                                    <a href="{a['url']}" target="_blank" style="text-decoration:none;">
                                        <b>{a['title']}</b>
                                    </a><br>
                                    <small style="color:#C5A059;">{a['source']} • {a['date']}</small>
                                </div>
                            """, unsafe_allow_html=True)
                else:
                    st.write("Aucune actualité ce jour.")
