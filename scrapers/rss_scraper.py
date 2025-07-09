import feedparser
from datetime import datetime
import requests

def fetch_rss_headlines(source):
    try:
        # We do a requests.get first to check status, feedparser alone does not raise errors
        response = requests.get(source["url"], timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{time_str}] ERROR fetching RSS {source['url']}: {type(e).__name__} - {e}")
        return []

    try:
        feed = feedparser.parse(response.text)
        entries = feed.entries[:source.get("limit", 5)]
    except Exception as e:
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{time_str}] ERROR parsing RSS feed from {source['url']}: {type(e).__name__} - {e}")
        return []

    headlines = []
    for entry in entries:
        try:
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                time_str = datetime(*entry.published_parsed[:6]).strftime("%H:%M:%S")
            else:
                time_str = datetime.now().strftime("%H:%M:%S")

            headlines.append({
                "title": entry.title,
                "link": entry.link,
                "source": source["name"],
                "time": time_str
            })
        except Exception as e:
            time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{time_str}] ERROR processing RSS entry from {source['url']}: {type(e).__name__} - {e}")
            continue

    return headlines
