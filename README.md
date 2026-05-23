# 🏝️ Comores Strategic Analyst

Agent d'analyse stratégique sur l'Union des Comores — politique, économique, humaine et opportunités d'investissement.

## 🚀 Démarrage rapide (local)

### 1. Cloner le projet
```bash
git clone https://gitlab.com/TON_USERNAME/comores-analyst.git
cd comores-analyst
```

### 2. Créer l'environnement Python
```bash
python3.12 -m venv venv
source venv/bin/activate       # Linux/macOS
# ou : venv\Scripts\activate   # Windows
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configurer la clé API
```bash
cp .env.example .env
# Éditez .env et ajoutez votre clé GROQ :
# GROQ_API_KEY=gsk_xxxxxxxx
```
> ⚠️ Pas de guillemets autour de la valeur dans .env

### 5. Lancer l'app
```bash
streamlit run app.py
```

---

## ☁️ Déploiement Streamlit Cloud

### 1. Pousser sur GitLab
```bash
git add .
git commit -m "feat: initial comores analyst"
git push origin main
```

### 2. Sur Streamlit Cloud
1. Aller sur [share.streamlit.io](https://share.streamlit.io)
2. **New app** → connecter votre repo GitLab
3. **Main file** : `app.py`
4. **Python version** : `3.12`

### 3. Ajouter le secret
Dans **Settings > Secrets** de votre app :
```toml
GROQ_API_KEY = "gsk_xxxxxxxxxxxxxxxxxxxxxxxx"
```

---

## 📁 Structure du projet

```
comores-analyst/
├── app.py              # Interface Streamlit
├── agent.py            # Logique de l'agent (Groq API)
├── prompts.py          # System prompt + builder de prompts
├── requirements.txt    # Dépendances Python
├── .env.example        # Template de configuration
├── .env                # Clés API (NON commité)
├── .gitignore
└── README.md
```

---

## 🔑 Obtenir une clé API Groq (gratuite)

1. Aller sur [console.groq.com](https://console.groq.com)
2. Créer un compte
3. **API Keys** → **Create API Key**
4. Copier la clé dans votre `.env`

---

## 💡 Fonctionnalités

| Feature | Description |
|---------|-------------|
| 🎯 Angles multiples | Politique, économique, humain, opportunités |
| 🌐 Influences extérieures | France, Golfe, BRICS, voisins |
| ⏱️ Horizons temporels | Court / Moyen / Long terme |
| 🏭 Secteurs ciblés | Tourisme, ENR, agro, fintech... |
| ⚡ Analyses rapides | 4 boutons de lancement rapide |
| 📥 Export JSON | Téléchargement de chaque analyse |
| 📋 Historique | 5 dernières analyses en sidebar |

---

## 🔧 Workflow GitLab recommandé

```bash
# Travailler sur une feature
git checkout -b feature/nouvelle-fonctionnalite

# Commiter
git add .
git commit -m "feat: description"

# Pousser
git push origin feature/nouvelle-fonctionnalite

# Merge request sur GitLab, puis merge sur main
# Streamlit Cloud redéploie automatiquement
```
