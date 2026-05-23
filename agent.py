import os
from pathlib import Path
from groq import Groq
from prompts import SYSTEM_PROMPT, build_user_prompt
from dotenv import load_dotenv

try:
    from telegram_bot import send_telegram_alert
except ImportError:
    def send_telegram_alert(q, a, p):
        return {"sent": False, "status": "Module telegram non disponible", "critical": False}

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)


class ComorosAnalyst:
    """Agent d'analyse stratégique sur les Comores."""

    def __init__(self):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY manquante")
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"

    def analyze(self, query: str, params: dict) -> tuple:
        user_prompt = build_user_prompt(query, params)
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
            telegram_result = send_telegram_alert(query, analysis, params)
            return analysis, telegram_result
        except Exception as e:
            return f"❌ Erreur : {str(e)}", {"sent": False, "status": str(e), "critical": False}
