import streamlit as st
from duckduckgo_search import DDGS
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Veille Pyxis Support", page_icon="⚖️", layout="wide")

# --- 2. DESIGN "ULTRA-LISIBLE" ---
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF !important; }
        
        /* Barre latérale : Fond gris clair, texte noir */
        [data-testid="stSidebar"] {
            background-color: #F8F9FB !important;
            border-right: 2px solid #EEE;
        }
        
        /* Forçage de la couleur de TOUS les textes en noir dans la sidebar */
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] span, 
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] li {
            color: #000000 !important;
            font-weight: 600 !important;
        }

        /* Bouton de suppression (X) : Fond gris clair, texte noir pour visibilité */
        div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] button {
            background-color: #E0E0E0 !important;
            color: #000000 !important;
            border: 1px solid #CCC !important;
            border-radius: 4px !important;
            height: 25px !important;
            padding: 0px 10px !important;
        }
        
        /* Survol des boutons de suppression */
        div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] button:hover {
            background-color: #FF4B4B !important;
            color: white !important;
        }

        .titre-pyxis {
            color: #000000 !important; font-size: 38px !important;
            font-weight: 900 !important; text-align: center; display: block; margin-bottom: 20px;
        }
        
        .article-card {
            background-color: #ffffff; padding: 15px; border: 1px solid #DDD;
            border-left: 8px solid #C5A059; border-radius: 8px; margin-bottom: 12px;
        }

        /* Bouton principal Noir/Blanc */
        div.stButton > button:first-child {
            background-color: #000000 !important;
            color: #FFFFFF !important;
            font-weight: bold !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIQUE ET SERVICES ---
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

# --- 4. LOGIQUE DE RECHERCHE ---
def effectuer_recherche(sujet):
    resultats = []
    with DDGS() as ddgs:
        try:
            # Recherche élargie pour garantir des résultats
            res = list(ddgs.news(sujet, region="fr-fr", timelimit="d", max_results=5))
            if res: resultats.extend(res)
        except: pass
    return resultats

# --- 5. INTERFACE SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#00A3C1;'>PYXIS</h2><p>Support</p>", unsafe_allow_html=True)
    st.write("---")
    nouveau = st.text_input("Ajouter un service :", placeholder="ex: Cybersécurité")
    if st.button("Ajouter +"):
        if nouveau and nouveau not in st.session_state['sujets']:
            st.session_state['sujets'].append(nouveau); st.rerun()
    
    st.write("---")
    st.markdown("**Gérer l'affichage :**")
    for s in st.session_state['sujets']:
        col_txt, col_del = st.columns([4, 1])
        col_txt.markdown(f"<small>{s}</small>", unsafe_allow_html=True)
        # La croix est maintenant noire sur fond gris clair
        if col_del.button("X", key=f"del_{s}"):
            st.session_state['sujets'].remove(s)
            st.rerun()

# --- 6. ZONE PRINCIPALE ---
st.markdown('<span class="titre-pyxis">Veille Stratégique Opérationnelle</span>', unsafe_allow_html=True)

if st.button("LANCER LA RECHERCHE GLOBALE 🚀", use_container_width=True):
    for sujet in st.session_state['sujets']:
        st.markdown(f"<h3 style='color:black; border-bottom: 2px solid #C5A059;'>📌 {sujet}</h3>", unsafe_allow_html=True)
        with st.spinner("Recherche en cours..."):
            time.sleep(1)
            actus = effectuer_recherche(sujet)
            if actus:
                c1, c2 = st.columns([1, 1.2])
                with c1:
                    st.info("💡 Analyse IA en cours de déploiement.")
                with c2:
                    for a in actus[:3]:
                        st.markdown(f"""<div class="article-card">
                            <a href="{a['url']}" target="_blank" style="text-decoration:none; color:black;"><b>{a['title']}</b></a><br>
                            <small>{a['source']}</small></div>""", unsafe_allow_html=True)
            else:
                st.write("Aucun résultat pour ce service aujourd'hui.")
