import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai

# --- CONFIGURATION ---
st.set_page_config(page_title="Veille Stratégique Pyxis", page_icon="⚖️", layout="wide")

# --- CLE API GEMINI (Sécurisée) ---
# On essaie de récupérer la clé dans les secrets, sinon on met une valeur vide
API_KEY = st.secrets.get("API_KEY", "")

if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.warning("⚠️ Clé API manquante. L'analyse IA est désactivée. Ajoutez 'API_KEY' dans les Secrets de Streamlit.")

# --- INITIALISATION DES DIVISIONS ---
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

# --- DESIGN HAUT CONTRASTE (MA-IA Style) ---
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF; }
        h1, h2, h3, p, span, label { color: #000000 !important; font-family: 'Segoe UI', sans-serif; }
        .main-title { text-align: center; font-weight: 800; font-size: 2.5em; margin-bottom: 20px; color: #000 !important; }
        .article-card {
            background-color: #ffffff; padding: 18px; border: 1px solid #EEE;
            border-top: 5px solid #C5A059; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 15px;
        }
        div.stButton > button { background-color: #000 !important; color: #fff !important; font-weight: bold; width: 100%; border: none; }
    </style>
""", unsafe_allow_html=True)

# --- LOGIQUE IA ---
def analyser_ia(sujet, articles):
    if not API_KEY: return "Analyse IA indisponible (Clé manquante)."
    if not articles: return "Aucun article trouvé."
    
    txt = "\n".join([f"- {a['title']} (Source: {a['source']})" for a in articles])
    prompt = f"""
    Tu es l'expert stratégique de Pyxis Support (AMO Marchés Publics, IT, Mobilités).
    Analyse pour la division : {sujet}.
    TACHE : Sélectionne les 4 articles les plus critiques pour Pyxis Support.
    FILTRE : Rejette strictement le Canada, le Québec et les marchés alimentaires.
    RÉPONSE : Une liste avec le titre et l'intérêt stratégique pour Pyxis.
    ARTICLES : {txt}
    """
    try:
        return model.generate_content(prompt).text
    except Exception as e:
        return f"Erreur IA : {str(e)}"

# --- INTERFACE ---
with st.sidebar:
    # Logo Pyxis texte (pour éviter les erreurs de chargement d'image)
    st.markdown("<div style='color:#00A3C1; font-size:24px; font-weight:bold; line-height:1.1;'>PYXIS<br><span style='color:#777; font-size:18px;'>Support</span></div>", unsafe_allow_html=True)
    st.write("---")
    st.subheader("⚙️ Configuration")
    nouveau = st.text_input("Ajouter un mot-clé :")
    if st.button("Ajouter +"):
        if nouveau and nouveau not in st.session_state['mes_sujets']:
            st.session_state['mes_sujets'].append(nouveau)
            st.rerun()
    st.write("---")
    st.subheader("📍 Divisions actives")
    for s in st.session_state['mes_sujets']:
        c1, c2 = st.columns([5,1])
        c1.markdown(f"<span style='color:black;'>• {s}</span>", unsafe_allow_html=True)
        if c2.button("X", key=s):
            st.session_state['mes_sujets'].remove(s)
            st.rerun()

st.markdown("<h1 class='main-title'>Veille Stratégique Opérationnelle</h1>", unsafe_allow_html=True)

if st.button("LANCER L'ANALYSE DES DIVISIONS 🚀"):
    with DDGS() as ddgs:
        for sujet in st.session_state['mes_sujets']:
            st.markdown(f"### 📌 {sujet}")
            with st.spinner("Analyse intelligente en cours..."):
                raw = list(ddgs.news(sujet, region="fr-fr", timelimit="d", max_results=8))
                if raw:
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.markdown("**Synthèse Stratégique :**")
                        st.info(analyser_ia(sujet, raw))
                    with col2:
                        st.markdown("**Sources recommandées :**")
                        for a in raw[:4]:
                            st.markdown(f"""
                                <div class='article-card'>
                                    <a href='{a['url']}' target='_blank' style='text-decoration:none; color:#000;'>
                                        <b>{a['title']}</b>
                                    </a><br>
                                    <small style='color:#C5A059;'>{a['source']} • {a['date']}</small>
                                </div>
                            """, unsafe_allow_html=True)
                else:
                    st.write("Pas d'actualité pertinente aujourd'hui.")
