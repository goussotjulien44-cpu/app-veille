import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai

# --- 1. CONFIGURATION IA (Utilise votre secret API_KEY) ---
if "API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Clé API manquante dans les Secrets Streamlit.")

# --- 2. CONFIGURATION GÉNÉRALE ---
st.set_page_config(page_title="Veille Pyxis Support", page_icon="⚖️", layout="wide")

if 'sujets' not in st.session_state:
    st.session_state['sujets'] = [
        "Mobilités (Ferroviaire & Aéroportuaire)", "Externalisation (Marchés Publics & AMO)",
        "IT & Systèmes d'Information", "Digitalisation & IA"
    ]

# --- 3. LOGIQUE IA : DÉDOUBLONNAGE ET ANALYSE ---
def traiter_articles_ia(liste_brute, service):
    if not liste_brute: return [], "Aucune actualité trouvée."
    
    # On demande à l'IA de choisir les 5 articles les plus diversifiés
    titres_texte = "\n".join([f"- {a['title']} (URL: {a['url']})" for a in liste_brute])
    
    prompt_tri = f"""
    En tant qu'expert en veille pour le cabinet Pyxis Support, analyse ces titres pour le service {service}.
    1. Supprime les doublons thématiques (ne garde qu'un article par sujet).
    2. Sélectionne les 5 plus stratégiques.
    Réponds UNIQUEMENT avec les URLs, une par ligne.
    Articles :
    {titres_texte}
    """
    
    try:
        # Tri des doublons
        res_tri = model.generate_content(prompt_tri)
        urls_uniques = res_tri.text.strip().split('\n')
        final_list = [a for a in liste_brute if a['url'] in urls_uniques][:5]
        
        # Analyse flash pour le bloc bleu
        resume_prompt = f"Fais une analyse de 3 lignes max sur l'enjeu majeur de ces actus pour un cabinet d'AMO : {[a['title'] for a in final_list]}"
        analyse_ia = model.generate_content(resume_prompt).text
        
        return final_list, analyse_ia
    except:
        return liste_brute[:5], "Analyse indisponible."

# --- 4. DESIGN ---
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF !important; }
        [data-testid="stSidebar"] { background-color: #F0F2F6 !important; border-right: 3px solid #000; }
        .main-title { color: #000; font-size: 35px; font-weight: 900; text-align: center; }
        .titre-service { color: #000; font-weight: 900; font-size: 20px; border-bottom: 3px solid #C5A059; margin-top: 25px; }
        .article-card { background-color: #ffffff; padding: 12px; border: 1px solid #000; border-left: 8px solid #C5A059; border-radius: 8px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 5. INTERFACE SIDEBAR ---
with st.sidebar:
    st.markdown("# PYXIS SUPPORT")
    for s in st.session_state['sujets']:
        c1, c2 = st.columns([4, 1])
        c1.write(f"**{s}**")
        if c2.button("X", key=f"del_{s}"):
            st.session_state['sujets'].remove(s); st.rerun()

# --- 6. PAGE PRINCIPALE ---
st.markdown('<h1 class="main-title">Veille Stratégique Opérationnelle</h1>', unsafe_allow_html=True)

if st.button("LANCER LA VEILLE INTELLIGENTE 🚀", use_container_width=True):
    for sujet in st.session_state['sujets']:
        st.markdown(f'<div class="titre-service">📌 {sujet}</div>', unsafe_allow_html=True)
        with st.spinner(f"L'IA analyse et dédoublonne {sujet}..."):
            with DDGS() as ddgs:
                # Recherche large pour donner du choix à l'IA
                raw = list(ddgs.news(sujet, region="fr-fr", timelimit="w", max_results=25))
            
            actus, analyse = traiter_articles_ia(raw, sujet)
            
            c1, c2 = st.columns([1, 1.4])
            with c1:
                st.warning(f"🎯 **Analyse Pyxis :**\n{analyse}")
            with c2:
                for a in actus:
                    st.markdown(f'<div class="article-card"><a href="{a["url"]}" target="_blank" style="text-decoration:none; color:black;"><b>{a["title"]}</b></a><br><small>{a["source"]}</small></div>', unsafe_allow_html=True)
