import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai
import time
from fpdf import FPDF
from datetime import datetime
import requests  # NÉCESSAIRE POUR VÉRIFIER LES LIENS MORTS

# --- 1. CONFIGURATION IA ---
if "API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["API_KEY"])
    generation_config = {"temperature": 0.0, "top_p": 1, "top_k": 1}
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config=generation_config)
else:
    st.error("ERREUR : Clé 'API_KEY' manquante.")

st.set_page_config(page_title="Veille Pyxis Support", layout="wide")

# --- 2. DICTIONNAIRE DE RECHERCHE STRATÉGIQUE (AVEC EXCLUSIONS GÉOGRAPHIQUES) ---
MOTS_CLES_STRATEGIQUES = {
    "Mobilités (Ferroviaire & Aéroportuaire)": "SNCF OR RER OR RATP OR 'Loi-cadre' OR 'Loi de programmation' OR 'Financement rail' OR 'Tramway'",
    # AJOUT DES EXCLUSIONS STRICTES ICI (-Afrique -Sénégal etc.)
    "Externalisation (Marchés Publics & AMO)": "BOAMP OR 'Marchés publics' OR 'Commande publique' OR 'Conseil d'Etat' OR 'Assistance à maîtrise d'ouvrage' OR AMO -Afrique -Sénégal -Maroc -Algérie -Tunisie -Cameroun -Abidjan",
    "IT & Systèmes d'Information": "'Systèmes d'information' OR 'Infrastructure IT' OR 'Transformation digitale' OR 'Cybersécurité' OR 'Logiciel métier'",
    "Digitalisation & IA": "'Intelligence artificielle' OR 'IA générative' OR 'Digitalisation' OR 'Souveraineté numérique'",
    "Vente SaaS & Commerciaux MA-IA": "'Vente SaaS' OR 'Logiciel par abonnement' OR 'Salesforce' OR 'Solution cloud'",
    "Développement Software": "'Développement logiciel' OR 'DevOps' OR 'Cloud computing' OR 'Logiciel libre'",
    "Administration, RH & DAF": "'Réforme RH' OR 'Gestion administrative' OR 'Finance d'entreprise' OR 'Externalisation RH'"
}

# --- 3. FONCTION DE VÉRIFICATION DES LIENS (NOUVEAU) ---
def verifier_lien_actif(url):
    """Vérifie si un lien est mort (404) ou inaccessible rapidement."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        # Timeout court (2s) pour ne pas trop ralentir l'app
        response = requests.head(url, headers=headers, timeout=2, allow_redirects=True)
        if response.status_code == 404: # Lien mort confirmé
            return False
        if response.status_code >= 500: # Erreur serveur
            return False
        return True
    except requests.RequestException:
        # En cas d'échec du HEAD (certains sites bloquent), on tente un GET léger
        try:
            response = requests.get(url, headers=headers, timeout=2, stream=True)
            return response.status_code < 400
        except:
            return False # Si tout échoue, on considère le lien comme risqué/mort

# --- 4. CLASSE GÉNÉRATION PDF ---
class PyxisPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, 'VEILLE STRATÉGIQUE PYXIS SUPPORT', 0, 1, 'C')
        self.set_font('Helvetica', '', 10)
        self.cell(0, 10, f'Généré le : {datetime.now().strftime("%d/%m/%Y à %H:%M")}', 0, 1, 'C')
        self.ln(10)
        self.set_draw_color(197, 160, 89)
        self.line(10, 32, 200, 32)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generer_pdf(resultats_complets):
    pdf = PyxisPDF()
    pdf.add_page()
    for service, data in resultats_complets.items():
        articles = data['articles']
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_fill_color(240, 242, 246)
        titre_service = f" SECTION : {service.upper()} "
        try:
            pdf.cell(0, 10, titre_service, 0, 1, 'L', fill=True)
        except:
            pdf.cell(0, 10, "SECTION", 0, 1, 'L', fill=True)
        pdf.ln(2)
        
        if not articles:
            pdf.set_font('Helvetica', 'I', 10)
            pdf.cell(0, 10, "Aucun article sélectionné.", 0, 1)
        else:
            for art in articles:
                pdf.set_font('Helvetica', 'B', 10)
                pdf.set_text_color(0, 0, 255)
                titre = art['title'].replace("’", "'").replace("“", '"').replace("”", '"')
                try:
                    pdf.multi_cell(0, 6, f"- {titre}", 0, 'L', link=art['url'])
                except:
                    pdf.multi_cell(0, 6, f"- (Titre non encodable)", 0, 'L', link=art['url'])
                pdf.set_font('Helvetica', '', 9)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 5, f"Source : {art['source']}", 0, 1)
                pdf.ln(2)
        pdf.ln(5)
    return bytes(pdf.output())

# --- 5. DESIGN STREAMLIT ---
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF !important; }
        .main-title { color: #000; font-size: 35px; font-weight: 900; text-align: center; margin-bottom: 30px; }
        .titre-service { color: #000; font-weight: 900; font-size: 18px; border-bottom: 3px solid #C5A059; margin-top: 25px; }
        .article-card { background-color: #fdfdfd; padding: 12px; border: 1px solid #ddd; border-left: 8px solid #C5A059; border-radius: 5px; margin-bottom: 8px; }
        .analyse-box { background-color: #E3F2FD; border: 1px solid #2196F3; padding: 15px; border-radius: 8px; color: #1976D2; }
    </style>
""", unsafe_allow_html=True)

# --- 6. MOTEUR IA ---
def traiter_ia_expert(liste_brute, service):
    if not liste_brute: return [], "Aucune actualité détectée."
    data_concat = "\n".join([f"ID: {a['url']}\nTITRE: {a['title']}\nCONTENU: {a.get('body', '')}\n---" for a in liste_brute])
    
    # PROMPT AVEC FILTRE GÉOGRAPHIQUE RENFORCÉ
    prompt = f"""
    Analyse ces articles pour le service {service}.
    
    RÈGLES D'OR :
    1. GÉOGRAPHIE : Conserve UNIQUEMENT ce qui concerne la FRANCE (Métropole/DOM-TOM). Jette impitoyablement tout article parlant d'Afrique, Maghreb ou pays étrangers, même si c'est en français.
    2. DÉDOUBLONNAGE : Si plusieurs articles parlent du même événement, n'en garde qu'UN SEUL.
    
    Réponds uniquement par la liste des URLs retenues (max 4).
    Articles :
    {data_concat}
    """
    try:
        response = model.generate_content(prompt).text
        urls_uniques = [u.strip() for u in response.strip().split("\n") if "http" in u]
        final_list = [a for a in liste_brute if a['url'] in urls_uniques]
        return final_list[:4], "Analyse IA : Fonctionnalité en cours de développement."
    except:
        return liste_brute[:4], "Analyse IA : Fonctionnalité en cours de développement."

# --- 7. INITIALISATION & SIDEBAR ---
if 'sujets' not in st.session_state:
    st.session_state['sujets'] = list(MOTS_CLES_STRATEGIQUES.keys())
if 'last_results' not in st.session_state:
    st.session_state['last_results'] = {}

with st.sidebar:
    st.markdown("### ⚖️ PYXIS SUPPORT")
    st.write("---")
    for s in st.session_state['sujets']:
        c1, c2 = st.columns([5, 1.2])
        c1.write(s)
        if c2.button("X", key=f"d_{s}"):
            st.session_state['sujets'].remove(s); st.rerun()

st.markdown('<h1 class="main-title">Veille Stratégique Opérationnelle</h1>', unsafe_allow_html=True)

# --- 8. LOGIQUE PRINCIPALE ---
if st.button("LANCER LA VEILLE INTELLIGENTE 🚀", use_container_width=True):
    st.session_state['last_results'] = {}
    
    for sujet in st.session_state['sujets']:
        with st.status(f"Analyse en cours : {sujet}...", expanded=False) as status:
            query = MOTS_CLES_STRATEGIQUES.get(sujet, sujet)
            raw = []
            success = False
            
            for attempt in range(2):
                try:
                    with DDGS() as ddgs:
                        raw = list(ddgs.news(query, region="fr-fr", timelimit="w", max_results=25))
                    if raw:
                        success = True; break
                except:
                    time.sleep(5); continue
            
            time.sleep(1.5)

            if success:
                # 1. FILTRE IA (Sémantique & Géographique)
                actus_ia, message_ia = traiter_ia_expert(raw, sujet)
                
                # 2. FILTRE TECHNIQUE (Liens Morts) - On ne vérifie que les élus par l'IA pour gagner du temps
                actus_valides = []
                for article in actus_ia:
                    # On teste le lien. Si OK, on garde.
                    if verifier_lien_actif(article['url']):
                        actus_valides.append(article)
                
                st.session_state['last_results'][sujet] = {
                    'articles': actus_valides,
                    'analysis': message_ia
                }
                status.update(label=f"✅ {sujet} terminé ({len(actus_valides)} articles)", state="complete")
            else:
                st.session_state['last_results'][sujet] = {
                    'articles': [],
                    'analysis': "Flux indisponible."
                }
                status.update(label=f"❌ {sujet} saturé.", state="error")
    
    st.rerun()

# AFFICHAGE PERSISTANT
if st.session_state['last_results']:
    try:
        pdf_data = generer_pdf(st.session_state['last_results'])
        st.download_button(
            label="📥 TÉLÉCHARGER LE RAPPORT COMPLET (PDF)",
            data=pdf_data,
            file_name=f"Veille_Pyxis_{datetime.now().strftime('%d_%m_%Y')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Erreur PDF : {e}")

    for sujet, data in st.session_state['last_results'].items():
        st.markdown(f'<div class="titre-service">📌 {sujet}</div>', unsafe_allow_html=True)
        actus = data['articles']
        message_ia = data['analysis']
        col1, col2 = st.columns([1, 1.4])
        with col1:
            st.markdown(f'<div class="analyse-box">💡 <b>{message_ia}</b></div>', unsafe_allow_html=True)
        with col2:
            if not actus:
                st.info("Aucun article pertinent ou lien valide identifié.")
            for a in actus:
                st.markdown(f"""<div class="article-card">
                    <a href="{a['url']}" target="_blank" style="text-decoration:none; color:black;"><b>{a['title']}</b></a><br>
                    <small>{a['source']}</small></div>""", unsafe_allow_html=True)
