import streamlit as st
from duckduckgo_search import DDGS

# --- CONFIGURATION INITIALE ---
st.set_page_config(page_title="Veille Pyxis Support", page_icon="⚖️", layout="wide")

# --- MÉMOIRE DES DONNÉES ---
if 'mes_sujets' not in st.session_state:
    st.session_state['mes_sujets'] = ["Intelligence Artificielle", "Marchés Publics"]

# --- DESIGN HAUT CONTRASTE (STYLE MA-IA) ---
st.markdown("""
    <style>
        /* Fond global et police */
        .stApp { background-color: #FFFFFF; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        
        /* Titre Principal : NOIR PROFOND pour lisibilité totale */
        .main-title { 
            text-align: center; 
            color: #000000 !important; 
            font-weight: 800; 
            font-size: 2.8em; 
            padding: 20px;
            margin-bottom: 10px;
        }

        /* Barre latérale : Texte Noir */
        [data-testid="stSidebar"] { background-color: #F0F2F6; border-right: 2px solid #D1D5DB; }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
            color: #000000 !important;
            font-weight: 600;
        }

        /* Cartes d'actualités avec bordure visible */
        .article-card {
            background-color: #ffffff;
            padding: 18px;
            border: 1px solid #E5E7EB;
            border-top: 6px solid #C5A059;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            height: 100%;
        }
        
        /* Titres des articles en NOIR */
        .article-card b { color: #000000 !important; font-size: 1.15em; display: block; margin-top: 5px; }
        .article-card a { text-decoration: none; }
        .article-card a:hover b { color: #C5A059 !important; }

        /* Boutons Noirs / Texte Blanc */
        div.stButton > button {
            background-color: #000000 !important;
            color: #FFFFFF !important;
            border: none;
            font-weight: bold;
            font-size: 1.1em;
            width: 100%;
            padding: 10px;
        }

        /* Titres des sections de recherche */
        h3 { color: #000000 !important; font-weight: 700; border-bottom: 2px solid #C5A059; padding-bottom: 5px; margin-top: 30px; }
    </style>
""", unsafe_allow_html=True)

# --- FONCTION DE RECHERCHE ---
def get_news(topic):
    try:
        with DDGS() as ddgs:
            return list(ddgs.news(topic, region="fr-fr", timelimit="d", max_results=8))
    except: return []

# --- CONSTRUCTION DE L'INTERFACE ---

with st.sidebar:
    # LOGO RECRÉÉ (Boussole + Nom)
    col_logo1, col_logo2 = st.columns([1, 4])
    with col_logo1:
        st.markdown("<h2 style='margin:0;'>🧭</h2>", unsafe_allow_html=True) # Icône stable
    with col_logo2:
        st.markdown("<div style='color:#00A3C1; font-size:22px; font-weight:bold; line-height:1;'>PYXIS<br><span style='color:#777; font-size:16px;'>Support</span></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("⚙️ Configuration")
    
    nouveau = st.text_input("Ajouter un mot-clé :", key="add_input")
    if st.button("Valider l'ajout ➕"):
        if nouveau and nouveau not in st.session_state['mes_sujets']:
            st.session_state['mes_sujets'].append(nouveau)
            st.rerun()

    st.markdown("---")
    st.subheader("📍 Vos Sujets de Veille")
    for s in st.session_state['mes_sujets']:
        c1, c2 = st.columns([5, 1])
        # On force l'affichage en noir pour les mots-clés
        c1.markdown(f"<span style='color:black;'>• {s}</span>", unsafe_allow_html=True)
        if c2.button("X", key=f"del_{s}"):
            st.session_state['mes_sujets'].remove(s)
            st.rerun()

# CONTENU CENTRAL
st.markdown("<h1 class='main-title'>Veille Stratégique Opérationnelle</h1>", unsafe_allow_html=True)

c_a, c_b, c_c = st.columns([1, 2, 1])
with c_b:
    if st.button("LANCER L'ANALYSE DU JOUR 🚀"):
        st.session_state['active_search'] = True

if st.session_state.get('active_search'):
    for sujet in st.session_state['mes_sujets']:
        st.markdown(f"### 📌 Sujet : {sujet}")
        articles = get_news(sujet)
        if articles:
            g1, g2 = st.columns(2)
            for i, art in enumerate(articles):
                with (g1 if i % 2 == 0 else g2):
                    st.markdown(f"""
                        <div class="article-card">
                            <span style="color:#C5A059; font-size:0.85em; font-weight:bold;">
                                {art.get('source')} • {art.get('date')}
                            </span>
                            <a href="{art.get('url')}" target="_blank">
                                <b>{art.get('title')}</b>
                            </a>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info(f"Aucune actualité trouvée pour '{sujet}' (dernières 24h).")
