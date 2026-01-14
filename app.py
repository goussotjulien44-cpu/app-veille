import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Veille Pyxis Support", page_icon="⚖️", layout="wide")

# --- 2. CONNEXION IA ROBUSTE ---
API_KEY = st.secrets.get("API_KEY", "")

def initialiser_ia():
    if not API_KEY: return None
    try:
        genai.configure(api_key=API_KEY)
        # On demande à Google quel modèle est réellement disponible pour éviter la 404
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else 'models/gemini-pro'
        return genai.GenerativeModel(target_model)
    except: return None

model = initialiser_ia()

# --- 3. DIVISIONS PYXIS ---
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

# --- 4. DESIGN "ZERO TRANSPARENCE" (HAUT CONTRASTE) ---
st.markdown("""
    <style>
        /* Fond global forcé en blanc */
        .stApp { background-color: #FFFFFF !important; }
        
        /* Titre Principal : Noir Pur, 100% Opaque */
        .titre-pyxis {
            color: #000000 !important;
            font-size: 42px !important;
            font-weight: 900 !important;
            text-align: center;
            display: block;
            padding: 20px 0;
            opacity: 1 !important;
        }

        /* Barre latérale : Forçage Noir sur Gris */
        [data-testid="stSidebar"] {
            background-color: #F1F3F6 !important;
            border-right: 3px solid #000000;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, 
        [data-testid="stSidebar"] span, 
        [data-testid="stSidebar"] label {
            color: #000000 !important;
            font-weight: 800 !important;
            opacity: 1 !important;
        }
        
        /* Forçage de tous les titres de sections en noir */
        h1, h2, h3, b, strong {
            color: #000000 !important;
            opacity: 1 !important;
        }

        /* Cartes d'articles avec bordures visibles */
        .article-card {
            background-color: #ffffff !important;
            padding: 20px;
            border: 2px solid #000000 !important;
            border-left: 10px solid #C5A059 !important;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        .article-card b { font-size: 1.2em; }

        /* Boutons Noirs Pleine Opacité */
        div.stButton > button {
            background-color: #000000 !important;
            color: #FFFFFF !important;
            border: 2px solid #000000 !important;
            opacity: 1 !important;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# --- 5. LOGIQUE D'ANALYSE ---
def generer_analyse(sujet, articles):
    if not model: return "⚠️ IA non connectée."
    titres = "\n".join([f"- {a['title']}" for a in articles[:3]])
    prompt = f"Expert Pyxis : Analyse ces titres pour '{sujet}'. Sois pro et concis (3 lignes). Rejette le Canada.\n\n{titres}"
    try:
        response = model.generate_content(prompt)
        return response.text if response.text else "Analyse en attente."
    except Exception as e:
        return f"Calcul en cours... (Synchro IA)"

# --- 6. INTERFACE ---
with st.sidebar:
    st.markdown("<h1 style='color:#00A3C1 !important;'>PYXIS</h1>", unsafe_allow_html=True)
    st.write("---")
    nouveau = st.text_input("Ajouter un mot-clé :", key="new_topic_input")
    if st.button("Ajouter à la liste"):
        if nouveau and nouveau not in st.session_state['mes_sujets']:
            st.session_state['mes_sujets'].append(nouveau); st.rerun()
    st.write("---")
    for s in st.session_state['mes_sujets']:
        c1, c2 = st.columns([5, 1])
        c1.write(f"**{s}**")
        if c2.button("X", key=f"del_{s}"):
            st.session_state['mes_sujets'].remove(s); st.rerun()

# Affichage du titre principal avec la classe "titre-pyxis"
st.markdown('<span class="titre-pyxis">Veille Stratégique Opérationnelle</span>', unsafe_allow_html=True)

if st.button("DÉMARRER LA VEILLE INTELLIGENTE 🚀", use_container_width=True):
    with DDGS() as ddgs:
        for sujet in st.session_state['mes_sujets']:
            st.markdown(f"<h2 style='border-bottom: 2px solid black; padding-top:20px;'>📌 {sujet}</h2>", unsafe_allow_html=True)
            
            # Pause de sécurité pour éviter le bannissement DuckDuckGo
            time.sleep(2)
            
            try:
                results = list(ddgs.news(sujet, region="fr-fr", timelimit="d", max_results=4))
                if results:
                    col1, col2 = st.columns([1, 1.2])
                    with col1:
                        st.markdown("<b style='font-size:1.1em;'>Analyse Pyxis Support :</b>", unsafe_allow_html=True)
                        st.info(generer_analyse(sujet, results))
                    with col2:
                        for art in results[:3]:
                            st.markdown(f"""
                                <div class="article-card">
                                    <a href="{art['url']}" target="_blank" style="text-decoration:none; color:#000000 !important;">
                                        <b>{art['title']}</b>
                                    </a><br>
                                    <small style="color:#444 !important;">Source : {art['source']}</small>
                                </div>
                            """, unsafe_allow_html=True)
                else:
                    st.write("Rien de nouveau aujourd'hui sur ce sujet.")
            except:
                st.error("Trop de requêtes. Veuillez patienter 1 minute.")
                break
