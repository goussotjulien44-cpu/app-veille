import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai

# --- CONFIGURATION INITIALE ---
st.set_page_config(page_title="Veille Pyxis Support", page_icon="⚖️", layout="wide")

# --- CONNEXION IA (Utilise le Secret que vous avez enregistré) ---
API_KEY = st.secrets.get("API_KEY", "")

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        ia_active = True
    except:
        ia_active = False
else:
    ia_active = False

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

# --- DESIGN "CONTRASTE PYXIS" ---
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF !important; }
        
        /* Sidebar : Texte NOIR sur fond GRIS CLAIR pour lisibilité totale */
        [data-testid="stSidebar"] {
            background-color: #F0F2F6 !important;
            border-right: 1px solid #DDD;
        }
        [data-testid="stSidebar"] * {
            color: #000000 !important;
            font-weight: 500 !important;
        }
        
        /* Titre et Titres de Sections en Noir pur */
        h1, h2, h3 { color: #000000 !important; font-weight: 700 !important; }

        /* Cartes d'articles */
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
            border: none;
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# --- LOGIQUE IA ---
def analyser_ia(sujet, articles):
    if not ia_active:
        return "⚠️ L'IA n'est pas encore activée par la clé API."
    
    txt = "\n".join([f"- {a['title']} (Source: {a['source']})" for a in articles])
    prompt = f"""
    Tu es l'expert stratégique de Pyxis Support. Analyse ces actualités pour la division '{sujet}'.
    Cible : Infrastructures, Marchés Publics français, IT complexe. 
    Action : Sélectionne les 3 points clés et explique pourquoi ils impactent Pyxis.
    Filtre : Exclus le Canada et l'alimentaire.
    Articles : {txt}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Analyse en cours de stabilisation..."

# --- INTERFACE ---
with st.sidebar:
    st.markdown("<h2 style='color:#00A3C1;'>PYXIS</h2><p style='color:#777;'>Support</p>", unsafe_allow_html=True)
    st.write("---")
    st.subheader("⚙️ Configuration")
    nouveau = st.text_input("Ajouter un mot-clé :")
    if st.button("Ajouter +"):
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

st.markdown("<h1 style='text-align:center;'>Veille Stratégique Opérationnelle</h1>", unsafe_allow_html=True)

if st.button("LANCER L'ANALYSE INTELLIGENTE 🚀"):
    with DDGS() as ddgs:
        for sujet in st.session_state['mes_sujets']:
            st.markdown(f"### 📌 {sujet}")
            with st.spinner(f"Analyse Pyxis pour {sujet}..."):
                raw = list(ddgs.news(sujet, region="fr-fr", timelimit="d", max_results=6))
                if raw:
                    col1, col2 = st.columns([1, 1.2])
                    with col1:
                        st.markdown("**Analyse de l'IA :**")
                        st.info(analyser_ia(sujet, raw))
                    with col2:
                        for a in raw[:3]:
                            st.markdown(f"""
                                <div class="article-card">
                                    <a href="{a['url']}" target="_blank" style="text-decoration:none; color:#000;">
                                        <b>{a['title']}</b>
                                    </a><br>
                                    <small style="color:#C5A059;">{a['source']} • {a['date']}</small>
                                </div>
                            """, unsafe_allow_html=True)
                else:
                    st.write("Aucune donnée aujourd'hui.")
