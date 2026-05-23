import os
import re
import requests
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# ─── MOTS-CLÉS DÉCLENCHEURS D'ALERTE ────────────────────────────────────────
CRITICAL_KEYWORDS = [
    # Risques sécuritaires
    "coup d'état", "instabilité", "radicalisation", "déstabilisation",
    "crise diplomatique", "conflit", "tensions", "sécession",
    # Risques économiques
    "dette souveraine", "défaut", "faillite", "effondrement",
    "crise financière", "dévaluation", "inflation élevée",
    # Opportunités majeures
    "opportunité majeure", "fort potentiel", "investissement stratégique",
    "fenêtre temporelle", "première mover", "niche inexploitée",
    # Géopolitique
    "BRI", "routes de la soie", "base militaire", "embargo",
    "sanctions", "rupture diplomatique",
]

RISK_LEVELS = {
    "🔴": "CRITIQUE",
    "🟠": "ÉLEVÉ",
    "🟡": "MOYEN",
}


def is_critical(analysis_text: str) -> bool:
    """Détecte si une analyse contient des signaux critiques."""
    text_lower = analysis_text.lower()
    matches = [kw for kw in CRITICAL_KEYWORDS if kw.lower() in text_lower]
    has_red_risk = "🔴" in analysis_text
    return len(matches) >= 3 or has_red_risk


def extract_summary(analysis_text: str, query: str, max_chars: int = 800) -> str:
    """Extrait un résumé compact de l'analyse pour Telegram."""
    lines = analysis_text.split("\n")
    summary_lines = []
    in_section = False

    priority_sections = ["CONTEXTE", "RISQUES", "OPPORTUNITÉS", "RECOMMANDATIONS"]

    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Détecte les sections prioritaires
        for section in priority_sections:
            if section in line.upper():
                in_section = True
                summary_lines.append(f"\n{line}")
                break
        else:
            if in_section and line and not line.startswith("#"):
                summary_lines.append(line)
                if len("\n".join(summary_lines)) > max_chars:
                    break

    summary = "\n".join(summary_lines[:20])
    if len(summary) > max_chars:
        summary = summary[:max_chars] + "..."
    return summary


def extract_risk_level(analysis_text: str) -> str:
    """Détermine le niveau de risque global de l'analyse."""
    if "🔴" in analysis_text:
        return "🔴 CRITIQUE"
    elif "🟠" in analysis_text:
        return "🟠 ÉLEVÉ"
    elif "🟡" in analysis_text:
        return "🟡 MODÉRÉ"
    else:
        return "🟢 FAIBLE"


def count_keywords(analysis_text: str) -> list:
    """Retourne les mots-clés critiques trouvés."""
    text_lower = analysis_text.lower()
    return [kw for kw in CRITICAL_KEYWORDS if kw.lower() in text_lower]


def send_telegram_alert(query: str, analysis_text: str, params: dict) -> dict:
    """
    Envoie une alerte Telegram si l'analyse est critique.

    Returns:
        dict avec status, sent (bool), message
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return {
            "sent": False,
            "status": "⚠️ Token Telegram non configuré dans .env",
            "critical": False
        }

    critical = is_critical(analysis_text)

    if not critical:
        return {
            "sent": False,
            "status": "✅ Analyse non critique — pas d'alerte envoyée",
            "critical": False
        }

    # Construction du message Telegram
    risk_level = extract_risk_level(analysis_text)
    summary = extract_summary(analysis_text, query)
    keywords_found = count_keywords(analysis_text)
    timestamp = datetime.now().strftime("%d/%m/%Y à %H:%M")

    # Paramètres de l'analyse
    angle = params.get("angle", "Tous angles")
    secteur = params.get("secteur", "Tous secteurs")
    horizon = params.get("horizon", "Tous horizons")

    message = f"""🏝️ *ALERTE — Comores Analyst*
━━━━━━━━━━━━━━━━━━━━
⚡ *Niveau de risque :* {risk_level}
📅 *Date :* {timestamp}

❓ *Question analysée :*
_{query[:150]}..._

📌 *Paramètres :*
• Angle : {angle}
• Secteur : {secteur}
• Horizon : {horizon}

🔑 *Signaux détectés ({len(keywords_found)}) :*
{chr(10).join(f'• {kw}' for kw in keywords_found[:6])}

📊 *Résumé de l'analyse :*
{summary}

━━━━━━━━━━━━━━━━━━━━
🤖 _Comores Strategic Analyst_"""

    # Envoi via API Telegram
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return {
                "sent": True,
                "status": f"📨 Alerte Telegram envoyée ({len(keywords_found)} signaux détectés)",
                "critical": True,
                "keywords": keywords_found
            }
        else:
            return {
                "sent": False,
                "status": f"❌ Erreur Telegram : {response.text}",
                "critical": True
            }
    except Exception as e:
        return {
            "sent": False,
            "status": f"❌ Connexion Telegram échouée : {str(e)}",
            "critical": True
        }


def test_telegram_connection() -> dict:
    """Teste la connexion Telegram avec un message de test."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return {
            "success": False,
            "message": "TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID manquant dans .env"
        }

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": "🏝️ *Comores Analyst* — Connexion Telegram opérationnelle ✅\n\n_Les alertes critiques seront envoyées ici._",
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return {"success": True, "message": "✅ Message de test envoyé avec succès"}
        else:
            return {"success": False, "message": f"Erreur : {response.json().get('description', 'Unknown')}"}
    except Exception as e:
        return {"success": False, "message": f"Connexion échouée : {str(e)}"}
