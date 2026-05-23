import os, re, requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

CRITICAL_KEYWORDS = [
    "coup d etat","instabilite","radicalisation","destabilisation",
    "crise diplomatique","conflit","tensions","sécession",
    "dette souveraine","défaut","faillite","effondrement",
    "opportunite majeure","fort potentiel","investissement strategique",
    "BRI","routes de la soie","base militaire","sanctions",
]

def is_critical(text):
    tl = text.lower()
    matches = [k for k in CRITICAL_KEYWORDS if k.lower() in tl]
    return len(matches) >= 3 or "🔴" in text

def extract_risk_level(text):
    if "🔴" in text: return "🔴 CRITIQUE"
    elif "🟠" in text: return "🟠 ÉLEVÉ"
    elif "🟡" in text: return "🟡 MODÉRÉ"
    return "🟢 FAIBLE"

def send_telegram_alert(query, analysis_text, params):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return {"sent": False, "status": "Token Telegram non configuré", "critical": False}
    critical = is_critical(analysis_text)
    if not critical:
        return {"sent": False, "status": "Analyse non critique — pas d alertes", "critical": False}
    risk = extract_risk_level(analysis_text)
    tl = analysis_text.lower()
    keywords = [k for k in CRITICAL_KEYWORDS if k.lower() in tl]
    ts = datetime.now().strftime("%d/%m/%Y à %H:%M")
    msg = f"🏝️ *ALERTE Comores Analyst*\n━━━━━━━━━━━━\n⚡ Risque : {risk}\n📅 {ts}\n\n❓ _{query[:120]}_\n\n🔑 Signaux ({len(keywords)}) :\n" + "\n".join(f"• {k}" for k in keywords[:5])
    try:
        r = requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
        if r.status_code == 200:
            return {"sent": True, "status": f"Alerte envoyée ({len(keywords)} signaux)", "critical": True, "keywords": keywords}
        return {"sent": False, "status": f"Erreur {r.status_code}", "critical": True}
    except Exception as e:
        return {"sent": False, "status": str(e), "critical": True}

def test_telegram_connection():
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return {"success": False, "message": "TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID manquant"}
    try:
        r = requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": "🏝️ Comores Analyst — Connexion OK ✅", "parse_mode": "Markdown"}, timeout=10)
        if r.status_code == 200:
            return {"success": True, "message": "✅ Message de test envoyé"}
        return {"success": False, "message": r.json().get("description", "Erreur")}
    except Exception as e:
        return {"success": False, "message": str(e)}
