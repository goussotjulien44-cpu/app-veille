import streamlit as st
from duckduckgo_search import DDGS
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Veille Stratégique", page_icon="⚖️", layout="wide")

# --- INITIALISATION DE LA MÉMOIRE (Session State) ---
# Cela permet de garder les mots-clés en mémoire même quand on clique sur des boutons
if 'mes_sujets' not in st.session_state:
    st.session_state['mes_sujets'] = ["Intelligence Artificielle", "Luxe Durable"]

# --- DESIGN "LUXE & CONSEIL" ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@300;400&display=swap');
        .stApp { background-color: #FDFDFD; }
        h1, h2, h3 { font-family: 'Playfair Display', serif; color: #1A2421; }
        .article-card {
            background-color: #FFFFFF;
            padding: 20px;
            border-left: 3px solid #C5A059;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin-bottom: 15px;
        }
        .topic-tag {
            background-color: #1A2421;
            color: #C5A059;
            padding: 5px 15px;
            border-radius: 20px;
            display: inline-block;
            margin: 5px;
            font-size: 0.8em;
            font-family: 'Lato', sans-serif;
        }
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
st.markdown("<h1 style='text-align: center;'>V E I L L E &middot; S T R A T É G I Q U E</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-style: italic;'>Tableau de bord personnalisé</p>", unsafe_allow_html=True)

# --- BARRE LATÉRALE : GESTION DES SUJETS ---
with st.sidebar:
    st.markdown("### ⚙️ Paramètres de Veille")
    
    # Ajouter un sujet
    nouveau_sujet = st.text_input("Ajouter un mot-clé :", placeholder="ex: Cybersécurité")
    if st.button("Ajouter à ma liste"):
        if nouveau_sujet and nouveau_sujet not in st.session_state['mes_sujets']:
            st.session_state['mes_sujets'].append(nouveau_sujet)
            st.rerun()

    st.markdown("---")
    st.markdown("### 📍 Mes flux actifs")
    for s in st.session_state['mes_sujets']:
        col_s, col_del = st.columns([4, 1])
        col_s.markdown(f"**{s}**")
        if col_del.button("❌", key=s):
            st.session_state['mes_sujets'].remove(s)
            st.rerun()

# --- ZONE CENTRALE : AFFICHAGE DES FLUX ---
if st.button("🔄 ACTUALISER TOUS LES FLUX", use_container_width=True):
    st.session_state['run_search'] = True

if 'run_search' in st.session_state:
    for sujet in st.session_state['mes_sujets']:
        st.markdown(f"## 📌 {sujet}")
        articles = get_news(sujet)
        
        if articles:
            for art in articles:
                st.markdown(f"""
                <div class="article-card">
                    <div style="color: #C5A059; font-size: 0.7em; text-transform: uppercase;">{art['source']} • {art['date']}</div>
                    <a href="{art['url']}" target="_blank" style="text-decoration:none; color:#1A2421;">
                        <h4 style="margin: 5px 0;">{art['title']}</h4>
                    </a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(f"Aucune nouveauté pour '{sujet}' ces dernières 24h.")
        st.markdown("<br>", unsafe_allow_html=True)
else:
    st.info("Cliquez sur le bouton ci-dessus pour charger vos veilles du jour.")
