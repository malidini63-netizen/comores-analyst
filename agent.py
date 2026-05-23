import os
from pathlib import Path
from groq import Groq
from prompts import SYSTEM_PROMPT, build_user_prompt
from web_scraper import gather_intelligence
from dotenv import load_dotenv

try:
    from telegram_bot import send_telegram_alert
except ImportError:
    def send_telegram_alert(q, a, p):
        return {"sent": False, "status": "Module telegram non disponible", "critical": False}

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)


class ComorosAnalyst:
    """Agent d'analyse stratégique sur les Comores avec veille temps réel."""

    def __init__(self):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY manquante")
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"

    def analyze(self, query: str, params: dict, use_web: bool = True) -> tuple:
        """
        Lance une analyse complète avec veille web optionnelle.

        Args:
            query: Question de l'utilisateur
            params: Paramètres (angle, influences, horizon, secteur)
            use_web: Active la veille temps réel

        Returns:
            (analyse_markdown, telegram_result, intel_summary)
        """
        # 1. Collecte des infos temps réel
        intel = None
        if use_web:
            try:
                intel = gather_intelligence(query, max_articles=10)
            except Exception as e:
                intel = {"count": 0, "formatted_context": "", "timestamp": ""}

        # 2. Construction du prompt enrichi
        user_prompt = build_user_prompt(query, params, intel)

        # 3. Appel LLM
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4,
                max_tokens=4096,
            )
            analysis = response.choices[0].message.content

            # 4. Alerte Telegram si critique
            telegram_result = send_telegram_alert(query, analysis, params)

            return analysis, telegram_result, intel

        except Exception as e:
            error_msg = f"❌ **Erreur** : {str(e)}"
            return error_msg, {"sent": False, "status": str(e), "critical": False}, intel
