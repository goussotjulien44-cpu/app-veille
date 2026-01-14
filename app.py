import streamlit as st
from duckduckgo_search import DDGS
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
# Layout "wide" pour profiter de l'espace comme sur MA-IA
st.set_page_config(page_title="Veille Stratégique - MA-IA", page_icon="🤖", layout="wide")

# --- INITIALISATION DE LA MÉMOIRE (Session State) ---
if 'mes_sujets' not in st.session_state:
    # Sujets par défaut
    st.session_state['mes_sujets'] = ["Intelligence Artificielle", "Marchés Publics"]

# --- DESIGN "MA-IA TECH & CLEAN" (CSS ADAPTÉ) ---
st.markdown("""
    <style>
        /* Importation de la police Roboto, moderne et clean */
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

        /* Fond global blanc pur */
        .stApp {
            background-color: #FFFFFF;
            font-family: 'Roboto', sans-serif;
        }
        
        /* Textes principaux en gris foncé */
        h1, h2, h3, p, div, label {
            color: #333333;
        }
        
        /* Titre principal centré */
        .main-title {
            text-align: center;
            font-weight: 700;
            font-size: 2.5em;
            margin-bottom: 0.5em;
        }

        /* Cartes d'articles style "Modules MA-IA" */
        .article-card {
            background-color: #FFFFFF;
            padding: 20px;
            /* Bordure supérieure épaisse couleur "Or/Moutarde" (style Sourcing) */
            border-top: 4px solid #C5A059;
            border-radius: 5px;
            /* Ombre douce pour l'effet de relief */
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            margin-bottom: 20px;
            transition: transform 0.2s;
        }
        .article-card:hover {
            transform: translateY(-3px);
        }
        
        /* Liens */
        a { text-decoration: none; color: #333333 !important; font-weight: bold; }
        a:hover { color: #C5A059 !important; }
        
        /* Style du bouton principal (Noir comme "Tutoriels" sur MA-IA) */
        div.stButton > button {
            background-color: #000000;
            color: #FFFFFF;
            border: none;
            border-radius: 5px;
            padding: 10px 24px;
            font-weight: bold;
        }
        div.stButton > button:hover {
            background-color: #333333;
            color: #FFFFFF;
        }

        /* Personnalisation de la sidebar pour qu'elle soit propre */
        section[data-testid="stSidebar"] {
            background-color: #F8F9FA; /* Gris très clair */
            border-right: 1px solid #E9ECEF;
        }
    </style>
""", unsafe_allow_html=True)

# --- LOGIQUE DE RECHERCHE ---
def get_news(topic):
    results = []
    try:
        with DDGS() as ddgs:
            # Recherche news, fr-fr, dernières 24h ("d"), max 10
            gen = ddgs.news(topic, region="fr-fr", timelimit="d", max_results=10)
            for r in gen:
                results.append(r)
    except Exception as e:
        print(f"Erreur: {e}")
        pass
    return results

# --- INTERFACE PRINCIPALE ---

# En-tête style MA-IA
st.markdown("<h1 class='main-title'>Bienvenue sur votre Veille Stratégique</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2em; color: #666;'>Analysez les dernières tendances de votre secteur en temps réel.</p>", unsafe_allow_html=True)
st.markdown("---")

# --- BARRE LATÉRALE : GESTION DES SUJETS ---
with st.sidebar:
    st.markdown("### ⚙️ Configuration des flux")
    st.write("Ajoutez les thèmes que vous souhaitez surveiller.")
    
    # Zone d'ajout
    nouveau_sujet = st.text_input("Nouveau mot-clé :", placeholder="ex: Appel d'offres IA")
    if st.button("Ajouter à ma liste +"):
        if nouveau_sujet and nouveau_sujet not in st.session_state['mes_sujets']:
            st.session_state['mes_sujets'].append(nouveau_sujet)
            st.rerun() # Recharge la page pour afficher le nouveau sujet

    st.markdown("---")
    st.markdown("### 📍 Vos sujets actifs")
    # Affichage de la liste avec bouton de suppression
    if not st.session_state['mes_sujets']:
        st.write("Aucun sujet configuré.")
    for s in st.session_state['mes_sujets']:
        col_text, col_btn = st.columns([4, 1])
        col_text.markdown(f"**{s}**")
        if col_btn.button("X", key=f"del_{s}", help="Supprimer ce sujet"):
            st.session_state['mes_sujets'].remove(s)
            st.rerun()

# --- ZONE CENTRALE : ACTIONS ET RÉSULTATS ---

# Bouton d'action principal style "MA-IA"
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Lancer l'analyse quotidienne 🚀", use_container_width=True):
        st.session_state['run_search'] = True

# Affichage des résultats si le bouton a été cliqué
if 'run_search' in st.session_state and st.session_state['mes_sujets']:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Boucle sur chaque sujet de la liste
    for sujet in st.session_state['mes_sujets']:
        st.markdown(f"### 📌 Résultats pour : {sujet}")
        
        with st.spinner(f"Recherche en cours sur '{sujet}'..."):
            articles = get_news(sujet)
        
        if articles:
            # Création de colonnes pour afficher les cartes côte à côte si l'écran est large
            cols = st.columns(2) # 2 cartes par ligne
            for i, art in enumerate(articles):
                with cols[i % 2]: # Alterne entre colonne de gauche et de droite
                    source = art.get('source', 'Source N/A')
                    date = art.get('date', 'Récemment')
                    title = art.get('title', 'Sans titre')
                    url = art.get('url', '#')
                    
                    st.markdown(f"""
                    <div class="article-card">
                        <div style="color: #C5A059; font-weight:bold; font-size: 0.8em; text-transform: uppercase; margin-bottom: 10px;">
                            {source} • {date}
                        </div>
                        <a href="{url}" target="_blank">
                            <h4 style="margin: 0; font-size: 1.1em;">{title}</h4>
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info(f"Aucun article trouvé dans les dernières 24h pour '{sujet}'.")
        
        st.markdown("---") # Séparateur entre les sujets

elif 'run_search' in st.session_state and not st.session_state['mes_sujets']:
    st.warning("Veuillez ajouter au moins un sujet dans la barre latérale.")
