import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai
import time
from fpdf import FPDF
from datetime import datetime
import requests
import urllib.parse

# --- CONFIGURATION FONCTIONNALITÉS ---
AFFICHER_EXPORT_PDF = False  # Masqué selon votre demande précédente

# --- 1. CONFIGURATION IA ---
if "API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["API_KEY"])
    generation_config = {"temperature": 0.0, "top_p": 1, "top_k": 1}
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config=generation_config)
else:
    st.error("ERREUR : Clé 'API_KEY' manquante dans les secrets.")

st.set_page_config(page_title="Veille Pyxis Support", layout="wide")

# --- 2. DICTIONNAIRE DE RECHERCHE ---
MOTS_CLES_STRATEGIQUES = {
    "Mobilités (Ferroviaire & Aéroportuaire)": "SNCF OR RER OR RATP OR 'Loi-cadre' OR 'Loi de programmation' OR 'Financement rail' OR 'Tramway'",
    "Externalisation (Marchés Publics & AMO)": "BOAMP OR 'Marchés publics' OR 'Commande publique' OR 'Conseil d'Etat' OR 'Assistance à maîtrise d'ouvrage' OR AMO -Afrique -Sénégal -Maroc -Algérie -Tunisie -Cameroun -Côte d'Ivoire",
    "IT & Systèmes d'Information": "'Systèmes d'information' OR 'Infrastructure IT' OR 'Transformation digitale' OR 'Cybersécurité' OR 'Logiciel métier'",
    "Digitalisation & IA": "'Intelligence artificielle' OR 'IA générative' OR 'Digitalisation' OR 'Souveraineté numérique'",
    "Vente SaaS & Commerciaux MA-IA": "'Vente SaaS' OR 'Logiciel par abonnement' OR 'Salesforce' OR 'Solution cloud'",
    "Développement Software": "'Développement logiciel' OR 'DevOps' OR 'Cloud computing' OR 'Logiciel libre'",
    "Administration, RH & DAF": "'Réforme RH' OR 'Gestion administrative' OR 'Finance d'entreprise' OR 'Externalisation RH'"
}

# --- 3. FONCTIONS TECHNIQUES ---
def verifier_lien_actif(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'}
    try:
        url_clean = str(url).strip()
        response = requests.head(url_clean, headers=headers, timeout=3, allow_redirects=True)
        return response.status_code < 400
    except:
        return False

# --- 4. LOGIQUE PDF (EN RÉSERVE / MASQUÉE) ---
class PyxisPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 10, 'VEILLE STRATÉGIQUE PYXIS SUPPORT', 0, 1, 'C')
        self.ln(10)
    def footer(self):
        self.set_y(-15)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generer_pdf(resultats):
    pdf = PyxisPDF()
    pdf.add_page()
    for service, data in resultats.items():
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 10, f"SECTION : {service.upper()}", 0, 1)
        for art in data['articles']:
            safe_url = urllib.parse.quote(art['url'], safe='/:?=&')
            pdf.set_font('Helvetica', '', 10)
            pdf.write(5, f"- {art['title']}\n", safe_url)
            pdf.ln(2)
    return bytes(pdf.output())

# --- 5. INTERFACE ET DESIGN (CORRECTION DU CONTRASTE ICI) ---
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF !important; }
        
        /* Correction contraste titre principal */
        .main-title { 
            color: #1a1a1a !important; 
            font-size: 38px !important; 
            font-weight: 900 !important; 
            text-align: center !important; 
            margin-bottom: 30px !important;
            opacity: 1 !important;
            display: block !important;
        }
        
        .titre-service { color: #000; font-weight: 900; font-size: 18px; border-bottom: 3px solid #C5A059; margin-top: 25px; }
        .article-card { background-color: #fdfdfd; padding: 12px; border: 1px solid #ddd; border-left: 8px solid #C5A059; border-radius: 5px; margin-bottom: 8px; }
        .analyse-box { background-color: #E3F2FD; border: 1px solid #2196F3; padding: 15px; border-radius: 8px; color: #1976D2; }
    </style>
""", unsafe_allow_html=True)

# --- 6. MOTEUR IA ---
def traiter_ia_expert(liste_brute, service):
    if not liste_brute: return [], "Aucune donnée."
    data_concat = "\n".join([f"TITRE: {a['title']}\nURL: {a['url']}\n---" for a in liste_brute])
    prompt = f"Expert Pyxis France : Filtre ces articles pour {service}. Garde uniquement la FRANCE. Jette l'Afrique et l'étranger. Max 4 URLs.\n{data_concat}"
    try:
        response = model.generate_content(prompt).text
        urls = [u.strip() for u in response.strip().split("\n") if "http" in u]
        return [a for a in liste_brute if a['url'] in urls][:4], "Filtrage géographique effectué."
    except:
        return liste_brute[:4], "Filtrage standard."

# --- 7. SESSION ET AFFICHAGE ---
if 'last_results' not in st.session_state:
    st.session_state['last_results'] = {}
if 'sujets' not in st.session_state:
    st.session_state['sujets'] = list(MOTS_CLES_STRATEGIQUES.keys())

# Application du titre avec la classe corrigée
st.markdown('<h1 class="main-title">Veille Stratégique Opérationnelle</h1>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ⚖️ PYXIS SUPPORT")
    st.write("---")
    for s in list(st.session_state['sujets']):
        c1, c2 = st.columns([5, 1.2])
        c1.write(s)
        if c2.button("X", key=f"d_{s}"):
            st.session_state['sujets'].remove(s)
            st.rerun()

if st.button("LANCER LA VEILLE GÉNÉRALE 🚀", use_container_width=True):
    st.session_state['last_results'] = {}
    for sujet in st.session_state['sujets']:
        with st.status(f"Recherche : {sujet}...", expanded=False) as status:
            query = MOTS_CLES_STRATEGIQUES.get(sujet, sujet)
            raw = []
            try:
                with DDGS() as ddgs:
                    raw = list(ddgs.news(query, region="fr-fr", timelimit="w", max_results=20))
            except: time.sleep(2)
            
            if raw:
                actus_ia, msg = traiter_ia_expert(raw, sujet)
                actus_finales = [a for a in actus_ia if verifier_lien_actif(a['url'])]
                st.session_state['last_results'][sujet] = {'articles': actus_finales, 'analysis': msg}
                status.update(label=f"✅ {sujet} terminé", state="complete")
            else:
                st.session_state['last_results'][sujet] = {'articles': [], 'analysis': "Aucun résultat."}
                status.update(label=f"❌ {sujet} : Vide", state="error")
            time.sleep(1)
    st.rerun()

# AFFICHAGE DES RÉSULTATS
if st.session_state['last_results']:
    if AFFICHER_EXPORT_PDF:
        try:
            pdf_bytes = generer_pdf(st.session_state['last_results'])
            st.download_button("📥 TÉLÉCHARGER LE RAPPORT PDF", pdf_bytes, "Veille_Pyxis.pdf", "application/pdf", use_container_width=True)
        except: st.warning("Le module PDF est en maintenance.")

    for sujet, data in st.session_state['last_results'].items():
        st.markdown(f'<div class="titre-service">📌 {sujet}</div>', unsafe_allow_html=True)
        col_ia, col_art = st.columns([1, 1.4])
        with col_ia:
            st.markdown(f'<div class="analyse-box">💡 {data["analysis"]}</div>', unsafe_allow_html=True)
        with col_art:
            if not data['articles']: st.info("Aucun article pertinent.")
            for a in data['articles']:
                st.markdown(f"""
                <div class="article-card">
                    <a href="{a['url']}" target="_blank" style="text-decoration:none; color:black; font-weight:bold;">{a['title']}</a><br>
                    <small style="color:gray;">Source : {a['source']}</small>
                </div>
                """, unsafe_allow_html=True)
