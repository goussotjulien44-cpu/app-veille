import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai

# --- 1. CONFIGURATION IA ---
if "API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("ERREUR : Clé 'API_KEY' manquante dans les Secrets Streamlit.")

st.set_page_config(page_title="Veille Pyxis Support", layout="wide")

# --- 2. DESIGN FIX (VISIBILITÉ TOTALE) ---
st.markdown("""
    <style>
        /* Force le fond blanc et texte noir partout */
        .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
        
        /* Correction Sidebar (Noir sur Gris) */
        [data-testid="stSidebar"] { background-color: #F0F2F6 !important; border-right: 2px solid #000; }
        [data-testid="stSidebar"] * { color: #000000 !important; font-weight: 700 !important; }
        
        /* Titres et Cartes */
        .main-title { color: #000; font-size: 32px; font-weight: 900; text-align: center; margin-bottom: 20px; }
        .titre-service { color: #000; font-weight: 900; font-size: 18px; border-bottom: 3px solid #C5A059; margin-top: 20px; }
        .article-card { background-color: #fdfdfd; padding: 10px; border: 1px solid #ddd; border-left: 6px solid #C5A059; border-radius: 5px; margin-bottom: 8px; }
        
        /* Bloc Analyse Pyxis */
        .analyse-box { background-color: #FFFDE7; border: 1px solid #FBC02D; padding: 15px; border-radius: 8px; color: #000; }
    </style>
""", unsafe_allow_html=True)

# --- 3. MOTEUR IA FILTRE SÉVÈRE ---
def traiter_ia_expert(liste_brute, service):
    if not liste_brute: return [], "Aucune actualité détectée."
    
    titres_concat = "\n".join([f"- {a['title']} (Source: {a['source']} | URL: {a['url']})" for a in liste_brute])
    
    prompt = f"""
    En tant qu'analyste pour le cabinet Pyxis (spécialiste AMO), examine ces articles pour le service {service}.
    1. FILTRE RADICAL : Ne sélectionne que 4 articles maximum. 
    2. INTERDICTION DE DOUBLONS : Si plusieurs articles parlent de la 'loi-cadre' ou du 'financement rail par autoroutes', n'en garde qu'UN SEUL (le plus complet).
    3. ANALYSE : Rédige une synthèse de 2 phrases sur l'impact de ces actus pour un consultant AMO.
    
    Réponds EXACTEMENT sous ce format :
    ANALYSE: (ton texte)
    URLS:
    (url1)
    (url2)
    """
    
    try:
        response = model.generate_content(prompt).text
        # Extraction de l'analyse et des URLs
        analyse_part = response.split("URLS:")[0].replace("ANALYSE:", "").strip()
        urls_part = response.split("URLS:")[1].strip().split("\n")
        
        final_articles = [a for a in liste_brute if a['url'] in [u.strip() for u in urls_part]]
        return final_articles[:4], analyse_part
    except:
        return liste_brute[:4], "L'IA a rencontré une erreur lors de l'analyse thématique."

# --- 4. INTERFACE ---
if 'sujets' not in st.session_state:
    st.session_state['sujets'] = ["Mobilités (Ferroviaire & Aéroportuaire)", "Externalisation (Marchés Publics & AMO)", "IT & Systèmes d'Information"]

with st.sidebar:
    st.markdown("### ⚖️ PYXIS SUPPORT")
    for s in st.session_state['sujets']:
        c1, c2 = st.columns([5, 1])
        c1.write(s)
        if c2.button("X", key=f"d_{s}"):
            st.session_state['sujets'].remove(s); st.rerun()

st.markdown('<h1 class="main-title">Veille Stratégique Opérationnelle</h1>', unsafe_allow_html=True)

if st.button("LANCER LA VEILLE INTELLIGENTE 🚀", use_container_width=True):
    for sujet in st.session_state['sujets']:
        st.markdown(f'<div class="titre-service">📌 {sujet}</div>', unsafe_allow_html=True)
        with DDGS() as ddgs:
            raw = list(ddgs.news(sujet, region="fr-fr", timelimit="w", max_results=20))
        
        actus, analyse = traiter_ia_expert(raw, sujet)
        
        col1, col2 = st.columns([1, 1.2])
        with col1:
            st.markdown(f'<div class="analyse-box">🎯 <b>Analyse Pyxis :</b><br>{analyse}</div>', unsafe_allow_html=True)
        with col2:
            for a in actus:
                st.markdown(f"""<div class="article-card">
                    <a href="{a['url']}" target="_blank" style="text-decoration:none; color:black;"><b>{a['title']}</b></a><br>
                    <small>{a['source']}</small></div>""", unsafe_allow_html=True)
