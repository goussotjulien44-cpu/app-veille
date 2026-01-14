import streamlit as st
from duckduckgo_search import DDGS
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Veille Pyxis Support", page_icon="⚖️", layout="wide")

# --- 2. CONFIGURATION MÉTIER (Recadrage) ---
# Dictionnaire structuré pour forcer la pertinence AMO / Stratégie
MOTS_CLES_METIER = {
    "Mobilités (Ferroviaire & Aéroportuaire)": "(SNCF OR RER OR SYSTRA OR EGIS OR 'Réseau Ferré' OR 'Infrastructures Aéroportuaires') AND (AMO OR investissement OR stratégie)",
    "Externalisation (Marchés Publics & AMO)": "('Marchés Publics' OR 'Commande Publique' OR 'Conseil d'Etat' OR BOAMP OR PLACE) AND (Jurisprudence OR Réglementation) -'police' -'municipale'",
    "IT & Systèmes d'Information": "('Gouvernance SI' OR 'Urbanisation SI' OR 'Schéma Directeur') AND (Public OR Collectivité OR AMO)",
    "Digitalisation & IA": "('IA Générative' OR 'Transformation Digitale') AND (Stratégie OR 'Aide à la décision' OR Entreprise)",
    "Vente SaaS & Commerciaux MA-IA": "('Marché SaaS' OR 'Éditeurs de logiciels') AND (Business OR Croissance OR SaaS France)",
    "Développement Software": "('Qualité logicielle' OR DevOps OR 'Dette Technique') AND (Management OR Gouvernance)",
    "Administration, RH & DAF": "('Droit Social' OR 'Réforme Fiscale' OR 'Facturation Électronique') AND (Entreprise OR Actualité Juridique)"
}

# --- 3. DESIGN HAUTE LISIBILITÉ ---
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF !important; }
        [data-testid="stSidebar"] { background-color: #F1F3F6 !important; border-right: 2px solid #000; }
        [data-testid="stSidebar"] * { color: #000000 !important; font-weight: 700 !important; }
        
        /* Correction visuelle des boutons "X" (Capture image_16d2a6) */
        div[data-testid="stSidebar"] button {
            background-color: #E0E0E0 !important;
            color: #000000 !important;
            border: 1px solid #333 !important;
            border-radius: 4px !important;
            font-weight: bold !important;
        }

        .article-card {
            background-color: #ffffff; padding: 15px; border: 1px solid #EEE;
            border-left: 8px solid #C5A059; border-radius: 8px; margin-bottom: 12px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        }
        
        div.stButton > button:first-child {
            background-color: #000000 !important; color: #FFFFFF !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- 4. MOTEUR DE RECHERCHE QUALITATIF ---
def effectuer_recherche_qualitative(sujet_label):
    query = MOTS_CLES_METIER.get(sujet_label, sujet_label)
    resultats_utiles = []
    
    with DDGS() as ddgs:
        # Étape 1 : Priorité absolue aux sources expertes
        # On injecte ici les sites que vous avez validés (Gazette, Moniteur, Village Justice, etc.)
        sources_experts = "site:lemoniteur.fr OR site:achatpublic.info OR site:village-justice.com OR site:lagazettedescommunes.com"
        try:
            experts = list(ddgs.news(f"{query} ({sources_experts})", region="fr-fr", timelimit="d", max_results=3))
            if experts: resultats_utiles.extend(experts)
        except: pass

        # Étape 2 : Ouverture au Net si besoin (Filtrage AMO)
        if len(resultats_utiles) < 2:
            try:
                web = list(ddgs.news(f"{query} AMO OR Conseil", region="fr-fr", timelimit="d", max_results=3))
                if web: resultats_utiles.extend(web)
            except: pass
            
    # Dédoublonnage et nettoyage
    seen_urls = set()
    return [a for a in resultats_utiles if not (a['url'] in seen_urls or seen_urls.add(a['url']))][:4]

# --- 5. INTERFACE ---
if 'sujets' not in st.session_state:
    st.session_state['sujets'] = list(MOTS_CLES_METIER.keys())

with st.sidebar:
    st.markdown("### PYXIS SUPPORT")
    st.write("---")
    nouveau = st.text_input("Ajouter un mot-clé :", key="input_new")
    if st.button("AJOUTER +"):
        if nouveau and nouveau not in st.session_state['sujets']:
            st.session_state['sujets'].append(nouveau); st.rerun()
    st.write("---")
    st.write("**Gérer l'affichage :**")
    for s in st.session_state['sujets']:
        c1, c2 = st.columns([5, 1])
        c1.write(f"• {s}")
        if c2.button("X", key=f"del_{s}"):
            st.session_state['sujets'].remove(s); st.rerun()

st.markdown("<h1 style='text-align:center;'>Veille Stratégique Opérationnelle</h1>", unsafe_allow_html=True)

if st.button("LANCER L'ANALYSE MÉTIER 🚀", use_container_width=True):
    for sujet in st.session_state['sujets']:
        st.markdown(f"### 📌 {sujet}")
        with st.spinner("Filtrage des actualités stratégiques..."):
            time.sleep(1) # Pause anti-rate-limit (image_dfe10b)
            actus = effectuer_recherche_qualitative(sujet)
            if actus:
                col_ia, col_news = st.columns([1, 1.4])
                with col_ia:
                    st.info("💡 **Analyse Pyxis :** IA en attente de synchronisation.")
                with col_news:
                    for a in actus:
                        st.markdown(f"""<div class="article-card">
                            <a href="{a['url']}" target="_blank" style="text-decoration:none; color:black;"><b>{a['title']}</b></a><br>
                            <small>{a['source']} • {a['date']}</small></div>""", unsafe_allow_html=True)
            else:
                st.write("*Aucune actualité stratégique détectée ce jour.*")
