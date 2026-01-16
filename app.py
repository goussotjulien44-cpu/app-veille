import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai
import time

# --- 1. CONFIGURATION IA ---
if "API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("ERREUR : Clé 'API_KEY' manquante.")

st.set_page_config(page_title="Veille Pyxis Support", layout="wide")

# --- 2. DESIGN ---
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
        [data-testid="stSidebar"] { background-color: #F0F2F6 !important; border-right: 2px solid #000; }
        [data-testid="stSidebar"] * { color: #000000 !important; font-weight: 700 !important; }
        div.stButton > button:first-child {
            background-color: #F0F2F6 !important;
            color: #000000 !important;
            border: 1px solid #000000 !important;
            font-weight: bold !important;
        }
        .titre-service { color: #000; font-weight: 900; font-size: 18px; border-bottom: 3px solid #C5A059; margin-top: 20px; }
        .article-card { background-color: #fdfdfd; padding: 10px; border: 1px solid #ddd; border-left: 6px solid #C5A059; border-radius: 5px; margin-bottom: 8px; }
        .analyse-box { background-color: #E3F2FD; border: 1px solid #2196F3; padding: 15px; border-radius: 8px; color: #1976D2; }
    </style>
""", unsafe_allow_html=True)

# --- 3. MOTEUR IA ---
def traiter_ia_expert(liste_brute, service):
    if not liste_brute: return [], "Aucune actualité détectée."
    titres_concat = "\n".join([f"- {a['title']} (URL: {a['url']})" for a in liste_brute])
    prompt = f"Trie ces articles pour {service}. Supprime les doublons. Garde les 4 plus stratégiques (URLs seules) :\n{titres_concat}"
    try:
        response = model.generate_content(prompt).text
        urls_uniques = [u.strip() for u in response.strip().split("\n") if "http" in u]
        return [a for a in liste_brute if a['url'] in urls_uniques][:4], "Fonctionnalité IA en cours de développement."
    except:
        return liste_brute[:4], "Fonctionnalité IA en cours de développement."

# --- 4. INITIALISATION ---
if 'sujets' not in st.session_state:
    st.session_state['sujets'] = [
        "Mobilités (Ferroviaire & Aéroportuaire)", "Externalisation (Marchés Publics & AMO)",
        "IT & Systèmes d'Information", "Digitalisation & IA",
        "Vente SaaS & Commerciaux MA-IA", "Développement Software", "Administration, RH & DAF"
    ]

with st.sidebar:
    st.markdown("### ⚖️ PYXIS SUPPORT")
    for s in st.session_state['sujets']:
        c1, c2 = st.columns([5, 1.2])
        c1.write(s)
        if c2.button("X", key=f"d_{s}"):
            st.session_state['sujets'].remove(s); st.rerun()

st.markdown('<h1 style="text-align:center;">Veille Stratégique Opérationnelle</h1>', unsafe_allow_html=True)

# --- 5. EXECUTION AVEC PAUSE DE SÉCURITÉ ---
if st.button("LANCER LA VEILLE INTELLIGENTE 🚀", use_container_width=True):
    for sujet in st.session_state['sujets']:
        st.markdown(f'<div class="titre-service">📌 {sujet}</div>', unsafe_allow_html=True)
        
        try:
            with st.spinner(f"Recherche en cours pour {sujet}..."):
                with DDGS() as ddgs:
                    # On nettoie un peu le terme de recherche pour éviter les erreurs
                    search_query = sujet.split('(')[0].strip()
                    raw = list(ddgs.news(search_query, region="fr-fr", timelimit="w", max_results=15))
                
                # PAUSE CRITIQUE : on attend que DuckDuckGo "oublie" la requête précédente
                time.sleep(2.0) 
            
            actus, message_ia = traiter_ia_expert(raw, sujet)
            col1, col2 = st.columns([1, 1.4])
            with col1:
                st.markdown(f'<div class="analyse-box">💡 <b>Analyse IA :</b><br>{message_ia}</div>', unsafe_allow_html=True)
            with col2:
                for a in actus:
                    st.markdown(f'<div class="article-card"><a href="{a["url"]}" target="_blank" style="text-decoration:none; color:black;"><b>{a["title"]}</b></a><br><small>{a["source"]}</small></div>', unsafe_allow_html=True)
        
        except Exception as e:
            if "Ratelimit" in str(e):
                st.warning(f"⚠️ DuckDuckGo limite temporairement les accès. Pause de 5s...")
                time.sleep(5.0)
            else:
                st.error(f"Flux interrompu pour {sujet}. Réessayez dans un instant.")
