import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai

# --- 1. CONFIGURATION IA ---
if "API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("ERREUR : Clé 'API_KEY' manquante dans les Secrets Streamlit.")

st.set_page_config(page_title="Veille Pyxis Support", layout="wide")

# --- 2. DESIGN FIX (VISIBILITÉ BOUTON ET INTERFACE) ---
st.markdown("""
    <style>
        /* Fond d'application blanc */
        .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
        
        /* Sidebar : Texte noir sur fond gris clair pour visibilité maximale */
        [data-testid="stSidebar"] { background-color: #F0F2F6 !important; border-right: 2px solid #000; }
        [data-testid="stSidebar"] * { color: #000000 !important; font-weight: 700 !important; }
        
        /* Titres */
        .main-title { color: #000; font-size: 32px; font-weight: 900; text-align: center; margin-bottom: 20px; }
        .titre-service { color: #000; font-weight: 900; font-size: 18px; border-bottom: 3px solid #C5A059; margin-top: 20px; }
        
        /* Bouton Lancer la veille : Couleur claire, texte noir */
        div.stButton > button:first-child {
            background-color: #E0E0E0 !important;
            color: #000000 !important;
            border: 2px solid #000000 !important;
            font-weight: bold !important;
        }

        /* Cartes articles */
        .article-card { background-color: #fdfdfd; padding: 10px; border: 1px solid #ddd; border-left: 6px solid #C5A059; border-radius: 5px; margin-bottom: 8px; }
        
        /* Bloc Analyse Pyxis (Bleu clair comme convenu) */
        .analyse-box { background-color: #E3F2FD; border: 1px solid #2196F3; padding: 15px; border-radius: 8px; color: #1976D2; }
    </style>
""", unsafe_allow_html=True)

# --- 3. MOTEUR IA AVEC MESSAGE DE DÉVELOPPEMENT ---
def traiter_ia_expert(liste_brute, service):
    if not liste_brute: return [], "Aucune actualité détectée."
    
    titres_concat = "\n".join([f"- {a['title']} (URL: {a['url']})" for a in liste_brute])
    
    # Prompt optimisé pour le dédoublonnage sémantique
    prompt = f"""
    Analyse ces articles pour le service {service}.
    1. Supprime les doublons (ne garde qu'un seul article par sujet même si les titres diffèrent).
    2. Sélectionne les 4 plus stratégiques.
    Réponds UNIQUEMENT avec les URLs, une par ligne.
    {titres_concat}
    """
    
    try:
        response = model.generate_content(prompt).text
        urls_part = response.strip().split("\n")
        final_articles = [a for a in liste_brute if a['url'] in [u.strip() for u in urls_part]]
        
        # On remplace l'analyse réelle par le message convenu
        message_dev = "Fonctionnalité IA en cours de développement."
        return final_articles[:4], message_dev
    except:
        return liste_brute[:4], "Fonctionnalité IA en cours de développement."

# --- 4. INTERFACE ---
if 'sujets' not in st.session_state:
    st.session_state['sujets'] = [
        "Mobilités (Ferroviaire & Aéroportuaire)", 
        "Externalisation (Marchés Publics & AMO)", 
        "IT & Systèmes d'Information",
        "Digitalisation & IA"
    ]

with st.sidebar:
    st.markdown("### ⚖️ PYXIS SUPPORT")
    for s in st.session_state['sujets']:
        c1, c2 = st.columns([5, 1])
        c1.write(s)
        if c2.button("X", key=f"d_{s}"):
            st.session_state['sujets'].remove(s); st.rerun()

st.markdown('<h1 class="main-title">Veille Stratégique Opérationnelle</h1>', unsafe_allow_html=True)

# Bouton avec style corrigé (clair/texte noir)
if st.button("LANCER LA VEILLE INTELLIGENTE 🚀", use_container_width=True):
    for sujet in st.session_state['sujets']:
        st.markdown(f'<div class="titre-service">📌 {sujet}</div>', unsafe_allow_html=True)
        with DDGS() as ddgs:
            raw = list(ddgs.news(sujet, region="fr-fr", timelimit="w", max_results=25))
        
        actus, analyse = traiter_ia_expert(raw, sujet)
        
        col1, col2 = st.columns([1, 1.4])
        with col1:
            # Encadré d'analyse avec le message fixe convenu
            st.markdown(f'<div class="analyse-box">💡 <b>Analyse IA :</b><br>{analyse}</div>', unsafe_allow_html=True)
        with col2:
            for a in actus:
                st.markdown(f"""<div class="article-card">
                    <a href="{a['url']}" target="_blank" style="text-decoration:none; color:black;"><b>{a['title']}</b></a><br>
                    <small>{a['source']}</small></div>""", unsafe_allow_html=True)
