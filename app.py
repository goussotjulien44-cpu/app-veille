import streamlit as st
from duckduckgo_search import DDGS
import pandas as pd
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Veille Stratégique - Cabinet",
    page_icon="unive",
    layout="centered"
)

# --- DESIGN "LUXE & CONSEIL" (CSS INJECTÉ) ---
st.markdown("""
    <style>
        /* Importation de polices élégantes */
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@300;400&display=swap');

        /* Fond et couleurs globales */
        .stApp {
            background-color: #F9F9F9;
        }
        
        /* Titres */
        h1, h2, h3 {
            font-family: 'Playfair Display', serif;
            color: #1A2421; /* Vert très sombre / Noir charbon */
        }
        
        /* Texte courant */
        p, div, label {
            font-family: 'Lato', sans-serif;
            color: #4A4A4A;
        }

        /* Cartes d'articles */
        .article-card {
            background-color: #FFFFFF;
            padding: 20px;
            border-left: 4px solid #C5A059; /* Or mat */
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-bottom: 20px;
            transition: transform 0.2s;
        }
        .article-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.1);
        }
        
        /* Liens */
        a {
            text-decoration: none;
            color: #1A2421 !important;
            font-weight: bold;
        }
        a:hover {
            color: #C5A059 !important;
        }
        
        /* Boutons */
        div.stButton > button {
            background-color: #1A2421;
            color: #C5A059;
            border: none;
            font-family: 'Lato', sans-serif;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 10px 24px;
        }
        div.stButton > button:hover {
            background-color: #2C3E38;
            color: #FFF;
            border: none;
        }
        
        /* Input fields */
        div[data-baseweb="input"] > div {
            border-radius: 0px;
            border-bottom: 2px solid #C5A059;
            background-color: transparent;
        }
    </style>
""", unsafe_allow_html=True)

# --- LOGIQUE DE RECHERCHE ---
def search_news(keywords):
    results = []
    try:
        with DDGS() as ddgs:
            # Recherche news, région France (fr-fr), temps: 1 jour (d), max 10 résultats
            ddgs_news_gen = ddgs.news(
                keywords, 
                region="fr-fr", 
                safesearch="off", 
                timelimit="d", 
                max_results=10
            )
            for r in ddgs_news_gen:
                results.append(r)
    except Exception as e:
        st.error(f"Erreur lors de la recherche : {e}")
    return results

# --- INTERFACE UTILISATEUR ---

# En-tête
st.markdown("<h1 style='text-align: center; margin-bottom: 10px;'>V E I L L E &middot; S T R A T É G I Q U E</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-style: italic; color: #888;'>Excellence & Insights</p>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar pour la configuration
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.markdown("Personnalisez votre flux d'information.")
    
    # Gestion des mots clés de l'utilisateur (Stocké dans la session temporaire)
    user_topic = st.text_input("Sujet de veille (ex: IA générative)", "Transformation Digitale")
    
    st.info("Cette application recherche les articles parus dans les dernières 24h.")

# Bouton de rafraîchissement
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Lancer l'analyse quotidienne", use_container_width=True):
        st.session_state['refresh'] = True

# Affichage des résultats
if 'refresh' in st.session_state and user_topic:
    with st.spinner(f"Analyse du web pour : {user_topic}..."):
        articles = search_news(user_topic)
        
    if articles:
        st.markdown(f"### 📰 Sélection du jour : {user_topic}")
        st.write(f"*{datetime.now().strftime('%d/%m/%Y')} - Top 10 articles*")
        
        for article in articles:
            # Nettoyage et affichage
            source = article.get('source', 'Source inconnue')
            date = article.get('date', '')
            title = article.get('title', 'Sans titre')
            link = article.get('url', '#')
            # L'image n'est pas toujours dispo via DDG, on fait sans pour le style minimaliste
            
            st.markdown(f"""
            <div class="article-card">
                <div style="font-size: 0.8em; color: #C5A059; text-transform: uppercase; margin-bottom: 5px;">
                    {source} &bull; {date}
                </div>
                <a href="{link}" target="_blank">
                    <h3 style="margin-top: 0; font-size: 1.2em;">{title}</h3>
                </a>
                <p style="font-size: 0.9em; margin-bottom: 0;">Cliquer sur le titre pour lire l'article complet.</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("Aucun article pertinent trouvé dans les dernières 24h. Essayez d'élargir votre recherche.")

# Pied de page
st.markdown("---")
st.markdown("<div style='text-align: center; font-size: 0.7em; color: #BBB;'>Powered by Automated Intelligence • Usage Interne</div>", unsafe_allow_html=True)
