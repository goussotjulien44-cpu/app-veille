import streamlit as st
from duckduckgo_search import DDGS
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Veille Stratégique - MA-IA", page_icon="🤖", layout="wide")

# --- INITIALISATION DE LA MÉMOIRE ---
if 'mes_sujets' not in st.session_state:
    st.session_state['mes_sujets'] = ["Intelligence Artificielle", "Marchés Publics"]

# --- DESIGN MA-IA (CORRIGÉ) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

        .stApp { background-color: #FFFFFF; font-family: 'Roboto', sans-serif; }
        
        h1, h2, h3, p, div, label { color: #333333; }
        
        .main-title { text-align: center; font-weight: 700; font-size: 2.5em; margin-bottom: 0.5em; }

        /* Cartes d'articles */
        .article-card {
            background-color: #FFFFFF;
            padding: 20px;
            border-top: 4px solid #C5A059;
            border-radius: 5px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            margin-bottom: 20px;
        }
        
        /* LIENS */
        a { text-decoration: none; color: #333333 !important; font-weight: bold; }
        a:hover { color: #C5A059 !important; }
        
        /* BOUTON PRINCIPAL (Texte blanc forcé) */
        div.stButton > button {
            background-color: #000000 !important;
            color: #FFFFFF !important;
            border: none;
            border-radius: 5px;
            padding: 10px 24px;
            font-weight: bold;
            width: 100%;
        }
        
        /* BOUTON SUPPRESSION (Croix blanche sur fond noir) */
        div[data-testid="stVerticalBlock"] div.stButton > button {
            background-color: #000000 !important;
            color: #FFFFFF !important;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            padding: 0;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        section[data-testid="stSidebar"] { background-color: #F8F9FA; border-right: 1px solid #E9ECEF; }
    </style>
""", unsafe_allow_html=True)

# --- LOGIQUE DE RECHERCHE ---
def get_news(topic):
    results = []
    try:
        with DDGS() as ddgs:
            gen = ddgs.news(topic, region="fr-fr", timelimit="d", max_results=10)
            for r in gen:
                results.append(r)
    except:
        pass
    return results

# --- INTERFACE ---
st.markdown("<h1 class='main-title'>Bienvenue sur votre Veille Stratégique</h1>", unsafe_allow_html=True)
st.markdown("---")

with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    nouveau_sujet = st.text_input("Nouveau mot-clé :")
    if st.button("Ajouter +"):
        if nouveau_sujet and nouveau_sujet not in st.session_state['mes_sujets']:
            st.session_state['mes_sujets'].append(nouveau_sujet)
            st.rerun()

    st.markdown("---")
    st.markdown("### 📍 Sujets actifs")
    for s in st.session_state['mes_sujets']:
        col_text, col_btn = st.columns([4, 1])
        col_text.markdown(f"**{s}**")
        # La croix sera blanche sur fond noir grâce au CSS ci-dessus
        if col_btn.button("X", key=f"del_{s}"):
            st.session_state['mes_sujets'].remove(s)
            st.rerun()

# --- ACTIONS ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Lancer l'analyse quotidienne 🚀"):
        st.session_state['run_search'] = True

if 'run_search' in st.session_state and st.session_state['mes_sujets']:
    for sujet in st.session_state['mes_sujets']:
        st.markdown(f"### 📌 Résultats : {sujet}")
        articles = get_news(sujet)
        if articles:
            cols = st.columns(2)
            for i, art in enumerate(articles):
                with cols[i % 2]:
                    st.markdown(f"""
                    <div class="article-card">
                        <div style="color: #C5A059; font-weight:bold; font-size: 0.8em; margin-bottom: 10px;">
                            {art.get('source', 'Source')} • {art.get('date', '')}
                        </div>
                        <a href="{art.get('url', '#')}" target="_blank">
                            <h4 style="margin: 0;">{art.get('title', 'Sans titre')}</h4>
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info(f"Rien pour '{sujet}' aujourd'hui.")

