import streamlit as st
from duckduckgo_search import DDGS

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Veille Pyxis Support", page_icon="⚖️", layout="wide")

# --- 2. MOTS-CLÉS AVEC PRIORITÉ STRATÉGIQUE ---
if 'sujets' not in st.session_state:
    st.session_state['sujets'] = [
        "Mobilités (Ferroviaire & Aéroportuaire)",
        "Externalisation (Marchés Publics & AMO)",
        "IT & Systèmes d'Information",
        "Digitalisation & IA",
        "Vente SaaS & Commerciaux MA-IA",
        "Développement Software",
        "Administration, RH & DAF"
    ]

MOTS_CLES_DICT = {
    "Mobilités (Ferroviaire & Aéroportuaire)": {
        "prioritaire": "'Loi-cadre' OR 'Loi de programmation' OR 'Réforme ferroviaire' OR 'Investissement transport'",
        "general": "SNCF OR RER OR RATP OR SYSTRA OR EGIS OR Tramway OR Métro OR Aéroport"
    },
    "Externalisation (Marchés Publics & AMO)": {
        "prioritaire": "'Jurisprudence commande publique' OR 'Réforme marchés publics' OR 'Conseil d'Etat'",
        "general": "BOAMP OR PLACE OR 'Appel d'offres' OR AMO"
    }
}

# --- 3. DESIGN ET VISIBILITÉ (RESTAURATION COLONNE GAUCHE) ---
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF !important; }
        [data-testid="stSidebar"] { background-color: #F0F2F6 !important; border-right: 3px solid #000; min-width: 300px; }
        [data-testid="stSidebar"] * { color: #000000 !important; font-weight: 800 !important; }
        .main-title { color: #000000 !important; font-size: 35px !important; font-weight: 900 !important; text-align: center; }
        .titre-service { color: #000000 !important; font-weight: 900 !important; font-size: 20px; border-bottom: 3px solid #C5A059; margin-top: 25px; padding-bottom: 5px; }
        .article-card { background-color: #ffffff; padding: 12px; border: 1px solid #000; border-left: 8px solid #C5A059; border-radius: 8px; margin-bottom: 10px; }
        div[data-testid="stSidebar"] button { background-color: #E0E0E0 !important; color: #000000 !important; border: 2px solid #000 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. MOTEUR DE RECHERCHE ANTI-DOUBLONS ---
def effectuer_recherche_intelligente(service_label):
    conf = MOTS_CLES_DICT.get(service_label, {"prioritaire": service_label, "general": service_label})
    resultats = []
    seen_urls = set()
    seen_titles = []

    def est_doublon_thematique(titre):
        for t in seen_titles:
            mots_communs = set(titre.lower().split()) & set(t.lower().split())
            if len(mots_communs) > 4: return True
        return False

    with DDGS() as ddgs:
        try:
            # Priorité stratégique (Loi-cadre, etc.)
            prio = list(ddgs.news(conf["prioritaire"], region="fr-fr", timelimit="w", max_results=15))
            for a in prio:
                if a['url'] not in seen_urls:
                    resultats.append(a); seen_urls.add(a['url']); seen_titles.append(a['title'])
            
            # Complément général
            if len(resultats) < 5:
                gen = list(ddgs.news(conf["general"], region="fr-fr", timelimit="w", max_results=20))
                for a in gen:
                    if a['url'] not in seen_urls and not est_doublon_thematique(a['title']):
                        resultats.append(a); seen_urls.add(a['url']); seen_titles.append(a['title'])
        except: pass
    return resultats[:5]

# --- 5. INTERFACE SIDEBAR (RESTAURÉE) ---
with st.sidebar:
    st.markdown("# PYXIS SUPPORT")
    st.write("---")
    nouveau = st.text_input("Saisir un mot-clé :", key="add_key")
    if st.button("AJOUTER +"):
        if nouveau and nouveau not in st.session_state['sujets']:
            st.session_state['sujets'].append(nouveau); st.rerun()
    st.write("---")
    st.markdown("### Gérer l'affichage")
    for s in st.session_state['sujets']:
        c1, c2 = st.columns([4, 1.2])
        c1.write(f"**{s}**")
        if c2.button("X", key=f"del_{s}"):
            st.session_state['sujets'].remove(s); st.rerun()

# --- 6. PAGE PRINCIPALE ---
st.markdown('<h1 class="main-title">Veille Stratégique Opérationnelle</h1>', unsafe_allow_html=True)

if st.button("LANCER LA VEILLE GLOBALE 🚀", use_container_width=True):
    for sujet in st.session_state['sujets']:
        st.markdown(f'<div class="titre-service">📌 {sujet}</div>', unsafe_allow_html=True)
        actus = effectuer_recherche_intelligente(sujet)
        if actus:
            col_ia, col_news = st.columns([1, 1.4])
            with col_ia:
                st.info("💡 **Analyse IA :** En cours de développement.")
            with col_news:
                for a in actus:
                    st.markdown(f"""<div class="article-card">
                        <a href="{a['url']}" target="_blank" style="text-decoration:none; color:black;"><b>{a['title']}</b></a><br>
                        <small>{a['source']} | {a['date']}</small></div>""", unsafe_allow_html=True)
        else:
            st.write("*Aucun article stratégique détecté.*")
