import streamlit as st
from duckduckgo_search import DDGS

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Veille Pyxis Support", page_icon="⚖️", layout="wide")

# --- 2. GESTION DES SUJETS ---
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

# Dictionnaire de recherche optimisé
MOTS_CLES_DICT = {
    "Mobilités (Ferroviaire & Aéroportuaire)": {
        "query": "SNCF OR RER OR RATP OR Tramway OR 'Loi-cadre' OR 'Loi de programmation' OR 'Réforme ferroviaire' OR 'Investissement transport'",
    },
    "Externalisation (Marchés Publics & AMO)": {
        "query": "BOAMP OR PLACE OR 'Appel d'offres' OR 'Marchés publics' OR 'Commande publique' OR 'Conseil d'Etat' OR AMO",
    }
}

# --- 3. DESIGN HAUT CONTRASTE (SIDEBAR RESTAURÉE) ---
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF !important; }
        [data-testid="stSidebar"] { background-color: #F0F2F6 !important; border-right: 3px solid #000; min-width: 300px; }
        [data-testid="stSidebar"] * { color: #000000 !important; font-weight: 800 !important; }
        .main-title { color: #000000 !important; font-size: 35px !important; font-weight: 900 !important; text-align: center; }
        .titre-service { color: #000000 !important; font-weight: 900 !important; font-size: 20px; border-bottom: 3px solid #C5A059; margin-top: 25px; padding-bottom: 5px; }
        .article-card { background-color: #ffffff; padding: 12px; border: 1px solid #000; border-left: 8px solid #C5A059; border-radius: 8px; margin-bottom: 10px; }
        div[data-testid="stSidebar"] button { background-color: #E0E0E0 !important; color: #000000 !important; border: 2px solid #000 !important; font-weight: 900 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. MOTEUR ANTI-DOUBLON SÉMANTIQUE ---
def effectuer_recherche_unique(service_label):
    conf = MOTS_CLES_DICT.get(service_label, {"query": service_label})
    resultats = []
    seen_urls = set()
    # On stocke les sets de mots-clés des titres déjà affichés
    mots_cles_affiches = [] 

    def est_doublon_thematique(titre):
        # On extrait les mots de plus de 3 lettres
        mots_actuels = set([m.lower() for m in titre.split() if len(m) > 3])
        for existant in mots_cles_affiches:
            # Si plus de 3 mots importants sont identiques, c'est le même sujet
            intersection = mots_actuels & existant
            if len(intersection) >= 3:
                return True
        return False

    with DDGS() as ddgs:
        try:
            # On demande 30 résultats pour avoir de la matière à filtrer
            raw = list(ddgs.news(conf["query"], region="fr-fr", timelimit="w", max_results=30))
            
            for a in raw:
                if len(resultats) >= 5: break # On s'arrête à 5 articles uniques
                
                if a['url'] not in seen_urls and not est_doublon_thematique(a['title']):
                    resultats.append(a)
                    seen_urls.add(a['url'])
                    # On mémorise les mots-clés pour bloquer les prochains doublons
                    mots_cles_affiches.append(set([m.lower() for m in a['title'].split() if len(m) > 3]))
        except: pass
    return resultats

# --- 5. INTERFACE SIDEBAR ---
with st.sidebar:
    st.markdown("# PYXIS SUPPORT")
    st.write("---")
    nouveau = st.text_input("Ajouter un service :", key="add_srv")
    if st.button("AJOUTER +"):
        if nouveau and nouveau not in st.session_state['sujets']:
            st.session_state['sujets'].append(nouveau); st.rerun()
    st.write("---")
    st.markdown("### Mes Services")
    for s in st.session_state['sujets']:
        c1, c2 = st.columns([4, 1.2])
        c1.write(f"**{s}**")
        if c2.button("X", key=f"del_{s}"):
            st.session_state['sujets'].remove(s); st.rerun()

# --- 6. PAGE PRINCIPALE ---
st.markdown('<h1 class="main-title">Veille Stratégique Opérationnelle</h1>', unsafe_allow_html=True)

if st.button("LANCER L'ANALYSE COMPLÈTE 🚀", use_container_width=True):
    for sujet in st.session_state['sujets']:
        st.markdown(f'<div class="titre-service">📌 {sujet}</div>', unsafe_allow_html=True)
        actus = effectuer_recherche_unique(sujet)
        if actus:
            col_ia, col_news = st.columns([1, 1.4])
            with col_ia:
                st.info("💡 **Analyse IA :** En cours de développement.")
            with col_news:
                for a in actus:
                    st.markdown(f"""<div class="article-card">
                        <a href="{a['url']}" target="_blank" style="text-decoration:none; color:black;"><b>{a['title']}</b></a><br>
                        <small>Source : {a['source']} | {a['date']}</small></div>""", unsafe_allow_html=True)
        else:
            st.write("*Aucun article unique détecté cette semaine.*")
