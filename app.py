import streamlit as st
from duckduckgo_search import DDGS
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Veille Pyxis Support", page_icon="⚖️", layout="wide")

# --- 2. DICTIONNAIRE DE RECHERCHE ULTRA-CIBLÉE ---
MOTS_CLES_EXPERTS = {
    "Mobilités (Ferroviaire & Aéroportuaire)": "(SNCF OR RATP OR RER OR SYSTRA OR EGIS OR 'PYXIS SUPPORT') AND (ferroviaire OR train OR métro OR aéroport)",
    "Externalisation (Marchés Publics & AMO)": "(BOAMP OR 'Marchés Publics' OR 'Conseil d'Etat' OR 'Droit de la commande publique') -'centre-ville' -'police'",
    "IT & Systèmes d'Information": "('Gouvernance SI' OR 'Cloud souverain' OR 'Schéma directeur informatique')",
    "Digitalisation & IA": "('Transformation digitale' OR 'IA générative' OR RPA) AND entreprise",
    "Vente SaaS & Commerciaux MA-IA": "('SaaS France' OR 'Éditeur de logiciel') AND (croissance OR marché)",
    "Développement Software": "('DevOps' OR 'Méthodes Agiles' OR 'Cybersécurité applicative')",
    "Administration, RH & DAF": "('Droit social' OR 'Réforme fiscale' OR 'Facturation électronique 2026')"
}

# --- 3. SOURCES PRIORITAIRES ---
SOURCES_GENERALISTES = ["lagazettedescommunes.com", "achatpublic.info", "village-justice.com", "lemoniteur.fr", "economie.gouv.fr/daj"]

# --- 4. DESIGN ANTI-INVISIBILITÉ (FORÇAGE NOIR/GRIS) ---
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF !important; }
        
        /* Sidebar : Forçage Noir Total */
        [data-testid="stSidebar"] { background-color: #F0F2F6 !important; border-right: 3px solid #000; }
        [data-testid="stSidebar"] * { color: #000000 !important; font-weight: 800 !important; }
        
        /* Correction des cases de saisie et boutons invisibles */
        [data-testid="stSidebar"] input { background-color: #FFFFFF !important; border: 1px solid #000 !important; color: #000 !important; }
        
        /* Boutons de suppression (X) : Fond gris, Croix Noire Épaisse */
        div[data-testid="stSidebar"] button {
            background-color: #DDE1E7 !important;
            color: #000000 !important;
            border: 2px solid #000000 !important;
            font-size: 16px !important;
            min-width: 35px !important;
        }

        .article-card {
            background-color: #ffffff; padding: 15px; border: 1px solid #000;
            border-left: 10px solid #C5A059; border-radius: 8px; margin-bottom: 12px;
        }
        
        h1, h2, h3 { color: #000000 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 5. LOGIQUE DE RECHERCHE ---
def effectuer_recherche(service_name):
    query = MOTS_CLES_EXPERTS.get(service_name, service_name)
    resultats = []
    with DDGS() as ddgs:
        # On cherche d'abord dans nos 5 sites de référence
        for site in SOURCES_GENERALISTES:
            try:
                search = list(ddgs.news(f"{query} site:{site}", region="fr-fr", timelimit="d", max_results=1))
                if search: resultats.extend(search)
            except: continue
        
        # Si pas assez de résultats "experts", on élargit
        if len(resultats) < 2:
            try:
                web = list(ddgs.news(query, region="fr-fr", timelimit="d", max_results=3))
                resultats.extend(web)
            except: pass
    return resultats[:4]

# --- 6. INTERFACE ---
if 'sujets' not in st.session_state:
    st.session_state['sujets'] = list(MOTS_CLES_EXPERTS.keys())

with st.sidebar:
    st.markdown("## PYXIS SUPPORT")
    st.write("---")
    nouveau = st.text_input("Ajouter un mot-clé :", key="add_input")
    if st.button("AJOUTER +"):
        if nouveau and nouveau not in st.session_state['sujets']:
            st.session_state['sujets'].append(nouveau); st.rerun()
    st.write("---")
    st.markdown("### Gérer l'affichage")
    for s in st.session_state['sujets']:
        col_txt, col_del = st.columns([4, 1.5])
        col_txt.write(f"**{s}**")
        if col_del.button("X", key=f"del_{s}"):
            st.session_state['sujets'].remove(s); st.rerun()

st.markdown("<h1 style='text-align:center;'>Veille Stratégique Opérationnelle</h1>", unsafe_allow_html=True)

if st.button("LANCER LA RECHERCHE EXPERTE 🚀", use_container_width=True):
    for sujet in st.session_state['sujets']:
        st.markdown(f"### 📌 {sujet}")
        with st.spinner(f"Filtrage juridique et technique pour {sujet}..."):
            actus = effectuer_recherche(sujet)
            if actus:
                c1, c2 = st.columns([1, 1.5])
                with c1:
                    st.info("💡 Analyse IA en attente de clé API.")
                with c2:
                    for a in actus:
                        st.markdown(f"""<div class="article-card">
                            <a href="{a['url']}" target="_blank" style="text-decoration:none; color:black;"><b>{a['title']}</b></a><br>
                            <small>Source : {a['source']} | Date : {a['date']}</small></div>""", unsafe_allow_html=True)
            else:
                st.write("Aucune actualité pertinente aujourd'hui.")
