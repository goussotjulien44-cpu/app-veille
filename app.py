import streamlit as st
from duckduckgo_search import DDGS
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Veille Pyxis Support", page_icon="⚖️", layout="wide")

# --- 2. RECADRAGE EXTENSIF (OUVERTURE DES FILTRES) ---
MOTS_CLES_PYXIS = {
    "Mobilités (Ferroviaire & Aéroportuaire)": "SNCF OR RER OR RATP OR SYSTRA OR EGIS OR Tramway OR Métro OR 'Loi-cadre transports' OR Ferroviaire OR Aéroport",
    "Externalisation (Marchés Publics & AMO)": "BOAMP OR PLACE OR 'Marchés publics' OR 'Commande publique' OR 'Conseil d'Etat' OR 'Appel d'offres' OR AMO",
    "IT & Systèmes d'Information": "'Gouvernance SI' OR 'Urbanisation SI' OR 'Schéma Directeur' OR 'Cloud souverain' OR 'DSI'",
    "Digitalisation & IA": "'IA générative' OR 'Transformation digitale' OR RPA OR 'Intelligence Artificielle' OR Dématérialisation",
    "Vente SaaS & Commerciaux MA-IA": "'Éditeur SaaS' OR 'Logiciel SaaS' OR 'Go-to-market' OR 'SaaS France' OR 'Business Development'",
    "Développement Software": "DevOps OR 'Méthodes Agiles' OR 'Qualité logicielle' OR 'Dette technique' OR 'API Management'",
    "Administration, RH & DAF": "RH OR 'Droit social' OR 'Réforme fiscale' OR 'Facturation électronique' OR 'Droit du travail'"
}

# --- 3. DESIGN HAUT CONTRASTE ---
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF !important; }
        [data-testid="stSidebar"] { background-color: #F0F2F6 !important; border-right: 3px solid #000; }
        [data-testid="stSidebar"] * { color: #000000 !important; font-weight: 800 !important; }
        .main-title { color: #000000 !important; font-size: 40px !important; font-weight: 900 !important; text-align: center; }
        .titre-service { color: #000000 !important; font-weight: 900 !important; font-size: 22px; border-bottom: 3px solid #C5A059; margin-top: 20px; }
        div[data-testid="stSidebar"] button { background-color: #E0E0E0 !important; color: #000000 !important; border: 2px solid #000 !important; }
        .article-card { background-color: #ffffff; padding: 15px; border: 1px solid #000; border-left: 10px solid #C5A059; border-radius: 8px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 4. MOTEUR DE RECHERCHE PROFOND ---
def effectuer_recherche(service_label):
    query = MOTS_CLES_PYXIS.get(service_label, service_label)
    resultats = []
    seen_urls = set()
    
    with DDGS() as ddgs:
        try:
            # On scanne 30 résultats (au lieu de 10) pour ne rien rater
            search_results = list(ddgs.news(query, region="fr-fr", timelimit="w", max_results=30))
            
            for art in search_results:
                if art['url'] not in seen_urls:
                    # On exclut quand même les termes parasites très précis pour "Externalisation"
                    if "casino" not in art['title'].lower():
                        resultats.append(art)
                        seen_urls.add(art['url'])
        except:
            pass
            
    return resultats[:5] # On affiche jusqu'à 5 articles par section

# --- 5. INTERFACE ---
if 'sujets' not in st.session_state:
    st.session_state['sujets'] = list(MOTS_CLES_PYXIS.keys())

with st.sidebar:
    st.markdown("## PYXIS SUPPORT")
    st.write("---")
    nouveau = st.text_input("Saisir un mot-clé :", key="new_key")
    if st.button("AJOUTER +"):
        if nouveau and nouveau not in st.session_state['sujets']:
            st.session_state['sujets'].append(nouveau); st.rerun()
    st.write("---")
    for s in st.session_state['sujets']:
        c1, c2 = st.columns([4, 1])
        c1.write(f"**{s}**")
        if c2.button("X", key=f"del_{s}"):
            st.session_state['sujets'].remove(s); st.rerun()

st.markdown('<h1 class="main-title">Veille Stratégique Opérationnelle</h1>', unsafe_allow_html=True)

if st.button("LANCER LA VEILLE GLOBALE 🚀", use_container_width=True):
    for sujet in st.session_state['sujets']:
        st.markdown(f'<div class="titre-service">📌 {sujet}</div>', unsafe_allow_html=True)
        with st.spinner(f"Scan large de l'actualité pour {sujet}..."):
            actus = effectuer_recherche(sujet)
            if actus:
                col_ia, col_news = st.columns([1, 1.4])
                with col_ia:
                    st.info("💡 **Analyse IA :** Fonctionnalité en cours de développement.")
                with col_news:
                    for a in actus:
                        st.markdown(f"""<div class="article-card">
                            <a href="{a['url']}" target="_blank" style="text-decoration:none; color:black;"><b>{a['title']}</b></a><br>
                            <small>Source : {a['source']} | {a['date']}</small></div>""", unsafe_allow_html=True)
            else:
                st.write("*Aucun article trouvé avec les nouveaux filtres.*")
