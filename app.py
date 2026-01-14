import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Veille Pyxis Support", page_icon="⚖️", layout="wide")

# --- 2. CONNEXION IA (GEMINI) ---
# Utilisation du secret configuré dans Streamlit Cloud
API_KEY = st.secrets.get("API_KEY", "")

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        ia_disponible = True
    except Exception:
        ia_disponible = False
else:
    ia_disponible = False

# --- 3. INITIALISATION DES SUJETS (DIVISIONS PYXIS) ---
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

# --- 4. DESIGN PERSONNALISÉ (MA-IA STYLE) ---
st.markdown("""
    <style>
        /* Fond global et contraste */
        .stApp { background-color: #FFFFFF !important; }
        
        /* Barre latérale - Texte Noir sur Fond Gris clair */
        [data-testid="stSidebar"] {
            background-color: #F8F9FB !important;
            border-right: 1px solid #E0E0E0;
        }
        [data-testid="stSidebar"] * {
            color: #000000 !important;
            font-weight: 600 !important;
        }

        /* Titres principaux */
        h1, h2, h3 { 
            color: #000000 !important; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        /* Cartes d'articles */
        .article-card {
            background-color: #ffffff;
            padding: 18px;
            border: 1px solid #E5E7EB;
            border-left: 6px solid #C5A059;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-bottom: 15px;
            height: 100%;
        }
        .article-card b { color: #000000 !important; font-size: 1.1em; }
        .article-card small { color: #6B7280 !important; }

        /* Boutons noirs */
        div.stButton > button {
            background-color: #000000 !important;
            color: #FFFFFF !important;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# --- 5. LOGIQUE D'ANALYSE IA ---
def generer_analyse(sujet, articles):
    if not ia_disponible:
        return "⚠️ L'IA est en attente de configuration (Clé API)."
    
    # Préparation des données pour l'IA (Titres uniquement pour la rapidité)
    contexte_actus = "\n".join([f"- {a['title']}" for a in articles[:4]])
    
    prompt = f"""
    Tu es l'expert stratégique du cabinet Pyxis Support. 
    Analyse ces actualités pour la division : {sujet}.
    Pyxis travaille sur des projets d'infrastructure (ferroviaire, portuaire), d'IT complexe et de marchés publics (AMO).
    
    CONSIGNES :
    1. Rejette strictement le Canada et l'alimentation.
    2. Explique en 3 points courts pourquoi ces actus sont importantes pour les clients de Pyxis.
    3. Utilise un ton professionnel et direct.

    ACTUALITÉS :
    {contexte_actus}
    """
    
    try:
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text
        return "Analyse en attente de données plus précises."
    except Exception as e:
        return f"Note : Synthèse en cours de mise à jour (Détail : {str(e)[:40]})."

# --- 6. INTERFACE UTILISATEUR ---

# Barre latérale
with st.sidebar:
    # Logo Pyxis texte stylisé
    st.markdown("<h2 style='color:#00A3C1; margin-bottom:0;'>PYXIS</h2><h4 style='color:#777; margin-top:0;'>Support</h4>", unsafe_allow_html=True)
    st.write("---")
    
    st.subheader("⚙️ Configuration")
    nouveau = st.text_input("Nouveau mot-clé :")
    if st.button("Ajouter à la veille"):
        if nouveau and nouveau not in st.session_state['mes_sujets']:
            st.session_state['mes_sujets'].append(nouveau)
            st.rerun()
            
    st.write("---")
    st.subheader("📍 Vos Divisions")
    for s in st.session_state['mes_sujets']:
        c1, c2 = st.columns([5, 1])
        c1.write(s)
        if c2.button("X", key=f"del_{s}"):
            st.session_state['mes_sujets'].remove(s)
            st.rerun()

# Zone principale
st.markdown("<h1 style='text-align:center;'>Veille Stratégique Opérationnelle</h1>", unsafe_allow_html=True)

if st.button("LANCER L'ANALYSE GLOBALE 🚀", use_container_width=True):
    with DDGS() as ddgs:
        for sujet in st.session_state['mes_sujets']:
            st.write("---")
            st.subheader(f"📌 {sujet}")
            
            with st.spinner(f"Recherche et analyse pour {sujet}..."):
                # Recherche d'actualités fr (limite 1 jour)
                results = list(ddgs.news(sujet, region="fr-fr", timelimit="d", max_results=6))
                
                if results:
                    col_ia, col_news = st.columns([1, 1.2])
                    
                    with col_ia:
                        st.markdown("**Synthèse Stratégique Pyxis :**")
                        analyse = generer_analyse(sujet, results)
                        st.info(analyse)
                    
                    with col_news:
                        st.markdown("**Sources recommandées :**")
                        for art in results[:3]: # Affiche les 3 meilleurs articles
                            st.markdown(f"""
                                <div class="article-card">
                                    <a href="{art['url']}" target="_blank" style="text-decoration:none;">
                                        <b>{art['title']}</b>
                                    </a><br>
                                    <small>{art['source']} • {art['date']}</small>
                                </div>
                            """, unsafe_allow_html=True)
                else:
                    st.write("Aucune actualité critique détectée ces dernières 24h.")

# --- FIN DU CODE ---
