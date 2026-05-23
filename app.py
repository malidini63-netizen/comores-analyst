import streamlit as st
from agent import ComorosAnalyst
from web_scraper import format_for_display
from telegram_bot import test_telegram_connection
from datetime import datetime
import json

st.set_page_config(page_title="Comores Analyst", page_icon="🏝️",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Playfair Display', serif; }
.main-title { font-family: 'Playfair Display', serif; font-size: 2.4rem; color: #1a3a5c; }
.subtitle { color: #6b8fa3; font-size: 0.95rem; font-weight: 300; margin-top: -10px; }
.section-tag { display: inline-block; background: #e8f4fd; color: #1a3a5c; padding: 3px 10px; border-radius: 4px; font-size: 0.78rem; font-weight: 500; text-transform: uppercase; letter-spacing: 1px; margin: 4px 2px; }
.intel-box { background: #f0f7ff; border-left: 4px solid #2196F3; padding: 12px 16px; border-radius: 0 8px 8px 0; margin: 8px 0; font-size: 0.85rem; }
.alert-critical { background: #f8d7da; border-left: 4px solid #dc3545; padding: 12px 16px; border-radius: 0 8px 8px 0; margin: 8px 0; }
.alert-ok { background: #d1e7dd; border-left: 4px solid #198754; padding: 12px 16px; border-radius: 0 8px 8px 0; margin: 8px 0; }
.stButton > button { background: #1a3a5c !important; color: white !important; border-radius: 8px !important; border: none !important; font-weight: 500 !important; }
.stButton > button:hover { background: #2196F3 !important; }
div[data-testid="stSidebarContent"] { background: #f0f6fb; }
.history-item { background: white; border: 1px solid #dce8f0; border-radius: 8px; padding: 10px 14px; margin: 6px 0; font-size: 0.85rem; }
.source-chip { display: inline-block; background: #e3f2fd; color: #1565c0; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; margin: 2px; }
</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE ────────────────────────────────────────────────────────────
for key, default in [("history", []), ("last_result", None),
                      ("last_telegram", None), ("last_intel", None)]:
    if key not in st.session_state:
        st.session_state[key] = default

if "analyst" not in st.session_state:
    st.session_state.analyst = ComorosAnalyst()

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏝️ Comores Analyst")
    st.markdown("---")

    st.markdown("**🎯 Angle d'analyse**")
    angle = st.selectbox("Angle", ["Tous les angles", "Politique", "Économique",
        "Humain & Sociétal", "Opportunités d'investissement", "Risques"],
        label_visibility="collapsed")

    st.markdown("**🌐 Influences extérieures**")
    influences = st.multiselect("Influences",
        ["Relations franco-comoriennes", "Pays du Golfe", "Pays BRICS",
         "Pays voisins / Océan Indien", "Organisations internationales"],
        default=["Relations franco-comoriennes", "Pays du Golfe"],
        label_visibility="collapsed")

    st.markdown("**⏱️ Horizon temporel**")
    horizon = st.select_slider("Horizon",
        options=["Court terme (1-3 ans)", "Moyen terme (3-7 ans)",
                 "Long terme (7-15 ans)", "Tous horizons"],
        value="Tous horizons", label_visibility="collapsed")

    st.markdown("**🏭 Secteur cible**")
    secteur = st.selectbox("Secteur",
        ["Tous secteurs", "Tourisme & Hôtellerie", "Agro-industrie",
         "Économie bleue & Pêche", "Énergies renouvelables", "Numérique & Fintech",
         "Immobilier & BTP", "Santé & Éducation", "Commerce & Import-Export",
         "Finance islamique"], label_visibility="collapsed")

    st.markdown("---")

    # ─── VEILLE WEB ──────────────────────────────────────────────────────────
    st.markdown("**📡 Veille temps réel**")
    use_web = st.toggle("Activer la veille web & réseaux sociaux", value=True)

    if use_web:
        st.markdown("""<div class="intel-box">
            <b>Sources scrutées :</b><br>
            📰 Al-Watwan, HZK-Presse, Masiwa<br>
            🌐 DuckDuckGo News (actualités récentes)<br>
            💬 Reddit, forums francophones
        </div>""", unsafe_allow_html=True)

        if st.session_state.last_intel:
            intel = st.session_state.last_intel
            st.markdown(f"""<div class="intel-box">
                {format_for_display(intel).replace(chr(10), '<br>')}
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ─── TELEGRAM ────────────────────────────────────────────────────────────
    st.markdown("**📱 Alertes Telegram**")
    with st.expander("⚙️ Configuration", expanded=False):
        st.markdown("""<small>Alertes automatiques sur signaux critiques :<br>
        🔴 Coup d'état / instabilité<br>
        • Crise diplomatique<br>
        • Dette souveraine / défaut<br>
        • Radicalisation / conflit<br>
        • Opportunité majeure (3+ signaux)</small>""", unsafe_allow_html=True)
        st.markdown("")
        if st.button("🧪 Tester la connexion", use_container_width=True):
            with st.spinner("Test..."):
                result = test_telegram_connection()
            if result["success"]:
                st.success(result["message"])
            else:
                st.error(result["message"])

    st.markdown("---")
    st.markdown("**📋 Historique**")
    for item in reversed(st.session_state.history[-5:]):
        icons = ""
        if item.get("intel", {}).get("count", 0) > 0:
            icons += "📡"
        if item.get("telegram", {}).get("sent"):
            icons += "📨"
        else:
            icons += "💬"
        st.markdown(f"""<div class="history-item">
            {icons} <b>{item['timestamp']}</b><br>{item['query'][:55]}...
        </div>""", unsafe_allow_html=True)

    if st.session_state.history:
        if st.button("🗑️ Effacer", use_container_width=True):
            for k in ["history", "last_result", "last_telegram", "last_intel"]:
                st.session_state[k] = [] if k == "history" else None
            st.rerun()

# ─── MAIN ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<p class="main-title">🏝️ Comores Strategic Analyst</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Analyses politiques · Économiques · Humaines · Veille temps réel · Alertes Telegram</p>', unsafe_allow_html=True)
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<small style='color:#6b8fa3'>📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}</small>", unsafe_allow_html=True)

st.markdown("---")

# ─── QUICK PROMPTS ───────────────────────────────────────────────────────────
st.markdown("**⚡ Analyses rapides**")
q_cols = st.columns(4)
quick_queries = {
    "🏨 Tourisme 2030": "Analyse le potentiel touristique des Comores à horizon 2030",
    "🇨🇳 Influence Chine": "Impact réel des investissements chinois BRI sur les Comores",
    "💰 Diaspora → Invest.": "Transformer les transferts diaspora comorienne en investissements",
    "⚡ Énergie renouvelable": "Opportunités énergies renouvelables aux Comores : solaire éolien géothermie",
}
selected_quick = None
for i, (label, query) in enumerate(quick_queries.items()):
    with q_cols[i]:
        if st.button(label, use_container_width=True):
            selected_quick = query

st.markdown("---")
st.markdown("**🔍 Votre question d'analyse**")
query = st.text_area("Question", value=selected_quick or "",
    placeholder="Ex: Quelles opportunités dans l'agro-industrie compte tenu des relations avec le Golfe ?",
    height=120, label_visibility="collapsed")

col1b, col2b, col3b = st.columns([2, 1, 1])
with col1b:
    run_btn = st.button("🚀 Lancer l'analyse", use_container_width=True)
with col2b:
    export_btn = st.button("📥 Exporter JSON", use_container_width=True,
                           disabled=st.session_state.last_result is None)
with col3b:
    if st.button("🔄 Réinitialiser", use_container_width=True):
        for k in ["last_result", "last_telegram", "last_intel"]:
            st.session_state[k] = None
        st.rerun()

# ─── RUN ─────────────────────────────────────────────────────────────────────
if run_btn and query.strip():
    params = {"angle": angle, "influences": influences, "horizon": horizon, "secteur": secteur}

    with st.spinner("📡 Collecte des actualités en cours..." if use_web else "⏳ Analyse en cours..."):
        result, telegram_result, intel = st.session_state.analyst.analyze(query, params, use_web)

    st.session_state.last_result = result
    st.session_state.last_telegram = telegram_result
    st.session_state.last_intel = intel
    st.session_state.history.append({
        "timestamp": datetime.now().strftime("%H:%M"),
        "query": query, "params": params,
        "result": result, "telegram": telegram_result, "intel": intel
    })
    st.rerun()

elif run_btn:
    st.warning("⚠️ Veuillez entrer une question.")

# ─── DISPLAY ─────────────────────────────────────────────────────────────────
if st.session_state.last_result:
    result = st.session_state.last_result
    telegram = st.session_state.last_telegram or {}
    intel = st.session_state.last_intel

    st.markdown("---")

    # Bandeau veille
    if intel and intel.get("count", 0) > 0:
        sources = [a["source"] for a in intel.get("articles", [])[:4]]
        chips = " ".join(f'<span class="source-chip">{s}</span>' for s in sources)
        st.markdown(f"""<div class="intel-box">
            📡 <b>{intel['count']} sources analysées</b> · {intel['timestamp']}<br>
            {chips}
        </div>""", unsafe_allow_html=True)

    # Bandeau Telegram
    if telegram.get("sent"):
        keywords = telegram.get("keywords", [])
        st.markdown(f"""<div class="alert-critical">
            📨 <b>Alerte Telegram envoyée</b> — {len(keywords)} signaux critiques détectés
        </div>""", unsafe_allow_html=True)
    elif not telegram.get("critical"):
        st.markdown(f"""<div class="alert-ok">
            ✅ {telegram.get('status', 'Analyse normale')}
        </div>""", unsafe_allow_html=True)

    st.markdown("## 📊 Résultats de l'analyse")

    # Tags
    params = st.session_state.history[-1]["params"]
    tags = ""
    if params.get("angle") != "Tous les angles":
        tags += f'<span class="section-tag">{params["angle"]}</span>'
    for inf in params.get("influences", []):
        tags += f'<span class="section-tag">{inf}</span>'
    if tags:
        st.markdown(tags + "<br>", unsafe_allow_html=True)

    st.markdown(result)

    if export_btn:
        st.download_button("⬇️ Télécharger",
            data=json.dumps({"timestamp": datetime.now().isoformat(),
                "query": st.session_state.history[-1]["query"],
                "params": params, "analysis": result,
                "sources_count": intel.get("count", 0) if intel else 0,
                "telegram": telegram}, ensure_ascii=False, indent=2),
            file_name=f"comores_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json")
else:
    st.markdown("""<div style='text-align:center;padding:60px 20px;color:#6b8fa3;'>
        <div style='font-size:3rem'>🏝️</div>
        <div style='font-family:Playfair Display,serif;font-size:1.4rem;color:#1a3a5c;margin:10px 0'>
            Prêt à analyser les Comores</div>
        <div style='font-size:0.9rem'>Veille temps réel activée · Alertes Telegram configurées</div>
    </div>""", unsafe_allow_html=True)
