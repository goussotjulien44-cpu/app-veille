import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Veille Pyxis Support", page_icon="⚖️", layout="wide")

# --- 2. CONNEXION IA (GEMINI) ---
API_KEY = st.secrets.get("API_KEY", "")

def initialiser_ia():
    if not API_KEY:
        return None
    try:
        genai.configure(api_key=API_KEY)
        # On cherche dynamiquement un modèle disponible (Flash ou Pro)
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'gemini-1.5-flash' in m.name or 'gemini-pro' in m.name:
                    return genai.GenerativeModel(m.name)
        return None
    except Exception:
        return None

model = initialiser_ia()

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

# --- 4. DESIGN PERSONNALISÉ ---
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF !important; }
        
        /* Sidebar : Forcer le Noir sur Gris Clair */
        [data-testid="stSidebar"] {
            background-color: #F1F3F6 !important;
            border-right: 1px solid #DDD;
        }
        [data-testid="stSidebar"] * {
            color: #000000 !important;
            font-weight: 600 !important;
        }
        
        h1, h2, h3 { color: #000000 !important; }

        /* Cartes d'articles style Pyxis */
        .article-card {
            background-color: #ffffff;
            padding: 15px;
            border: 1px solid #EEE;
            border-left: 6px solid #C5A059;
            border-radius: 8px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
            margin-bottom: 15px;
        }
        
        /* Boutons Noirs */
        div.stButton > button {
            background-color: #000000 !important;
            color: #FFFFFF !important;
            width: 100%;
            border: none;
        }
    </style>
""", unsafe_allow_html=True)

# --- 5. LOGIQUE D'ANALYSE ---
def generer_analyse(sujet, articles):
    if not model:
        return "⚠️ L'IA n'est pas encore connectée. Vérifiez votre clé API dans les Secrets."
    
    titres = "\n".join([f"- {a['title']}" for a in articles[:4]])
    prompt = f"""Expert Pyxis Support : Analyse l'intérêt de ces actus pour la division '{sujet}'.
    Contexte : Infrastructures (ferroviaire, portuaire), IT complexe, Marchés publics.
    Action : 2 points clés stratégiques. Exclus Canada/Alimentaire.
    
    Titres:
    {titres}"""
    
    try:
        response = model.generate_content(prompt)
        return response.text if response.text else "Analyse indisponible pour ces sources."
    except Exception as e:
        # Si erreur, on affiche un message propre
        return "Synthèse en cours de calcul... (L'IA se synchronise)"

# --- 6. INTERFACE ---
with st.sidebar:
    st.markdown("<h2 style='color:#00A3C1; margin-bottom:0;'>PYXIS</h2><h4 style='color:#777; margin-top:0;'>Support</h4>", unsafe_allow_html=True)
    st.write("---")
    nouveau = st.text_input("Ajouter un mot-clé :")
    if st.button("Ajouter +"):
        if nouveau and nouveau not in st.session_state['mes_sujets']:
            st.session_state['mes_sujets'].append(nouveau); st.rerun()
    st.write("---")
    for s in st.session_state['mes_sujets']:
        c1, c2 = st.columns([5, 1])
        c1.write(s)
        if c2.button("X", key=f"del_{s}"):
            st.session_state['mes_sujets'].remove(s); st.rerun()

st.markdown("<h1 style='text-align:center;'>Veille Stratégique Opérationnelle</h1>", unsafe_allow_html=True)

if st.button("LANCER L'ANALYSE INTELLIGENTE 🚀", use_container_width=True):
    with DDGS() as ddgs:
        for sujet in st.session_state['mes_sujets']:
            st.write("---")
            st.subheader(f"📌 {sujet}")
            with st.spinner("Recherche..."):
                results = list(ddgs.news(sujet, region="fr-fr", timelimit="d", max_results=5))
                if results:
                    col1, col2 = st.columns([1, 1.2])
                    with col1:
                        st.markdown("**Synthèse Pyxis :**")
                        st.info(generer_analyse(sujet, results))
                    with col2:
                        for art in results[:3]:
                            st.markdown(f"""
                                <div class='article-card'>
                                    <a href='{art['url']}' target='_blank' style='text-decoration:none; color:#000;'>
                                        <b>{art['title']}</b>
                                    </a><br>
                                    <small>{art['source']}</small>
                                </div>
                            """, unsafe_allow_html=True)
                else:
                    st.write("Aucune actualité détectée pour cette division.")
