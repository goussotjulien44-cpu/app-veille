import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai
import time
from fpdf import FPDF
from datetime import datetime
import requests

# --- 1. CONFIGURATION IA ---
if "API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["API_KEY"])
    generation_config = {"temperature": 0.0, "top_p": 1, "top_k": 1}
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config=generation_config)
else:
    st.error("ERREUR : Clé 'API_KEY' manquante dans les secrets.")

st.set_page_config(page_title="Veille Pyxis Support", layout="wide")

# --- 2. DICTIONNAIRE DE RECHERCHE (AVEC FILTRE FRANCE STRICT) ---
MOTS_CLES_STRATEGIQUES = {
    "Mobilités (Ferroviaire & Aéroportuaire)": "SNCF OR RER OR RATP OR 'Loi-cadre' OR 'Loi de programmation' OR 'Financement rail' OR 'Tramway'",
    "Externalisation (Marchés Publics & AMO)": "BOAMP OR 'Marchés publics' OR 'Commande publique' OR 'Conseil d'Etat' OR 'Assistance à maîtrise d'ouvrage' OR AMO -Afrique -Sénégal -Maroc -Algérie -Tunisie -Cameroun -Côte d'Ivoire",
    "IT & Systèmes d'Information": "'Systèmes d'information' OR 'Infrastructure IT' OR 'Transformation digitale' OR 'Cybersécurité' OR 'Logiciel métier'",
    "Digitalisation & IA": "'Intelligence artificielle' OR 'IA générative' OR 'Digitalisation' OR 'Souveraineté numérique'",
    "Vente SaaS & Commerciaux MA-IA": "'Vente SaaS' OR 'Logiciel par abonnement' OR 'Salesforce' OR 'Solution cloud'",
    "Développement Software": "'Développement logiciel' OR 'DevOps' OR 'Cloud computing' OR 'Logiciel libre'",
    "Administration, RH & DAF": "'Réforme RH' OR 'Gestion administrative' OR 'Finance d'entreprise' OR 'Externalisation RH'"
}

# --- 3. FONCTION TECHNIQUE : VÉRIFICATION DES LIENS ---
def verifier_lien_actif(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'}
    try:
        # On nettoie l'URL avant de tester
        url_clean = str(url).strip()
        response = requests.head(url_clean, headers=headers, timeout=3, allow_redirects=True)
        return response.status_code < 400
    except:
        return False

# --- 4. CLASSE PDF : GÉNÉRATION DU RAPPORT ---
class PyxisPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 10, 'VEILLE STRATÉGIQUE PYXIS SUPPORT', 0, 1, 'C')
        self.set_font('Helvetica', '', 10)
        self.cell(0, 10, f'Généré le : {datetime.now().strftime("%d/%m/%Y à %H:%M")}', 0, 1, 'C')
        self.ln(10)
        self.set_draw_color(197, 160, 89) # Or Pyxis
        self.line(10, 32, 200, 32)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generer_pdf(resultats_complets):
    pdf = PyxisPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    for service, data in resultats_complets.items():
        articles = data['articles']
        
        # Titre de la section
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_fill_color(240, 242, 246)
        pdf.cell(0, 10, f" SECTION : {service.upper()} ", 0, 1, 'L', fill=True)
        pdf.ln(2)
        
        if not articles:
            pdf.set_font('Helvetica', 'I', 10)
            pdf.cell(0, 10, "Aucun article pertinent sélectionné.", 0, 1)
        else:
            for art in articles:
                # NETTOYAGE CRUCIAL DU LIEN (Correction ERR_FILE_NOT_FOUND)
                raw_url = str(art['url']).strip()
                
                # NETTOYAGE DU TITRE (ASCII pour éviter les bugs d'encodage PDF)
                titre_brut = art['title'].replace("’", "'").replace("“", '"').replace("”", '"')
                titre_pdf = titre_brut.encode('latin-1', 'replace').decode('latin-1')

                # Titre cliquable
                pdf.set_font('Helvetica', 'B', 10)
                pdf.set_text_color(0, 0, 255) 
                pdf.multi_cell(0, 6, f"- {titre_pdf}", 0, 'L', link=raw_url)
                
                # Source
                pdf.set_font('Helvetica', '', 9)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 5, f"Source : {art['source']}", 0, 1)
                pdf.ln(2)
        pdf.ln(5)
    
    return bytes(pdf.output())

# --- 5. INTERFACE (CSS) ---
st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF !important; }
        .main-title { color: #000; font-size: 35px; font-weight: 900; text-align: center; margin-bottom: 30px; }
        .titre-service { color: #000; font-weight: 900; font-size: 18px; border-bottom: 3px solid #C5A059; margin-top: 25px; }
        .article-card { background-color: #fdfdfd; padding: 12px; border: 1px solid #ddd; border-left: 8px solid #C5A059; border-radius: 5px; margin-bottom: 8px; }
        .analyse-box { background-color: #E3F2FD; border: 1px solid #2196F3; padding: 15px; border-radius: 8px; color: #1976D2; }
    </style>
""", unsafe_allow_html=True)

# --- 6. INTELLIGENCE ARTIFICIELLE (FILTRAGE) ---
def traiter_ia_expert(liste_brute, service):
    if not liste_brute: return [], "Aucune donnée."
    
    data_concat = "\n".join([f"ID: {a['url']}\nTITRE: {a['title']}\n---" for a in liste_brute])
    
    prompt = f"""
    En tant qu'expert en veille stratégique pour le cabinet Pyxis (France), analyse ces articles pour le pôle : {service}.
    
    CONSIGNES IMPÉRATIVES :
    1. EXCLUSION GÉOGRAPHIQUE : Supprime TOUT ce qui ne concerne pas la FRANCE métropolitaine ou les DOM-TOM. Rejette l'Afrique, le Maghreb, le Canada, etc.
    2. DÉDOUBLONNAGE : Si un sujet est très repris (ex: Loi-cadre), ne garde que l'article le plus pertinent.
    3. QUALITÉ : Garde maximum 4 liens.
    
    Réponds uniquement avec la liste des URLs retenues.
    Articles :
    {data_concat}
    """
    try:
        response = model.generate_content(prompt).text
        urls_uniques = [u.strip() for u in response.strip().split("\n") if "http" in u]
        final_list = [a for a in liste_brute if a['url'] in urls_uniques]
        return final_list[:4], "Analyse IA : Filtrage géographique et thématique effectué."
    except:
        return liste_brute[:4], "Analyse IA : Mode dégradé (Erreur API)."

# --- 7. LOGIQUE DE SESSION ET AFFICHAGE ---
if 'last_results' not in st.session_state:
    st.session_state['last_results'] = {}
if 'sujets' not in st.session_state:
    st.session_state['sujets'] = list(MOTS_CLES_STRATEGIQUES.keys())

with st.sidebar:
    st.markdown("### ⚖️ PYXIS SUPPORT")
    st.write("---")
    for s in st.session_state['sujets']:
        c1, c2 = st.columns([5, 1.2])
        c1.write(s)
        if c2.button("X", key=f"d_{s}"):
            st.session_state['sujets'].remove(s); st.rerun()

st.markdown('<h1 class="main-title">Veille Stratégique Opérationnelle</h1>', unsafe_allow_html=True)

# BOUTON DE LANCEMENT
if st.button("LANCER LA VEILLE GÉNÉRALE 🚀", use_container_width=True):
    st.session_state['last_results'] = {}
    
    for sujet in st.session_state['sujets']:
        with st.status(f"Recherche : {sujet}...", expanded=False) as status:
            query = MOTS_CLES_STRATEGIQUES.get(sujet, sujet)
            raw = []
            
            try:
                with DDGS() as ddgs:
                    raw = list(ddgs.news(query, region="fr-fr", timelimit="w", max_results=25))
            except:
                time.sleep(2) # Anti-ban
            
            if raw:
                # 1. Filtre IA
                actus_ia, msg = traiter_ia_expert(raw, sujet)
                # 2. Filtre Liens Morts
                actus_finales = [a for a in actus_ia if verifier_lien_actif(a['url'])]
                
                st.session_state['last_results'][sujet] = {
                    'articles': actus_finales,
                    'analysis': msg
                }
                status.update(label=f"✅ {sujet} : OK", state="complete")
            else:
                st.session_state['last_results'][sujet] = {'articles': [], 'analysis': "Aucun résultat trouvé."}
                status.update(label=f"❌ {sujet} : Aucun résultat", state="error")
            
            time.sleep(2) # Pause pour DuckDuckGo

    st.rerun()

# AFFICHAGE DES RÉSULTATS (PERSISTANT)
if st.session_state['last_results']:
    
    # 1. Zone Export PDF
    try:
        pdf_bytes = generer_pdf(st.session_state['last_results'])
        st.download_button(
            label="📥 TÉLÉCHARGER LE RAPPORT PDF (LIENS SÉCURISÉS)",
            data=pdf_bytes,
            file_name=f"Veille_Pyxis_{datetime.now().strftime('%d_%m_%Y')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Erreur lors de la préparation du PDF : {e}")

    # 2. Affichage écran
    for sujet, data in st.session_state['last_results'].items():
        st.markdown(f'<div class="titre-service">📌 {sujet}</div>', unsafe_allow_html=True)
        col_ia, col_art = st.columns([1, 1.4])
        
        with col_ia:
            st.markdown(f'<div class="analyse-box">💡 {data["analysis"]}</div>', unsafe_allow_html=True)
            
        with col_art:
            if not data['articles']:
                st.info("Aucun article retenu pour ce pôle.")
            for a in data['articles']:
                st.markdown(f"""
                <div class="article-card">
                    <a href="{a['url']}" target="_blank" style="text-decoration:none; color:black; font-weight:bold;">
                        {a['title']}
                    </a><br>
                    <small style="color:gray;">Source : {a['source']}</small>
                </div>
                """, unsafe_allow_html=True)
