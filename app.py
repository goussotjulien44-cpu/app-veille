import streamlit as st
from duckduckgo_search import DDGS
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Veille Pyxis Support", page_icon="⚖️", layout="wide")

# --- 2. DICTIONNAIRE DES MOTS-CLÉS ÉLARGIS ---
MOTS_CLES_EXPERTS = {
    "Mobilités (Ferroviaire & Aéroportuaire)": "SNCF OR RATP OR RER OR SYSTRA OR EGIS OR 'PYXIS SUPPORT' OR 'trains régionaux' OR train OR métro OR tramway OR avions OR aéroport",
    "Externalisation (Marchés Publics & AMO)": "BOAMP OR PLACE OR 'marchés publics' OR 'profil acheteur' OR 'Conseil d'Etat' OR consultations OR AMO OR 'commande publique'",
    "IT & Systèmes d'Information": "Gouvernance SI OR 'Schéma directeur informatique' OR 'Cloud souverain' OR Infogérance OR ERP",
    "Digitalisation & IA": "Transformation digitale OR 'IA générative' OR RPA OR Dématérialisation OR Data",
    "Vente SaaS & Commerciaux MA-IA": "SaaS France OR 'Logiciel en tant que service' OR 'Business Development IA'",
    "Développement Software": "DevOps OR 'Méthodes Agiles' OR 'Cybersécurité applicative' OR API",
    "Administration, RH & DAF": "RH OR 'Droit social' OR 'direction administrative et financière' OR impôt OR 'droit du travail'"
}

# --- 3. SOURCES PRIVILÉGIÉES ---
SOURCES_MOBILITES = ["espacetrain.com", "lerail.com", "laviedurail.com", "ville-rail-transports.com", "usinenouvelle.com"]
SOURCES_GENERALISTES = ["lagazettedescommunes.com", "achatpublic.info", "village-justice.com", "lemoniteur.fr", "economie.gouv.fr/daj"]

# --- 4. DESIGN & VISIBILITÉ ---
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF !important; }
        
        /* Sidebar : Correction visuelle complète */
        [data-testid="stSidebar"] { background-color: #F8F9FB !important; border-right: 2px solid #000; }
        [data-testid="stSidebar"] * { color: #000000 !important; font-weight: 700 !important; }
        
        /* Boutons de suppression (X) : Gris clair avec croix noire visible */
        div[data-testid="stSidebar"] button {
            background-color: #EEEEEE !important;
            color: #000000 !important;
            border: 1px solid #000000 !important;
            font-size: 14px !important;
            padding: 2px 10px !important;
        }
        
        .article-card {
            background-color: #ffffff; padding: 15px; border: 1px solid #DDD;
            border-left: 8px solid #C5A059; border-radius: 8px; margin-bottom: 12px;
        }
        
        div.stButton > button:first-child {
            background-color: #000000 !important; color: #FFFFFF !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- 5. LOGIQUE DE RECHERCHE OPTIMISÉE ---
def effectuer_recherche(service_name):
    query = MOTS_CLES_EXPERTS.get(service_name, service_name)
    resultats = []
    
    with DDGS() as ddgs:
        # Étape 1 : Recherche sur les sources expertes
        sources = SOURCES_MOBILITES + SOURCES_GENERALISTES if "Mobilités" in service_name else SOURCES_GENERALISTES
        for site in sources[:3]:
            try:
                search = list(ddgs.news(f"{query} site:{site}", region="fr-fr", timelimit="d", max_results=1))
                if search: resultats.extend(search)
            except: continue
        
        # Étape 2 : Recherche Web Globale pour ne rien rater
        try:
            general = list(ddgs.news(query, region="fr-fr", timelimit="d", max_results=5))
            if general: resultats.extend(general)
        except: pass
            
    # Dédoublonnage
    seen = set()
    return [x for x in resultats if not (x['url'] in seen or seen.add(x['url']))][:5]

# --- 6. INTERFACE ---
if 'sujets' not in st.session_state:
    st.session_state['sujets'] = list(MOTS_CLES_EXPERTS.keys())

with st.sidebar:
    st.markdown("<h2>PYXIS</h2>", unsafe_allow_html=True)
    st.write("---")
    nouveau = st.text_input("Ajouter un mot-clé :", key="add_input")
    if st.button("Ajouter +"):
        if nouveau and nouveau not in st.session_state['sujets']:
            st.session_state['sujets'].append(nouveau); st.rerun()
    st.write("---")
    for s in st.session_state['sujets']:
        col_txt, col_del = st.columns([4, 1])
        col_txt.write(f"• {s}")
        if col_del.button("X", key=f"del_{s}"):
            st.session_state['sujets'].remove(s); st.rerun()

st.markdown("<h1 style='text-align:center; color:black;'>Veille Stratégique Opérationnelle</h1>", unsafe_allow_html=True)

if st.button("DÉMARRER LA VEILLE EXPERTE 🚀", use_container_width=True):
    for sujet in st.session_state['sujets']:
        st.markdown(f"<h3 style='color:black; border-bottom: 2px solid #C5A059;'>📌 {sujet}</h3>", unsafe_allow_html=True)
        with st.spinner(f"Scan des sources pour {sujet}..."):
            time.sleep(1.5)
            actus = effectuer_recherche(sujet)
            if actus:
                c1, c2 = st.columns([1, 1.2])
                with c1:
                    st.info("💡 Analyse IA : Fonctionnalité en développement.")
                with c2:
                    for a in actus:
                        st.markdown(f"""<div class="article-card">
                            <a href="{a['url']}" target="_blank" style="text-decoration:none; color:black;"><b>{a['title']}</b></a><br>
                            <small>{a['source']} • {a['date']}</small></div>""", unsafe_allow_html=True)
            else:
                st.write("Aucune actualité détectée ce jour.")
