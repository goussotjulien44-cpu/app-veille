import streamlit as st
from duckduckgo_search import DDGS

# --- CONFIGURATION (Structure Stable) ---
st.set_page_config(page_title="Veille Stratégique - Pyxis", page_icon="⚖️", layout="wide")

# --- MÉMOIRE ---
if 'mes_sujets' not in st.session_state:
    st.session_state['mes_sujets'] = ["Intelligence Artificielle", "Marchés Publics"]

# --- DESIGN ROBUSTE (Noir & Blanc MA-IA) ---
st.markdown("""
    <style>
        /* Fond blanc et police propre */
        .stApp { background-color: #FFFFFF; font-family: 'Helvetica', sans-serif; }
        
        /* Titre principal bien visible */
        .main-title { text-align: center; color: #1A1A1A; font-weight: bold; padding: 20px; }

        /* Style des boutons noirs avec texte BLANC */
        div.stButton > button {
            background-color: #000000 !important;
            color: #FFFFFF !important;
            border-radius: 4px;
            font-weight: bold;
            border: none;
            width: 100%;
        }
        
        /* Cartes d'articles */
        .article-card {
            background-color: #ffffff;
            padding: 20px;
            border-top: 4px solid #C5A059;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 15px;
        }
        
        /* Sidebar grise comme MA-IA */
        [data-testid="stSidebar"] { background-color: #F8F9FA; border-right: 1px solid #EEE; }
        
        /* Logo Texte Pyxis */
        .pyxis-logo { color: #00A3C1; font-weight: bold; font-size: 24px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- LOGIQUE RECHERCHE ---
def get_news(topic):
    try:
        with DDGS() as ddgs:
            return list(ddgs.news(topic, region="fr-fr", timelimit="d", max_results=8))
    except: return []

# --- INTERFACE ---

# Barre Latérale (Sidebar)
with st.sidebar:
    # Si l'image ne charge pas, on met un beau texte stylé
    st.markdown("<div class='pyxis-logo'>PYXIS <span style='color:#777;'>Support</span></div>", unsafe_allow_html=True)
    st.markdown("### ⚙️ Configuration")
    
    nouveau = st.text_input("Ajouter un mot-clé :", placeholder="ex: Innovation")
    if st.button("Valider l'ajout"):
        if nouveau and nouveau not in st.session_state['mes_sujets']:
            st.session_state['mes_sujets'].append(nouveau)
            st.rerun()

    st.markdown("---")
    st.subheader("📍 Vos flux")
    for s in st.session_state['mes_sujets']:
        c1, c2 = st.columns([4, 1])
        c1.write(s)
        if c2.button("X", key=f"del_{s}"):
            st.session_state['mes_sujets'].remove(s)
            st.rerun()

# Zone Centrale
st.markdown("<h1 class='main-title'>Veille Stratégique Opérationnelle</h1>", unsafe_allow_html=True)

# Bouton d'action
c_a, c_b, c_c = st.columns([1, 2, 1])
with c_b:
    if st.button("LANCER L'ANALYSE DU JOUR 🚀"):
        st.session_state['search_active'] = True

# Résultats
if st.session_state.get('search_active'):
    for sujet in st.session_state['mes_sujets']:
        st.write(f"### 📌 {sujet}")
        articles = get_news(sujet)
        if articles:
            g1, g2 = st.columns(2)
            for i, art in enumerate(articles):
                with (g1 if i % 2 == 0 else g2):
                    st.markdown(f"""
                        <div class="article-card">
                            <small style="color:#C5A059;">{art.get('source')} • {art.get('date')}</small><br>
                            <a href="{art.get('url')}" target="_blank" style="text-decoration:none; color:#222; font-weight:bold;">
                                {art.get('title')}
                            </a>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info(f"Aucun article trouvé pour '{sujet}'.")
