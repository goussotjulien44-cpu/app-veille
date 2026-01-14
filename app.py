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

# --- 3. LISTE DES SERVICES "EN DUR" ---
SERVICES_FIXES = [
    "Mobilités (Ferroviaire & Aéroportuaire)",
    "Externalisation (Marchés Publics & AMO)",
    "IT & Systèmes d'Information",
    "Digitalisation & IA",
    "Vente SaaS & Commerciaux MA-IA",
    "Développement Software",
    "Administration, RH & DAF"
]

if 'sujets' not in st.session_state:
    st.session_state['sujets'] = SERVICES_FIXES.copy()

# --- 4. DESIGN HAUTE VISIBILITÉ ---
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF !important; }
        [data-testid="stSidebar"] { background-color: #F1F3F6 !important; border-right: 2px solid #000; }
        
        /* Correction zone de saisie jaune : Texte Noir Opaque */
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

# --- 5. LOGIQUE DE RECHERCHE ---
def effectuer_recherche(sujet):
    resultats = []
    # Sélection des sources
    sources = SOURCES_MOBILITES + SOURCES_GENERALISTES if "Mobilités" in sujet else SOURCES_GENERALISTES
    
    with DDGS() as ddgs:
        # Priorité aux sources expertes
        for site in sources[:3]: # On limite à 3 sites pour la rapidité
            try:
                search = list(ddgs.news(f"{sujet} site:{site}", region="fr-fr", timelimit="d", max_results=1))
                if search: resultats.extend(search)
            except: continue
        
        # Complément Web Global pour garantir du contenu
        try:
            general = list(ddgs.news(sujet, region="fr-fr", timelimit="d", max_results=4))
            resultats.extend(general)
        except: pass
            
    return resultats[:5]

# --- 6. INTERFACE SIDEBAR ---
with st.sidebar:
    st.markdown("<h1>PYXIS</h1><p>Support</p>", unsafe_allow_html=True)
    st.write("---")
    st.write("**Ajouter une thématique**")
    nouveau = st.text_input("Saisir :", key="input_expert", placeholder="ex: Cybersécurité")
    if st.button("Valider"):
        if nouveau and nouveau not in st.session_state['sujets']:
            st.session_state['sujets'].append(nouveau); st.rerun()
    st.write("---")
    st.write("**Services suivis :**")
    for s in st.session_state['sujets']:
        c1, c2 = st.columns([5, 1])
        c1.write(f"• {s}")
        if s not in SERVICES_FIXES: # On ne permet de supprimer que les ajouts manuels
            if c2.button("X", key=f"del_{s}"):
                st.session_state['sujets'].remove(s); st.rerun()

# --- 7. ZONE PRINCIPALE ---
st.markdown('<span class="titre-pyxis">Veille Stratégique Opérationnelle</span>', unsafe_allow_html=True)

if st.button("LANCER LA RECHERCHE SUR TOUS LES SERVICES 🚀", use_container_width=True):
    for sujet in st.session_state['sujets']:
        st.markdown(f"<h2 style='color:black; border-bottom: 2px solid #C5A059;'>📌 {sujet}</h2>", unsafe_allow_html=True)
        
        time.sleep(1.5) # Protection contre le blocage DDG
        
        actus = effectuer_recherche(sujet)
        if actus:
            col_ia, col_news = st.columns([1, 1.2])
            with col_ia:
                st.info("💡 **Analyse IA :** Fonctionnalité en cours de développement.")
                st.caption("Scan des sources institutionnelles (DAJ, Gazette, Moniteur) effectué.")
            with col_news:
                for a in actus:
                    st.markdown(f"""<div class="article-card">
                        <a href="{a['url']}" target="_blank" style="text-decoration:none; color:black;"><b>{a['title']}</b></a><br>
                        <small>{a['source']} • {a['date']}</small></div>""", unsafe_allow_html=True)
        else:
            st.write("Aucune actualité récente détectée pour ce service.")
