import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai
import time

# --- 1. CONFIGURATION IA ---
if "API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["API_KEY"])
    # CONFIGURATION STRICTE : Température à 0 pour supprimer toute "créativité" de tri
    generation_config = {"temperature": 0.0, "top_p": 1, "top_k": 1}
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config=generation_config)
else:
    st.error("ERREUR : Clé 'API_KEY' manquante dans les Secrets Streamlit.")

st.set_page_config(page_title="Veille Pyxis Support", layout="wide")

# --- 2. DICTIONNAIRE DE RECHERCHE STRATÉGIQUE ---
MOTS_CLES_STRATEGIQUES = {
    "Mobilités (Ferroviaire & Aéroportuaire)": "SNCF OR RER OR RATP OR 'Loi-cadre' OR 'Loi de programmation' OR 'Financement rail' OR 'Tramway'",
    "Externalisation (Marchés Publics & AMO)": "BOAMP OR 'Marchés publics' OR 'Commande publique' OR 'Conseil d'Etat' OR 'Assistance à maîtrise d'ouvrage' OR AMO",
    "IT & Systèmes d'Information": "'Systèmes d'information' OR 'Infrastructure IT' OR 'Transformation digitale' OR 'Cybersécurité' OR 'Logiciel métier'",
    "Digitalisation & IA": "'Intelligence artificielle' OR 'IA générative' OR 'Digitalisation' OR 'Souveraineté numérique'",
    "Vente SaaS & Commerciaux MA-IA": "'Vente SaaS' OR 'Logiciel par abonnement' OR 'Salesforce' OR 'Solution cloud'",
    "Développement Software": "'Développement logiciel' OR 'DevOps' OR 'Cloud computing' OR 'Logiciel libre'",
    "Administration, RH & DAF": "'Réforme RH' OR 'Gestion administrative' OR 'Finance d'entreprise' OR 'Externalisation RH'"
}

# --- 3. DESIGN ---
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF !important; }
        .main-title { 
            color: #000000 !important; font-size: 35px !important; font-weight: 900 !important; 
            text-align: center !important; margin-bottom: 30px !important; display: block !important;
        }
        [data-testid="stSidebar"] { background-color: #F0F2F6 !important; border-right: 2px solid #000; }
        [data-testid="stSidebar"] * { color: #000000 !important; font-weight: 700 !important; }
        div.stButton > button:first-child {
            background-color: #F0F2F6 !important; color: #000000 !important; border: 1px solid #000000 !important; font-weight: bold !important;
        }
        .titre-service { color: #000; font-weight: 900; font-size: 18px; border-bottom: 3px solid #C5A059; margin-top: 25px; }
        .article-card { background-color: #fdfdfd; padding: 12px; border: 1px solid #ddd; border-left: 8px solid #C5A059; border-radius: 5px; margin-bottom: 8px; }
        .analyse-box { background-color: #E3F2FD; border: 1px solid #2196F3; padding: 15px; border-radius: 8px; color: #1976D2; }
    </style>
""", unsafe_allow_html=True)

# --- 4. MOTEUR IA : ANALYSE PROFONDE (TITRE + CONTENU) ---
def traiter_ia_expert(liste_brute, service):
    if not liste_brute: return [], "Aucune actualité détectée."
    
    # ON INJECTE MAINTENANT LE 'BODY' (EXTRAIT) POUR QUE L'IA VOIT QUE C'EST LA MÊME HISTOIRE
    data_concat = "\n".join([f"ID: {a['url']}\nTITRE: {a['title']}\nEXTRAIT: {a.get('body', '')}\n---" for a in liste_brute])
    
    prompt = f"""
    Tu es un éditeur en chef impitoyable pour le service {service}.
    Ta mission : Éliminer la redondance médiatique.
    
    Règles strictes :
    1. Lis les TITRES et les EXTRAITS.
    2. Si plusieurs articles parlent du même événement (ex: Loi-cadre, Grève, Contrat spécifique), garde UNIQUEMENT l'article qui semble le plus informatif. Jette les autres.
    3. Je préfère avoir 1 seul article pertinent que 4 articles répétitifs.
    4. Ne sélectionne JAMAIS plus de 4 articles.
    
    Données à analyser :
    {data_concat}
    
    Réponds UNIQUEMENT par la liste des IDs (URLs) retenues, une par ligne. Rien d'autre.
    """
    try:
        response = model.generate_content(prompt).text
        urls_uniques = [u.strip() for u in response.strip().split("\n") if "http" in u]
        final_list = [a for a in liste_brute if a['url'] in urls_uniques]
        return final_list[:4], "Fonctionnalité IA en cours de développement."
    except:
        return liste_brute[:4], "Fonctionnalité IA en cours de développement."

# --- 5. INITIALISATION ---
if 'sujets' not in st.session_state:
    st.session_state['sujets'] = list(MOTS_CLES_STRATEGIQUES.keys())

with st.sidebar:
    st.markdown("### ⚖️ PYXIS SUPPORT")
    st.write("---")
    for s in st.session_state['sujets']:
        c1, c2 = st.columns([5, 1.2])
        c1.write(s)
        if c2.button("X", key=f"d_{s}"):
            st.session_state['sujets'].remove(s); st.rerun()

st.markdown('<h1 class="main-title">Veille Stratégique Opérationnelle</h1>', unsafe_allow_html=True)

# --- 6. EXECUTION ---
if st.button("LANCER LA VEILLE INTELLIGENTE 🚀", use_container_width=True):
    for sujet in st.session_state['sujets']:
        st.markdown(f'<div class="titre-service">📌 {sujet}</div>', unsafe_allow_html=True)
        query = MOTS_CLES_STRATEGIQUES.get(sujet, sujet)
        raw = []
        success = False
        
        for attempt in range(2):
            try:
                with st.spinner(f"Analyse approfondie pour {sujet}..."):
                    with DDGS() as ddgs:
                        raw = list(ddgs.news(query, region="fr-fr", timelimit="w", max_results=25))
                    if raw:
                        success = True
                        break
            except:
                if attempt == 0: time.sleep(5)
                continue
        time.sleep(1.8)

        if success:
            actus, message_ia = traiter_ia_expert(raw, sujet)
            col1, col2 = st.columns([1, 1.4])
            with col1:
                st.markdown(f'<div class="analyse-box">💡 <b>Analyse IA :</b><br>{message_ia}</div>', unsafe_allow_html=True)
            with col2:
                if len(actus) == 0:
                    st.info("Aucune actualité majeure unique détectée ce jour.")
                for a in actus:
                    st.markdown(f"""<div class="article-card">
                        <a href="{a['url']}" target="_blank" style="text-decoration:none; color:black;"><b>{a['title']}</b></a><br>
                        <small>{a['source']}</small></div>""", unsafe_allow_html=True)
        else:
            st.error(f"Le flux pour {sujet} est saturé.")
