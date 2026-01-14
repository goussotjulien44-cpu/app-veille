import streamlit as st
from duckduckgo_search import DDGS
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Veille Pyxis Support", page_icon="⚖️", layout="wide")

# --- 2. MOTS-CLÉS AVEC PRIORITÉ STRATÉGIQUE ---
MOTS_CLES_PYXIS = {
    "Mobilités (Ferroviaire & Aéroportuaire)": {
        "prioritaire": "'Loi-cadre' OR 'Loi de programmation' OR 'Réforme ferroviaire' OR 'Investissement transport'",
        "general": "SNCF OR RER OR RATP OR SYSTRA OR EGIS OR Tramway OR Métro OR Aéroport"
    },
    "Externalisation (Marchés Publics & AMO)": {
        "prioritaire": "'Jurisprudence commande publique' OR 'Réforme marchés publics' OR 'Conseil d'Etat'",
        "general": "BOAMP OR PLACE OR 'Appel d'offres' OR AMO"
    },
    # ... (les autres services gardent leur structure simplifiée)
}

# --- 3. DESIGN --- (Identique au précédent pour la visibilité)
st.markdown("""<style>
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #F0F2F6 !important; border-right: 3px solid #000; }
    [data-testid="stSidebar"] * { color: #000000 !important; font-weight: 800 !important; }
    .main-title { color: #000000 !important; font-size: 35px !important; font-weight: 900 !important; text-align: center; }
    .titre-service { color: #000000 !important; font-weight: 900 !important; font-size: 20px; border-bottom: 3px solid #C5A059; margin-top: 20px; }
    .article-card { background-color: #ffffff; padding: 12px; border: 1px solid #000; border-left: 8px solid #C5A059; border-radius: 8px; margin-bottom: 8px; }
</style>""", unsafe_allow_html=True)

# --- 4. MOTEUR ANTI-DOUBLONS ET PRIORISATION ---
def effectuer_recherche_intelligente(service_label):
    conf = MOTS_CLES_PYXIS.get(service_label, {"prioritaire": service_label, "general": ""})
    resultats = []
    seen_urls = set()
    seen_titles = [] # Pour détecter la similarité thématique

    def est_doublon_thematique(nouveau_titre):
        for t in seen_titles:
            # Si les deux titres partagent trop de mots clés, on refuse
            mots_communs = set(nouveau_titre.lower().split()) & set(t.lower().split())
            if len(mots_communs) > 4: return True
        return False

    with DDGS() as ddgs:
        # Étape 1 : On cherche d'abord les sujets prioritaires (Loi, Réformes)
        try:
            prio = list(ddgs.news(conf["prioritaire"], region="fr-fr", timelimit="w", max_results=10))
            for a in prio:
                if a['url'] not in seen_urls:
                    resultats.append(a); seen_urls.add(a['url']); seen_titles.append(a['title'])
        except: pass

        # Étape 2 : On complète avec le général, sans doublons de sujet
        if len(resultats) < 5:
            try:
                gen = list(ddgs.news(conf["general"], region="fr-fr", timelimit="w", max_results=20))
                for a in gen:
                    if a['url'] not in seen_urls and not est_doublon_thematique(a['title']):
                        resultats.append(a); seen_urls.add(a['url']); seen_titles.append(a['title'])
            except: pass
            
    return resultats[:5]

# --- 5. INTERFACE ---
if 'sujets' not in st.session_state:
    st.session_state['sujets'] = list(MOTS_CLES_PYXIS.keys())

st.markdown('<h1 class="main-title">Veille Stratégique Opérationnelle</h1>', unsafe_allow_html=True)

if st.button("LANCER LA VEILLE GLOBALE 🚀", use_container_width=True):
    for sujet in st.session_state['sujets']:
        st.markdown(f'<div class="titre-service">📌 {sujet}</div>', unsafe_allow_html=True)
        actus = effectuer_recherche_intelligente(sujet)
        if actus:
            c1, c2 = st.columns([1, 1.4])
            with c1: st.info("💡 **Analyse IA :** En cours de développement.")
            with c2:
                for a in actus:
                    st.markdown(f'<div class="article-card"><a href="{a["url"]}" target="_blank" style="text-decoration:none; color:black;"><b>{a["title"]}</b></a><br><small>{a["source"]} | {a["date"]}</small></div>', unsafe_allow_html=True)
