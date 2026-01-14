import streamlit as st
from duckduckgo_search import DDGS
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Veille Pyxis Support", page_icon="⚖️", layout="wide")

# --- 2. RECADRAGE MÉTIER (AMO & STRATÉGIE) ---
# Utilisation de mots-clés restrictifs pour éliminer le hors-sujet
MOTS_CLES_PYXIS = {
    "Mobilités (Ferroviaire & Aéroportuaire)": "(SNCF OR RER OR RATP OR SYSTRA OR EGIS OR 'Concurrence ferroviaire') AND (AMO OR infrastructure OR transport)",
    "Externalisation (Marchés Publics & AMO)": "('Marchés publics' OR 'Commande publique' OR 'Conseil d'Etat' OR BOAMP) AND (AMO OR Jurisprudence OR Réforme) -'police' -'casino' -'municipal'",
    "IT & Systèmes d'Information": "('Gouvernance SI' OR 'Audit SI' OR 'Schéma Directeur') AND (Public OR AMO OR Conseil)",
    "Digitalisation & IA": "('Transformation digitale' OR 'IA générative' OR RPA) AND (Entreprise OR Stratégie)",
    "Vente SaaS & Commerciaux MA-IA": "('Éditeurs SaaS' OR 'Logiciel SaaS') AND (Marché OR Croissance OR Vente)",
    "Développement Software": "('Qualité logicielle' OR DevOps OR 'Dette technique') AND (Management OR Gouvernance)",
    "Administration, RH & DAF": "('Droit social' OR 'Réforme fiscale' OR 'RH') AND (Entreprise OR Droit)"
}

# --- 3. DESIGN HAUT CONTRASTE (VISIBILITÉ TOTALE) ---
st.markdown("""
    <style>
        /* Fond global et sidebar */
        .stApp { background-color: #FFFFFF !important; }
        [data-testid="stSidebar"] { background-color: #F0F2F6 !important; border-right: 3px solid #000; }
        
        /* Forçage Texte Noir (Sidebar) */
        [data-testid="stSidebar"] * { color: #000000 !important; font-weight: 800 !important; }

        /* Titres de services : Noir profond */
        .titre-service { color: #000000 !important; font-weight: 900 !important; font-size: 24px; border-bottom: 2px solid #C5A059; margin-top: 20px; }
        
        /* Titre Principal : Très lisible */
        .main-title { color: #000000 !important; font-size: 42px !important; font-weight: 900 !important; text-align: center; margin-bottom: 30px; }

        /* Boutons de suppression (X) : Fond Gris Clair, Croix Noire (Visibilité garantie) */
        div[data-testid="stSidebar"] button {
            background-color: #E0E0E0 !important;
            color: #000000 !important;
            border: 2px solid #000000 !important;
            font-size: 16px !important;
            font-weight: 900 !important;
            border-radius: 4px !important;
        }

        /* Cartes articles */
        .article-card {
            background-color: #ffffff; padding: 18px; border: 1px solid #000000;
            border-left: 10px solid #C5A059; border-radius: 8px; margin-bottom: 15px;
        }
        
        /* Bouton Lancer : Noir et Blanc */
        div.stButton > button:first-child { background-color: #000000 !important; color: #FFFFFF !important; font-size: 18px !important; font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. LOGIQUE DE RECHERCHE ANTI-DOUBLONS ---
def effectuer_recherche(service_label):
    query = MOTS_CLES_PYXIS.get(service_label, service_label)
    resultats = []
    seen_urls = set() # Pour éviter les doublons (image_16ddac)
    
    with DDGS() as ddgs:
        # On interroge les sources spécialisées + le net
        try:
            # On cherche des news récentes (timelimit='d')
            search_results = list(ddgs.news(query, region="fr-fr", timelimit="d", max_results=8))
            
            for art in search_results:
                # Nettoyage des doublons par URL
                if art['url'] not in seen_urls:
                    resultats.append(art)
                    seen_urls.add(art['url'])
        except Exception:
            pass
            
    return resultats[:4] # Retourne les 4 meilleurs articles uniques

# --- 5. INTERFACE UTILISATEUR ---
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
        
        with st.spinner(f"Recherche AMO en cours..."):
            time.sleep(1) # Sécurité anti-blocage
            actus = effectuer_recherche(sujet)
            
            if actus:
                col_ia, col_news = st.columns([1, 1.4])
                with col_ia:
                    # Message IA fixe comme demandé (image_d5fb8d)
                    st.info("💡 **Analyse IA :** Fonctionnalité en cours de développement.")
                with col_news:
                    for a in actus:
                        st.markdown(f"""<div class="article-card">
                            <a href="{a['url']}" target="_blank" style="text-decoration:none; color:black;"><b>{a['title']}</b></a><br>
                            <small>Source : {a['source']} | {a['date']}</small></div>""", unsafe_allow_html=True)
            else:
                st.write("*Aucune actualité stratégique détectée aujourd'hui.*")
