import streamlit as st
from agent import ComorosAnalyst
from datetime import datetime
import json

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Comores Analyst",
    page_icon="🏝️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
h1, h2, h3 {
    font-family: 'Playfair Display', serif;
}
.main-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.4rem;
    color: #1a3a5c;
    letter-spacing: -0.5px;
}
.subtitle {
    color: #6b8fa3;
    font-size: 0.95rem;
    font-weight: 300;
    margin-top: -10px;
}
.section-tag {
    display: inline-block;
    background: #e8f4fd;
    color: #1a3a5c;
    padding: 3px 10px;
    border-radius: 4px;
    font-size: 0.78rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 4px 2px;
}
.analysis-card {
    background: #f9fbfd;
    border-left: 4px solid #2196F3;
    padding: 16px 20px;
    border-radius: 0 8px 8px 0;
    margin: 12px 0;
}
.risk-badge {
    background: #fff3cd;
    border: 1px solid #ffc107;
    color: #856404;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.78rem;
}
.opportunity-badge {
    background: #d1e7dd;
    border: 1px solid #198754;
    color: #0f5132;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.78rem;
}
.stTextArea textarea {
    border-radius: 8px !important;
    border: 1px solid #c9dde8 !important;
    font-family: 'Inter', sans-serif !important;
}
.stButton > button {
    background: #1a3a5c !important;
    color: white !important;
    border-radius: 8px !important;
    border: none !important;
    font-weight: 500 !important;
    padding: 0.5rem 2rem !important;
}
.stButton > button:hover {
    background: #2196F3 !important;
}
div[data-testid="stSidebarContent"] {
    background: #f0f6fb;
}
.history-item {
    background: white;
    border: 1px solid #dce8f0;
    border-radius: 8px;
    padding: 10px 14px;
    margin: 6px 0;
    font-size: 0.85rem;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE ────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "analyst" not in st.session_state:
    st.session_state.analyst = ComorosAnalyst()

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏝️ Comores Analyst")
    st.markdown("---")

    st.markdown("**🎯 Angle d'analyse**")
    angle = st.selectbox(
        "Dimension principale",
        ["Tous les angles", "Politique", "Économique", "Humain & Sociétal",
         "Opportunités d'investissement", "Risques"],
        label_visibility="collapsed"
    )

    st.markdown("**🌐 Influences extérieures**")
    influences = st.multiselect(
        "Acteurs à intégrer",
        ["Relations franco-comoriennes", "Pays du Golfe", "Pays BRICS",
         "Pays voisins / Océan Indien", "Organisations internationales"],
        default=["Relations franco-comoriennes", "Pays du Golfe"],
        label_visibility="collapsed"
    )

    st.markdown("**⏱️ Horizon temporel**")
    horizon = st.select_slider(
        "Projection",
        options=["Court terme (1-3 ans)", "Moyen terme (3-7 ans)", "Long terme (7-15 ans)", "Tous horizons"],
        value="Tous horizons",
        label_visibility="collapsed"
    )

    st.markdown("**📊 Secteur cible**")
    secteur = st.selectbox(
        "Secteur",
        ["Tous secteurs", "Tourisme & Hôtellerie", "Agro-industrie",
         "Économie bleue & Pêche", "Énergies renouvelables", "Numérique & Fintech",
         "Immobilier & BTP", "Santé & Éducation", "Commerce & Import-Export",
         "Finance islamique"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("**📋 Historique**")
    for i, item in enumerate(reversed(st.session_state.history[-5:])):
        st.markdown(f"""<div class="history-item">
            <b>{item['timestamp']}</b><br>
            {item['query'][:60]}...
        </div>""", unsafe_allow_html=True)

    if st.session_state.history:
        if st.button("🗑️ Effacer l'historique", use_container_width=True):
            st.session_state.history = []
            st.session_state.last_result = None
            st.rerun()

# ─── MAIN ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<p class="main-title">🏝️ Comores Strategic Analyst</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Analyses politiques · Économiques · Humaines · Opportunités d\'investissement</p>',
                unsafe_allow_html=True)

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    ts = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.markdown(f"<small style='color:#6b8fa3'>📅 {ts}</small>", unsafe_allow_html=True)

st.markdown("---")

# ─── QUICK PROMPTS ───────────────────────────────────────────────────────────
st.markdown("**⚡ Analyses rapides**")
q_cols = st.columns(4)
quick_queries = {
    "🏨 Tourisme 2030": "Analyse le potentiel touristique des Comores à horizon 2030 avec les opportunités d'investissement concrètes",
    "🇨🇳 Influence Chine": "Quel est l'impact réel des investissements chinois (BRI) sur l'économie et la gouvernance comorienne ?",
    "💰 Diaspora → Invest.": "Comment transformer les transferts de la diaspora comorienne en investissements productifs structurés ?",
    "⚡ Énergie renouvelable": "Analyse les opportunités dans les énergies renouvelables aux Comores : solaire, éolien, géothermie",
}

selected_quick = None
for i, (label, query) in enumerate(quick_queries.items()):
    with q_cols[i]:
        if st.button(label, use_container_width=True):
            selected_quick = query

st.markdown("---")

# ─── INPUT ZONE ──────────────────────────────────────────────────────────────
st.markdown("**🔍 Votre question d'analyse**")
default_query = selected_quick if selected_quick else ""
query = st.text_area(
    "Question",
    value=default_query,
    placeholder="Ex: Quelles sont les meilleures opportunités d'investissement dans le secteur agro-industriel aux Comores compte tenu des relations avec les pays du Golfe ?",
    height=120,
    label_visibility="collapsed"
)

col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
with col_btn1:
    run_analysis = st.button("🚀 Lancer l'analyse", use_container_width=True)
with col_btn2:
    export_btn = st.button("📥 Exporter JSON", use_container_width=True,
                           disabled=st.session_state.last_result is None)
with col_btn3:
    clear_btn = st.button("🔄 Réinitialiser", use_container_width=True)

if clear_btn:
    st.session_state.last_result = None
    st.rerun()

# ─── RUN ANALYSIS ────────────────────────────────────────────────────────────
if run_analysis and query.strip():
    with st.spinner("⏳ Analyse en cours..."):
        params = {
            "angle": angle,
            "influences": influences,
            "horizon": horizon,
            "secteur": secteur
        }
        result = st.session_state.analyst.analyze(query, params)
        st.session_state.last_result = result
        st.session_state.history.append({
            "timestamp": datetime.now().strftime("%H:%M"),
            "query": query,
            "params": params,
            "result": result
        })
    st.rerun()

elif run_analysis and not query.strip():
    st.warning("⚠️ Veuillez entrer une question d'analyse.")

# ─── DISPLAY RESULT ──────────────────────────────────────────────────────────
if st.session_state.last_result:
    result = st.session_state.last_result
    st.markdown("---")
    st.markdown("## 📊 Résultats de l'analyse")

    # Tags paramètres
    params = st.session_state.history[-1]["params"] if st.session_state.history else {}
    if params:
        tags_html = ""
        if params.get("angle") != "Tous les angles":
            tags_html += f'<span class="section-tag">{params["angle"]}</span>'
        for inf in params.get("influences", []):
            tags_html += f'<span class="section-tag">{inf}</span>'
        if params.get("secteur") != "Tous secteurs":
            tags_html += f'<span class="section-tag">{params["secteur"]}</span>'
        st.markdown(tags_html, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # Affichage du résultat
    st.markdown(result)

    # Export
    if export_btn:
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "query": st.session_state.history[-1]["query"],
            "params": params,
            "analysis": result
        }
        st.download_button(
            label="⬇️ Télécharger l'analyse",
            data=json.dumps(export_data, ensure_ascii=False, indent=2),
            file_name=f"comores_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json"
        )

elif not st.session_state.last_result:
    st.markdown("""
    <div style='text-align:center; padding: 60px 20px; color: #6b8fa3;'>
        <div style='font-size:3rem'>🏝️</div>
        <div style='font-family: Playfair Display, serif; font-size:1.4rem; color:#1a3a5c; margin:10px 0'>
            Prêt à analyser les Comores
        </div>
        <div style='font-size:0.9rem'>
            Utilisez les analyses rapides ou posez votre propre question stratégique
        </div>
    </div>
    """, unsafe_allow_html=True)
