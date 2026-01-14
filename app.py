import streamlit as st
from duckduckgo_search import DDGS
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Veille Pyxis Support", page_icon="⚖️", layout="wide")

# --- 2. FILTRAGE MÉTIER RIGOUREUX & ÉLARGISSEMENT TEMPIS (7 JOURS) ---
MOTS_CLES_PYXIS = {
    "Mobilités (Ferroviaire & Aéroportuaire)": "(SNCF OR RER OR RATP OR SYSTRA OR EGIS) AND (AMO OR infrastructure OR transport OR ferroviaire)",
    "Externalisation (Marchés Publics & AMO)": "('Marchés publics' OR 'Commande publique' OR 'Conseil d'Etat' OR BOAMP OR 'Appel d'offres') AND (AMO OR Conseil) -'casino' -'municipale' -'fait-divers'",
    "IT & Systèmes d'Information": "('Gouvernance SI' OR 'Urbanisation SI' OR 'Schéma Directeur') AND (Public OR AMO OR Conseil)",
    "Digitalisation & IA": "('Transformation digitale' OR 'IA générative' OR RPA) AND (Entreprise OR Stratégie)",
    "Vente SaaS & Commerciaux MA-IA": "('Éditeurs SaaS' OR 'Logiciel SaaS') AND (Marché OR Croissance OR Vente)",
    "Développement Software": "('Qualité logicielle' OR DevOps OR 'Dette technique') AND (Management OR Gouvernance)",
    "Administration, RH & DAF": "('Droit social' OR 'Réforme fiscale' OR 'RH') AND (Entreprise OR Droit)"
}

# --- 3. DESIGN HAUT CONTRASTE (LISIBILITÉ GARANTIE) ---
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF !important; }
        [data-testid="stSidebar"] { background-color: #F0F2F6 !important; border-right: 3px solid #000; }
        
        /* Forçage Texte Noir Sidebar (image_15f184) */
        [data-testid="stSidebar"] * { color: #000000 !important; font-weight: 800 !important; }

        /* Titre Principal Noir Intense */
        .main-title { color: #000000 !important; font-size: 40px !important; font-weight: 900 !important; text-align: center; margin-bottom: 30px; }
        
        /* Titres de services */
        .titre-service { color: #000000 !important; font-weight: 900 !important; font-size: 24px; border-bottom: 3px solid #C5A059; padding-bottom: 5px; margin-top: 25px; }

        /* Boutons de suppression (X) : Fond Gris Clair, Croix Noire (image_16d2a6) */
        div[data-testid="stSidebar"] button {
            background-color: #E0E0E0 !important;
            color: #000000 !important;
            border: 2px solid #000000 !important;
            font-size: 16px !important;
            font-weight: 900 !important;
        }

        /* Cartes articles avec bordures nettes */
        .article-card {
            background-color: #ffffff; padding: 18px; border: 2px solid #EEEEEE;
            border-left: 10px solid #C5A059; border-radius: 8px; margin-bottom: 15px;
        }
        
        /* Message IA Fixe (image_174305) */
        .ia-box { background-color: #E3F2FD; color: #0D47A1; padding: 15px; border-radius: 5px; font-weight: 500; border: 1px solid #BBDEFB; }
    </style>
""", unsafe_allow_html=True)

# --- 4. MOTEUR DE RECHERCHE QUALITATIF (ANTI-DOUBLONS) ---
def effectuer_recherche(service_label):
    query = MOTS_CLES_PYXIS.get(service_label, service_label)
    resultats = []
    seen_urls = set()
    
    with DDGS() as ddgs:
        try:
            # Passage à timelimit='w' (semaine) pour plus de pertinence (image_174305)
            search_results = list(ddgs.news(query, region="fr-fr", timelimit="w", max_results=10))
            
            for art in search_results:
                if art['url'] not in seen_urls:
                    resultats.append(art)
                    seen_urls.add(art['url'])
        except:
            pass
            
    return resultats[:4]

# --- 5. INTERFACE ---
if 'sujets' not in st.session_state:
    st.session_state['sujets'] = list(MOTS_CLES_PYXIS.keys())

with st.sidebar:
    st.markdown("## PYXIS SUPPORT")
    st.write("---")
    nouveau = st.text_input("Saisir un mot-clé :", key="input_service")
    if st.button("AJOUTER +"):
        if nouveau and nouveau not in st.session_state['sujets']:
            st.session_state['sujets'].append(nouveau); st.rerun()
    st.write("---")
    st.markdown("### Gérer l'affichage")
    for s in st.session_state['sujets']:
        col_txt, col_del = st.columns([4, 1.2])
        col_txt.write(f"**{s}**")
        if col_del.button("X", key=f"del_{s}"):
            st.session_state['sujets'].remove(s); st.rerun()

st.markdown('<h1 class="main-title">Veille Stratégique Opérationnelle</h1>', unsafe_allow_html=True)

if st.button("LANCER L'ANALYSE GLOBALE 🚀", use_container_width=True):
    for sujet in st.session_state['sujets']:
        st.markdown(f'<div class="titre-service">📌 {sujet}</div>', unsafe_allow_html=True)
        
        with st.spinner(f"Analyse stratégique en cours..."):
            time.sleep(1) 
            actus = effectuer_recherche(sujet)
            
            if actus:
                col_ia, col_news = st.columns([1, 1.4])
                with col_ia:
                    st.markdown('<div class="ia-box">💡 <b>Analyse IA :</b> Fonctionnalité en cours de développement.</div>', unsafe_allow_html=True)
                with col_news:
                    for a in actus:
                        st.markdown(f"""<div class="article-card">
                            <a href="{a['url']}" target="_blank" style="text-decoration:none; color:black;"><b>{a['title']}</b></a><br>
                            <small><b>Source :</b> {a['source']} | {a['date']}</small></div>""", unsafe_allow_html=True)
            else:
                st.write("*Aucune actualité pertinente détectée cette semaine.*")
