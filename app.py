import streamlit as st
from duckduckgo_search import DDGS
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Veille Pyxis Support", page_icon="⚖️", layout="wide")

# --- 2. SOURCES PRIVILÉGIÉES ---
SOURCES_MOBILITES = [
    "espacetrain.com", "lerail.com", "laviedurail.com", "railpassion.fr", 
    "ville-rail-transports.com", "usinenouvelle.com", "railmarket.com"
]

SOURCES_GENERALISTES = [
    "lagazettedescommunes.com", "achatpublic.info", "village-justice.com", 
    "conseil-etat.fr", "lemoniteur.fr", "economie.gouv.fr/daj"
]

# --- 3. SERVICES PAR DÉFAUT ---
SERVICES_INITIAUX = [
    "Mobilités (Ferroviaire & Aéroportuaire)",
    "Externalisation (Marchés Publics & AMO)",
    "IT & Systèmes d'Information",
    "Digitalisation & IA",
    "Vente SaaS & Commerciaux MA-IA",
    "Développement Software",
    "Administration, RH & DAF"
]

if 'sujets' not in st.session_state:
    st.session_state['sujets'] = SERVICES_INITIAUX.copy()

# --- 4. DESIGN ---
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF !important; }
        [data-testid="stSidebar"] { background-color: #F1F3F6 !important; border-right: 2px solid #000; }
        [data-testid="stSidebar"] * { color: #000000 !important; font-weight: 700 !important; }
        .titre-pyxis {
            color: #000000 !important; font-size: 38px !important;
            font-weight: 900 !important; text-align: center; display: block; margin-bottom: 20px;
        }
        .article-card {
            background-color: #ffffff; padding: 15px; border: 1px solid #DDD;
            border-left: 8px solid #C5A059; border-radius: 8px; margin-bottom: 12px;
        }
        div.stButton > button { background-color: #000000 !important; color: #FFFFFF !important; }
    </style>
""", unsafe_allow_html=True)

# --- 5. LOGIQUE DE RECHERCHE ROBUSTE ---
def effectuer_recherche(sujet):
    resultats = []
    # On détermine les sources selon le sujet
    sources_specialisees = SOURCES_MOBILITES if "Mobilités" in sujet else []
    toutes_sources = sources_specialisees + SOURCES_GENERALISTES
    
    with DDGS() as ddgs:
        # ÉTAPE 1 : Tentative sur les sources privilégiées (plus rapide)
        for site in toutes_sources[:4]:
            try:
                query = f"{sujet} site:{site}"
                search = list(ddgs.news(query, region="fr-fr", timelimit="d", max_results=1))
                if search: resultats.extend(search)
            except: continue
        
        # ÉTAPE 2 : Recherche Web Globale (systématique pour garantir du contenu)
        try:
            # On cherche des news générales pour compléter
            general = list(ddgs.news(sujet, region="fr-fr", timelimit="d", max_results=5))
            if general:
                resultats.extend(general)
        except: pass
            
    # Suppression des doublons potentiels par URL
    vus = set()
    uniques = []
    for a in resultats:
        if a['url'] not in vus:
            uniques.append(a)
            vus.add(a['url'])
            
    return uniques[:5]

# --- 6. INTERFACE SIDEBAR ---
with st.sidebar:
    st.markdown("<h1>PYXIS</h1><p>Support</p>", unsafe_allow_html=True)
    st.write("---")
    st.write("**Ajouter un service ou mot-clé**")
    nouveau = st.text_input("Saisir :", key="input_expert", placeholder="ex: Cybersécurité")
    if st.button("Ajouter à la veille"):
        if nouveau and nouveau not in st.session_state['sujets']:
            st.session_state['sujets'].append(nouveau); st.rerun()
    
    st.write("---")
    st.write("**Gérer l'affichage :**")
    # Liste de suppression pour TOUS les services
    for s in st.session_state['sujets']:
        col_txt, col_del = st.columns([5, 1])
        col_txt.write(f"• {s}")
        if col_del.button("X", key=f"del_{s}"):
            st.session_state['sujets'].remove(s)
            st.rerun()

# --- 7. ZONE PRINCIPALE ---
st.markdown('<span class="titre-pyxis">Veille Stratégique Opérationnelle</span>', unsafe_allow_html=True)

if st.button("LANCER LA RECHERCHE SUR TOUS LES SERVICES 🚀", use_container_width=True):
    if not st.session_state['sujets']:
        st.warning("Veuillez ajouter ou sélectionner au moins un service dans la barre latérale.")
    else:
        for sujet in st.session_state['sujets']:
            st.markdown(f"<h2 style='color:black; border-bottom: 2px solid #C5A059; padding-top:10px;'>📌 {sujet}</h2>", unsafe_allow_html=True)
            
            with st.spinner(f"Analyse en cours pour {sujet}..."):
                time.sleep(1.5) # Pause anti-blocage
                actus = effectuer_recherche(sujet)
                
                if actus:
                    col_ia, col_news = st.columns([1, 1.2])
                    with col_ia:
                        st.info("💡 **Analyse IA :** Fonctionnalité en cours de développement.")
                        st.caption("Sources prioritaires et Web global interrogés.")
                    with col_news:
                        for a in actus:
                            st.markdown(f"""<div class="article-card">
                                <a href="{a['url']}" target="_blank" style="text-decoration:none; color:black;"><b>{a['title']}</b></a><br>
                                <small>{a['source']} • {a['date']}</small></div>""", unsafe_allow_html=True)
                else:
                    st.write("Aucune actualité détectée ce jour. Essayez d'élargir le mot-clé.")
