import os
from groq import Groq
from prompts import SYSTEM_PROMPT, build_user_prompt
from dotenv import load_dotenv

load_dotenv()


class ComorosAnalyst:
    """Agent d'analyse stratégique sur les Comores."""

    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"

    def analyze(self, query: str, params: dict) -> str:
        """
        Lance une analyse complète basée sur la question et les paramètres.
        
        Args:
            query: La question de l'utilisateur
            params: Dict avec angle, influences, horizon, secteur
        
        Returns:
            Analyse formatée en Markdown
        """
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
            return response.choices[0].message.content

        except Exception as e:
            return f"❌ **Erreur d'analyse** : {str(e)}\n\nVérifiez votre clé API GROQ dans le fichier `.env`."
