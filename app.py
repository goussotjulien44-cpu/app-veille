import streamlit as st
from duckduckgo_search import DDGS

# --- CONFIGURATION ---
st.set_page_config(page_title="Veille Stratégique - MA-IA", page_icon="🤖", layout="wide")

# --- MÉMOIRE ---
if 'mes_sujets' not in st.session_state:
    st.session_state['mes_sujets'] = ["Intelligence Artificielle", "Marchés Publics"]

# --- DESIGN ÉPURÉ (STABLE) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
        html, body, [class*="css"]  { font-family: 'Roboto', sans-serif; }
        
        .main-title { text-align: center; font-weight: 700; font-size: 2.2em; color: #333; margin-bottom: 20px; }
        
        /* Cartes Articles Style MA-IA */
        .article-card {
            background-color: #ffffff;
            padding: 1.5rem;
            border-top: 5px solid #C5A059;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            margin-bottom: 1rem;
            height: 100%;
        }
        
        /* Forcer le texte du bouton principal en BLANC */
        div.stButton > button:first-child {
            background-color: #000000 !important;
            color: #ffffff !important;
            border: none;
            padding: 0.6rem 2rem;
            font-weight: bold;
        }

        /* Liens */
        .article-card a { text-decoration: none; color: #1a1a1a !important; font-size: 1.1em; }
        .article-card a:hover { color: #C5A059 !important; }
    </style>
""", unsafe_allow_html=True)

# --- LOGIQUE RECHERCHE ---
def get_news(topic):
    try:
        with DDGS() as ddgs:
            return list(ddgs.news(topic, region="fr-fr", timelimit="d", max_results=10))
    except: return []

# --- INTERFACE ---
st.markdown("<h1 class='main-title'>Bienvenue sur votre Veille Stratégique</h1>", unsafe_allow_html=True)

# Barre Latérale
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3649/3649238.png", width=50) # Icone neutre
    st.title("Configuration")
    
    with st.expander("➕ Ajouter un sujet", expanded=True):
        nouveau = st.text_input("Mot-clé :", key="input_sujet")
        if st.button("Valider l'ajout"):
            if nouveau and nouveau not in st.session_state['mes_sujets']:
                st.session_state['mes_sujets'].append(nouveau)
                st.rerun()

    st.markdown("---")
    st.subheader("📍 Sujets actifs")
    for s in st.session_state['mes_sujets']:
        cols = st.columns([4, 1])
        cols[0].write(s)
        if cols[1].button("X", key=f"del_{s}"):
            st.session_state['mes_sujets'].remove(s)
            st.rerun()

# Zone Centrale
col_a, col_b, col_c = st.columns([1, 2, 1])
with col_b:
    btn_search = st.button("LANCER L'ANALYSE QUOTIDIENNE 🚀", use_container_width=True)

if btn_search or 'results' in st.session_state:
    st.session_state['results'] = True
    
    for sujet in st.session_state['mes_sujets']:
        st.markdown(f"### 📌 {sujet}")
        res = get_news(sujet)
        if res:
            # Affichage en grille de 2 colonnes
            grid_cols = st.columns(2)
            for i, art in enumerate(res):
                with grid_cols[i % 2]:
                    st.markdown(f"""
                        <div class="article-card">
                            <p style="color:#C5A059; font-size:0.8em; font-weight:bold; margin-bottom:5px;">
                                {art.get('source','Source')} • {art.get('date','')}
                            </p>
                            <a href="{art.get('url','#')}" target="_blank">
                                <b>{art.get('title','Sans titre')}</b>
                            </a>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info(f"Aucune actualité récente pour '{sujet}'.")

