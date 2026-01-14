import streamlit as st
from duckduckgo_search import DDGS
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Veille Pyxis Support", page_icon="⚖️", layout="wide")

# --- 2. DESIGN "PYXIS" HAUTE VISIBILITÉ ---
st.markdown("""
    <style>
        /* Fond et texte global */
        .stApp { background-color: #FFFFFF !important; }
        
        /* Barre latérale : Forçage visuel */
        [data-testid="stSidebar"] {
            background-color: #F1F3F6 !important;
            border-right: 2px solid #000;
        }
        /* Correction de la case jaune : Texte forcé en Noir */
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] span, 
        [data-testid="stSidebar"] label {
            color: #000000 !important;
            font-weight: 700 !important;
            opacity: 1 !important;
        }

        /* Titres et Textes Zone Principale */
        h1, h2, h3, b, strong, p { color: #000000 !important; }
        
        .titre-pyxis {
            color: #000000 !important;
            font-size: 38px !important;
            font-weight: 900 !important;
            text-align: center;
            display: block;
            margin-bottom: 20px;
        }

        /* Cartes d'articles */
        .article-card {
            background-color: #ffffff;
            padding: 15px;
            border: 1px solid #DDD;
            border-left: 8px solid #C5A059;
            border-radius: 8px;
            margin-bottom: 12px;
        }
        
        /* Bouton Lancement */
        div.stButton > button {
            background-color: #000000 !important;
            color: #FFFFFF !important;
            border: 2px solid #000 !important;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. INITIALISATION DES DIVISIONS ---
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

# --- 4. INTERFACE ---
with st.sidebar:
    st.markdown("<h1 style='color:#00A3C1 !important; margin:0;'>PYXIS</h1><small style='color:black;'>Support</small>", unsafe_allow_html=True)
    st.write("---")
    
    # La zone de saisie qui était "invisible"
    nouveau = st.text_input("Saisir un mot-clé :", placeholder="ex: Cybersécurité", key="input_veille")
    if st.button("Ajouter à la veille"):
        if nouveau and nouveau not in st.session_state['mes_sujets']:
            st.session_state['mes_sujets'].append(nouveau); st.rerun()
            
    st.write("---")
    st.write("**Divisions actives :**")
    for s in st.session_state['mes_sujets']:
        c1, c2 = st.columns([5, 1])
        c1.write(f"• {s}")
        if c2.button("X", key=f"del_{s}"):
            st.session_state['mes_sujets'].remove(s); st.rerun()

st.markdown('<span class="titre-pyxis">Veille Stratégique Opérationnelle</span>', unsafe_allow_html=True)

if st.button("DÉMARRER LA RECHERCHE 🚀", use_container_width=True):
    with DDGS() as ddgs:
        for sujet in st.session_state['mes_sujets']:
            st.markdown(f"<h2 style='border-bottom: 2px solid #C5A059; padding-top:15px;'>📌 {sujet}</h2>", unsafe_allow_html=True)
            
            # Pause technique pour éviter le blocage
            time.sleep(1.5)
            
            try:
                results = list(ddgs.news(sujet, region="fr-fr", timelimit="d", max_results=3))
                if results:
                    col_ia, col_news = st.columns([1, 1.2])
                    with col_ia:
                        st.markdown("**Synthèse IA Pyxis :**")
                        # Message d'attente propre
                        st.warning("⚡ Fonctionnalité IA en cours de développement.")
                        st.caption("Le moteur d'analyse stratégique sera bientôt relié à votre clé API d'entreprise.")
                    with col_news:
                        for art in results:
                            st.markdown(f"""
                                <div class="article-card">
                                    <a href="{art['url']}" target="_blank" style="text-decoration:none; color:#000;">
                                        <b>{art['title']}</b>
                                    </a><br>
                                    <small style="color:#666;">Source : {art['source']}</small>
                                </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("Aucune actualité publiée aujourd'hui pour ce sujet.")
            except:
                st.error("Moteur de recherche saturé. Réessayez dans 1 minute.")
                break
