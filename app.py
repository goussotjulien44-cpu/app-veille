import streamlit as st
from duckduckgo_search import DDGS
import re

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Veille Pyxis Support", page_icon="⚖️", layout="wide")

# --- 2. GESTION DES SUJETS ---
if 'sujets' not in st.session_state:
    st.session_state['sujets'] = [
        "Mobilités (Ferroviaire & Aéroportuaire)", "Externalisation (Marchés Publics & AMO)",
        "IT & Systèmes d'Information", "Digitalisation & IA"
    ]

MOTS_CLES_DICT = {
    "Mobilités (Ferroviaire & Aéroportuaire)": "SNCF OR RER OR RATP OR Tramway OR 'Loi-cadre' OR 'Loi de programmation' OR 'Financement rail'",
    "Externalisation (Marchés Publics & AMO)": "BOAMP OR 'Marchés publics' OR 'Commande publique' OR 'Conseil d'Etat' OR AMO",
}

# --- 3. DESIGN HAUT CONTRASTE ---
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF !important; }
        [data-testid="stSidebar"] { background-color: #F0F2F6 !important; border-right: 3px solid #000; min-width: 320px; }
        [data-testid="stSidebar"] * { color: #000000 !important; font-weight: 800 !important; }
        .main-title { color: #000000 !important; font-size: 35px !important; font-weight: 900 !important; text-align: center; }
        .titre-service { color: #000000 !important; font-weight: 900 !important; font-size: 20px; border-bottom: 3px solid #C5A059; margin-top: 25px; }
        .article-card { background-color: #ffffff; padding: 12px; border: 1px solid #000; border-left: 8px solid #C5A059; border-radius: 8px; margin-bottom: 10px; }
        div[data-testid="stSidebar"] button { background-color: #E0E0E0 !important; color: #000000 !important; border: 2px solid #000 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. MOTEUR ANTI-DOUBLON RADICAL ---
def effectuer_recherche_unique(service_label):
    query = MOTS_CLES_DICT.get(service_label, service_label)
    resultats = []
    seen_urls = set()
    # On stocke les paires de mots déjà vues pour bloquer les sujets redondants
    paires_vues = set()

    def obtenir_paires(texte):
        # Nettoyage : mots de plus de 3 lettres uniquement
        mots = [m for m in re.findall(r'\w+', texte.lower()) if len(m) > 3]
        # Création de paires consécutives (bigrammes)
        return set(zip(mots, mots[1:]))

    with DDGS() as ddgs:
        try:
            raw = list(ddgs.news(query, region="fr-fr", timelimit="w", max_results=40))
            for a in raw:
                if len(resultats) >= 5: break
                
                paires_actuelles = obtenir_paires(a['title'])
                # Si l'article partage au moins une paire de mots clé avec un article déjà pris, on zappe
                if a['url'] not in seen_urls and not (paires_actuelles & paires_vues):
                    resultats.append(a)
                    seen_urls.add(a['url'])
                    paires_vues.update(paires_actuelles)
        except: pass
    return resultats

# --- 5. INTERFACE ---
with st.sidebar:
    st.markdown("# PYXIS SUPPORT")
    st.write("---")
    st.markdown("### Mes Services")
    for s in st.session_state['sujets']:
        c1, c2 = st.columns([4, 1.2])
        c1.write(f"**{s}**")
        if c2.button("X", key=f"del_{s}"):
            st.session_state['sujets'].remove(s); st.rerun()

st.markdown('<h1 class="main-title">Veille Stratégique Opérationnelle</h1>', unsafe_allow_html=True)

if st.button("LANCER L'ANALYSE COMPLÈTE 🚀", use_container_width=True):
    for sujet in st.session_state['sujets']:
        st.markdown(f'<div class="titre-service">📌 {sujet}</div>', unsafe_allow_html=True)
        actus = effectuer_recherche_unique(sujet)
        if actus:
            c1, c2 = st.columns([1, 1.4])
            with c1: st.info("💡 **Analyse IA :** En cours de développement.")
            with c2:
                for a in actus:
                    st.markdown(f'<div class="article-card"><a href="{a["url"]}" target="_blank" style="text-decoration:none; color:black;"><b>{a["title"]}</b></a><br><small>{a["source"]} | {a["date"]}</small></div>', unsafe_allow_html=True)
