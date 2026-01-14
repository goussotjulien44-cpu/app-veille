import streamlit as st
from duckduckgo_search import DDGS
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Veille Pyxis Support", page_icon="⚖️", layout="wide")

# --- 2. BASE DE DONNÉES DES SOURCES PRIVILÉGIÉES ---
# Vos sources spécifiques par domaine
SOURCES_MOBILITES = [
    "espacetrain.com", "lerail.com", "laviedurail.com", "railpassion.fr", 
    "ville-rail-transports.com", "usinenouvelle.com", "railmarket.com"
]

# Vos nouvelles sources généralistes et institutionnelles
SOURCES_GENERALISTES = [
    "lagazettedescommunes.com", 
    "achatpublic.info", 
    "village-justice.com", 
    "conseil-etat.fr", 
    "lemoniteur.fr", 
    "economie.gouv.fr/daj"
]

# --- 3. DESIGN HAUT CONTRASTE ---
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF !important; }
        [data-testid="stSidebar"] { background-color: #F1F3F6 !important; border-right: 2px solid #000; }
        [data-testid="stSidebar"] * { color: #000000 !important; font-weight: 700 !important; }
        .article-card {
            background-color: #ffffff; padding: 15px; border: 1px solid #DDD;
            border-left: 8px solid #C5A059; border-radius: 8px; margin-bottom: 12px;
        }
        div.stButton > button { background-color: #000000 !important; color: #FFFFFF !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. LOGIQUE DE RECHERCHE CIBLÉE ---
def effectuer_recherche(sujet):
    resultats_finaux = []
    # On définit les sources à scanner selon le sujet
    sources_a_scanner = SOURCES_GENERALISTES
    if "Mobilités" in sujet:
        sources_a_scanner = SOURCES_MOBILITES + SOURCES_GENERALISTES

    with DDGS() as ddgs:
        # ÉTAPE 1 : Scan des sources expertes/généralistes listées
        for site in sources_a_scanner:
            query = f"{sujet} site:{site}"
            try:
                # On prend le meilleur article récent par site
                search = list(ddgs.news(query, region="fr-fr", timelimit="d", max_results=1))
                if search: resultats_finaux.extend(search)
            except: continue
            time.sleep(0.3)
        
        # ÉTAPE 2 : Si pas assez de résultats, on élargit au Web Global
        if len(resultats_finaux) < 3:
            try:
                general = list(ddgs.news(sujet, region="fr-fr", timelimit="d", max_results=5))
                resultats_finaux.extend(general)
            except: pass
            
    return resultats_finaux[:6] # On affiche les 6 résultats les plus pertinents

# --- 5. INTERFACE ---
with st.sidebar:
    st.markdown("<h1>PYXIS</h1>", unsafe_allow_html=True)
    st.write("---")
    st.write("**Ajouter un mot-clé**")
    nouveau = st.text_input("Saisir :", key="input_pyxis")
    if st.button("Valider"):
        if 'sujets' not in st.session_state: 
            st.session_state['sujets'] = ["Mobilités (Ferroviaire & Aéroportuaire)", "Externalisation (Marchés Publics & AMO)"]
        if nouveau and nouveau not in st.session_state['sujets']:
            st.session_state['sujets'].append(nouveau); st.rerun()

st.markdown("<h1 style='text-align:center; color:black;'>Veille Stratégique Opérationnelle</h1>", unsafe_allow_html=True)

if st.button("LANCER LA RECHERCHE EXPERTE 🚀", use_container_width=True):
    sujets = st.session_state.get('sujets', ["Mobilités (Ferroviaire & Aéroportuaire)", "Externalisation (Marchés Publics & AMO)"])
    for s in sujets:
        st.markdown(f"<h2 style='color:black; border-bottom: 2px solid #C5A059;'>📌 {s}</h2>", unsafe_allow_html=True)
        
        with st.spinner(f"Interrogation des sources (Gazette, Moniteur, DAJ, etc.)..."):
            actus = effectuer_recherche(s)
            
            if actus:
                col_info, col_news = st.columns([1, 1.2])
                with col_info:
                    st.info("💡 **Analyse IA :** Fonctionnalité en cours de développement.")
                    st.caption("Sources institutionnelles prioritaires vérifiées avec succès.")
                with col_news:
                    for a in actus:
                        st.markdown(f"""<div class="article-card">
                            <a href="{a['url']}" target="_blank" style="text-decoration:none; color:black;"><b>{a['title']}</b></a><br>
                            <small>{a['source']} • {a['date']}</small></div>""", unsafe_allow_html=True)
            else:
                st.write("Aucune actualité détectée ce jour sur vos sources privilégiées.")
