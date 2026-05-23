import os
import feedparser
import requests
from datetime import datetime, timedelta
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
from typing import List, Dict

# ─── SOURCES RSS COMORES ─────────────────────────────────────────────────────
RSS_FEEDS = {
    "Al-Watwan (Officiel)": "https://www.al-watwan.net/feed/",
    "HZK-Presse": "https://www.hzk-presse.com/feed/",
    "Masiwa": "https://www.masiwa.info/feed/",
    "Comores Infos": "https://www.comores-infos.com/feed/",
    "La Gazette des Comores": "https://www.lagazettedescomores.com/feed/",
}

# ─── MOTS-CLÉS DE RECHERCHE ───────────────────────────────────────────────────
SEARCH_QUERIES = [
    "Comores actualité",
    "Union des Comores politique économie",
    "Comoros news today",
    "Comores investissement",
    "Azali Assoumani",
    "Comores Mayotte",
]


def fetch_rss_news(max_per_feed: int = 3) -> List[Dict]:
    """Récupère les dernières news depuis les flux RSS comoriens."""
    articles = []
    cutoff = datetime.now() - timedelta(days=30)

    for source, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_per_feed]:
                # Date de publication
                pub_date = ""
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6]).strftime("%d/%m/%Y")

                # Résumé propre
                summary = ""
                if hasattr(entry, "summary"):
                    soup = BeautifulSoup(entry.summary, "html.parser")
                    summary = soup.get_text()[:300]

                articles.append({
                    "source": source,
                    "title": entry.get("title", "Sans titre"),
                    "summary": summary,
                    "url": entry.get("link", ""),
                    "date": pub_date,
                    "type": "rss"
                })
        except Exception as e:
            continue

    return articles


def search_web_news(query: str, max_results: int = 5) -> List[Dict]:
    """Recherche web via DuckDuckGo pour actualités récentes."""
    articles = []
    try:
        with DDGS() as ddgs:
            results = ddgs.news(
                keywords=query,
                region="fr-fr",
                safesearch="off",
                timelimit="m",  # dernier mois
                max_results=max_results
            )
            for r in results:
                articles.append({
                    "source": r.get("source", "Web"),
                    "title": r.get("title", ""),
                    "summary": r.get("body", "")[:300],
                    "url": r.get("url", ""),
                    "date": r.get("date", ""),
                    "type": "web"
                })
    except Exception as e:
        pass
    return articles


def search_social_signals(topic: str, max_results: int = 5) -> List[Dict]:
    """
    Scrape les signaux sociaux (Reddit, forums, blogs) via DuckDuckGo.
    Cherche dans Reddit, Twitter/X (via nitter), et forums francophones.
    """
    signals = []
    social_queries = [
        f"site:reddit.com Comoros {topic}",
        f"Comores {topic} 2025 OR 2026",
        f"\"Comores\" OR \"Comoros\" {topic} forum",
    ]

    try:
        with DDGS() as ddgs:
            for q in social_queries[:2]:
                results = ddgs.text(
                    keywords=q,
                    region="fr-fr",
                    safesearch="off",
                    timelimit="y",
                    max_results=3
                )
                for r in results:
                    signals.append({
                        "source": r.get("href", "").split("/")[2] if r.get("href") else "Social",
                        "title": r.get("title", ""),
                        "summary": r.get("body", "")[:250],
                        "url": r.get("href", ""),
                        "date": "",
                        "type": "social"
                    })
    except Exception as e:
        pass

    return signals[:max_results]


def gather_intelligence(query: str, max_articles: int = 10) -> Dict:
    """
    Collecte toutes les sources d'information pour enrichir une analyse.

    Returns:
        Dict avec articles RSS, news web, signaux sociaux et résumé formaté
    """
    # 1. RSS feeds locaux
    rss_articles = fetch_rss_news(max_per_feed=2)

    # 2. Recherche web ciblée sur le sujet
    web_articles = []
    search_term = f"Comores {query[:60]}"
    web_articles = search_web_news(search_term, max_results=5)

    # 3. Signaux sociaux
    social_signals = search_social_signals(query[:40], max_results=3)

    # 4. Recherche générale actualités Comores
    general_news = search_web_news("Comores actualité politique économie", max_results=3)

    # Fusion et déduplication par titre
    all_articles = rss_articles + web_articles + general_news + social_signals
    seen_titles = set()
    unique_articles = []
    for a in all_articles:
        title_key = a["title"][:50].lower()
        if title_key not in seen_titles and a["title"]:
            seen_titles.add(title_key)
            unique_articles.append(a)

    unique_articles = unique_articles[:max_articles]

    # Formatage pour injection dans le prompt
    formatted = format_intelligence_for_prompt(unique_articles)

    return {
        "articles": unique_articles,
        "count": len(unique_articles),
        "rss_count": len(rss_articles),
        "web_count": len(web_articles),
        "social_count": len(social_signals),
        "formatted_context": formatted,
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")
    }


def format_intelligence_for_prompt(articles: List[Dict]) -> str:
    """Formate les articles pour injection dans le prompt LLM."""
    if not articles:
        return "Aucune information récente disponible."

    sections = {
        "rss": "📰 ACTUALITÉS LOCALES (Sources comoriennes)",
        "web": "🌐 ACTUALITÉS WEB RÉCENTES",
        "social": "💬 SIGNAUX SOCIAUX & FORUMS"
    }

    formatted_parts = []

    for article_type, section_title in sections.items():
        type_articles = [a for a in articles if a["type"] == article_type]
        if not type_articles:
            continue

        formatted_parts.append(f"\n{section_title}")
        formatted_parts.append("─" * 40)

        for a in type_articles:
            date_str = f" [{a['date']}]" if a.get("date") else ""
            formatted_parts.append(f"• {a['source']}{date_str}")
            formatted_parts.append(f"  TITRE: {a['title']}")
            if a.get("summary"):
                formatted_parts.append(f"  RÉSUMÉ: {a['summary'][:200]}")
            formatted_parts.append("")

    return "\n".join(formatted_parts)


def format_for_display(intel: Dict) -> str:
    """Formate pour affichage dans la sidebar Streamlit."""
    if intel["count"] == 0:
        return "Aucune source récente trouvée"

    lines = [
        f"📊 **{intel['count']} sources collectées**",
        f"📰 RSS locaux: {intel['rss_count']}",
        f"🌐 Web: {intel['web_count']}",
        f"💬 Signaux sociaux: {intel['social_count']}",
        f"🕐 {intel['timestamp']}"
    ]
    return "\n".join(lines)
