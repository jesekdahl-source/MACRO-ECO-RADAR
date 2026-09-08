
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from urllib.parse import quote_plus
import html
import re

import feedparser
import pandas as pd

from news_config import NEWS_CONFIG

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

def _clean(text: str) -> str:
    text = html.unescape(text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def _published(entry):
    for key in ("published", "updated"):
        value = getattr(entry, key, None)
        if value:
            try:
                dt = parsedate_to_datetime(value)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc)
            except Exception:
                pass
    return None

def _source_name(entry):
    source = getattr(entry, "source", None)
    if source and isinstance(source, dict):
        return source.get("title") or "Unknown"
    title = getattr(entry, "title", "")
    # Google News often appends " - Publisher"
    if " - " in title:
        return title.rsplit(" - ", 1)[-1].strip()
    return "Unknown"

def _classify(category: str, title: str, summary: str):
    cfg = NEWS_CONFIG[category]
    text = f"{title} {summary}".lower()
    up_hits = [kw for kw in cfg["risk_up"] if kw in text]
    down_hits = [kw for kw in cfg["risk_down"] if kw in text]
    if len(up_hits) > len(down_hits):
        return "Risk Up", up_hits[:3]
    if len(down_hits) > len(up_hits):
        return "Risk Down", down_hits[:3]
    return "Neutral", []

def fetch_category_news(category: str, hours: int = 24, max_items: int = 20):
    cfg = NEWS_CONFIG[category]
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    seen = set()
    items = []

    for query in cfg["queries"]:
        url = GOOGLE_NEWS_RSS.format(query=quote_plus(query))
        feed = feedparser.parse(url)

        for entry in feed.entries:
            title = _clean(getattr(entry, "title", ""))
            link = getattr(entry, "link", "")
            published = _published(entry)
            summary = _clean(getattr(entry, "summary", ""))

            if not title or not link:
                continue
            dedupe = (title.lower(), link)
            if dedupe in seen:
                continue
            seen.add(dedupe)

            # Keep undated items, but they won't count as "fresh".
            is_fresh = bool(published and published >= cutoff)
            tone, hits = _classify(category, title, summary)

            items.append({
                "title": title,
                "link": link,
                "source": _source_name(entry),
                "published": published,
                "published_text": published.astimezone().strftime("%Y-%m-%d %H:%M") if published else "Unknown",
                "summary": summary,
                "tone": tone,
                "hits": hits,
                "fresh": is_fresh,
            })

    items.sort(key=lambda x: x["published"] or datetime(1970,1,1,tzinfo=timezone.utc), reverse=True)
    fresh_items = [x for x in items if x["fresh"]]
    return items[:max_items], len(fresh_items)

def fetch_all_news(hours: int = 24, max_items: int = 20):
    out = {}
    errors = []
    for category in NEWS_CONFIG:
        try:
            items, fresh_count = fetch_category_news(category, hours=hours, max_items=max_items)
            out[category] = {"items": items, "fresh_count": fresh_count}
        except Exception as e:
            out[category] = {"items": [], "fresh_count": 0}
            errors.append(f"{category}: {e}")
    return out, errors

def news_tone_summary(items):
    if not items:
        return {
            "risk_up": 0, "risk_down": 0, "neutral": 0,
            "label": "No recent news", "score": 0
        }
    risk_up = sum(1 for x in items if x["tone"] == "Risk Up")
    risk_down = sum(1 for x in items if x["tone"] == "Risk Down")
    neutral = sum(1 for x in items if x["tone"] == "Neutral")
    score = risk_up - risk_down
    if score >= 3:
        label = "Risk tone worsening"
    elif score <= -3:
        label = "Risk tone improving"
    else:
        label = "Mixed / neutral"
    return {
        "risk_up": risk_up, "risk_down": risk_down, "neutral": neutral,
        "label": label, "score": score
    }
