import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Veille Pyxis Support", page_icon="⚖️", layout="wide")

# --- 2. CONNEXION IA (GEMINI) ---
API_KEY = st.secrets.get("API_KEY", "")

def initialiser_ia():
    if not API_KEY: return None
    try:
        genai.configure(api_key=API_KEY)
        # Configuration avec tolérance maximale pour éviter les blocages de réponse
        return genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
        )
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

# --- 4. DESIGN HAUT CONTRASTE (FORCE NOIR SUR BLANC) ---
st.markdown("""
    <style>
        /* Fond global */
        .stApp { background-color: #FFFFFF !important; }
        
        /* Titre Principal forcé en Noir pur */
        .titre-noir {
            color: #000000 !important;
            text-align: center;
            font-size: 2.5em;
            font-weight: 800;
            margin-bottom: 30px;
            display: block;
        }

        /* Barre latérale - Contraste maximum */
        [data-testid="stSidebar"] {
            background-color: #F0F2F6 !important;
            border-right: 2px solid #000;
        }
        [data-testid="stSidebar"] * {
            color: #000000 !important;
            font-weight: 700 !important;
        }
        
        /* Texte des articles et titres de sections */
        h1, h2, h3, p, span, li {
            color: #000000 !important;
        }

        /* Cartes d'articles */
        .article-card {
            background-color: #ffffff;
            padding: 15px;
            border: 2px solid #EEEEEE;
            border-left: 8px solid #C5A059;
            border-radius: 10px;
            margin-bottom: 15px;
        }
        
        /* Boutons Noirs */
        div.stButton > button {
            background-color: #000000 !important;
            color: #FFFFFF !important;
            border: 2px solid #000;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# --- 5. LOGIQUE D'ANALYSE ---
def generer_analyse(sujet, articles):
    if not model: return "⚠️ IA non connectée (Vérifiez la clé API)."
    
    titres = "\n".join([f"- {a['title']}" for a in articles[:3]])
    prompt = f"Expert Pyxis Support : Analyse ces titres pour '{sujet}' (Infrastructures, IT, Marchés publics). Rejette le Canada. Donne 2 points clés courts.\n\n{titres}"
    
    try:
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text
        return "Analyse en attente (Contenu filtré par Google)."
    except Exception as e:
        return f"IA indisponible : {str(e)[:50]}"

# --- 6. INTERFACE ---
with st.sidebar:
    st.markdown("<h2 style='color:#00A3C1;'>PYXIS</h2><p>Support</p>", unsafe_allow_html=True)
    st.write("---")
    st.subheader("⚙️ Configuration")
    nouveau = st.text_input("Ajouter un mot-clé :", key="add_input")
    if st.button("Ajouter +"):
        if nouveau and nouveau not in st.session_state['mes_sujets']:
            st.session_state['mes_sujets'].append(nouveau); st.rerun()
    st.write("---")
    for s in st.session_state['mes_sujets']:
        c1, c2 = st.columns([5, 1])
        c1.write(s)
        if c2.button("X", key=f"del_{s}"):
            st.session_state['mes_sujets'].remove(s); st.rerun()

# Utilisation d'une classe CSS spécifique pour le titre
st.markdown("<span class='titre-noir'>Veille Stratégique Opérationnelle</span>", unsafe_allow_html=True)

if st.button("LANCER L'ANALYSE GLOBALE 🚀", use_container_width=True):
    with DDGS() as ddgs:
        for sujet in st.session_state['mes_sujets']:
            st.markdown(f"<h2 style='color:black;'>📌 {sujet}</h2>", unsafe_allow_html=True)
            
            # Délai pour éviter le blocage DuckDuckGo
            time.sleep(2)
            
            try:
                results = list(ddgs.news(sujet, region="fr-fr", timelimit="d", max_results=4))
                if results:
                    col1, col2 = st.columns([1, 1.2])
                    with col1:
                        st.markdown("<b style='color:black;'>Synthèse Pyxis :</b>", unsafe_allow_html=True)
                        st.info(generer_analyse(sujet, results))
                    with col2:
                        for art in results[:3]:
                            st.markdown(f"""
                                <div class="article-card">
                                    <a href="{art['url']}" target="_blank" style="text-decoration:none; color:#000;">
                                        <b>{art['title']}</b>
                                    </a><br>
                                    <small style="color:#666;">{art['source']}</small>
                                </div>
                            """, unsafe_allow_html=True)
                else:
                    st.write("Aucune actualité détectée ce jour.")
            except:
                st.error("Recherche saturée. Attendez 30 secondes.")
                break
