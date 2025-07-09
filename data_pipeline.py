import json
from datetime import datetime
from scrapers.rss_scraper import fetch_rss_headlines
from scrapers.html_scraper import fetch_html_headlines
import time

# Toggle scrape time logging here (True to enable, False to disable)
SHOW_SCRAPE_TIMES = False

def load_sources():
    with open("config.json") as f:
        return json.load(f)

def fetch_website_headlines():
    headlines = []
    sources = load_sources()

    for source in sources:
        start_time = time.perf_counter()
        try:
            if source["type"] == "rss":
                result = fetch_rss_headlines(source)
            elif source["type"] == "html":
                result = fetch_html_headlines(source)
            else:
                result = []
            if result is None:
                result = []

            # Add color and audio properties from config to each headline
            for h in result:
                h["color"] = source.get("color", "WHITE")
                h["audio"] = source.get("audio", None)

            headlines.extend(result)

            elapsed = time.perf_counter() - start_time
            if SHOW_SCRAPE_TIMES:
                print(f"[INFO] {source['name']} scrape time: {elapsed:.2f} seconds")
            if elapsed > 5.0:
                print(f"[WARNING] {source['name']} slow response!")

        except Exception as e:
            time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{time_str}] ERROR fetching headlines for {source['name']}: {type(e).__name__} - {e}")
            continue
    return headlines

def fetch_all_headlines():
    # Keeping for backward compatibility
    return fetch_website_headlines()

def group_headlines_by_type(headlines):
    grouped = {"RSS": [], "HTML": [], "SEC": []}
    for h in headlines:
        if h.get("source") == "SEC EDGAR (8-K)":
            grouped["SEC"].append(h)
        elif "(RSS)" in h.get("source", ""):
            grouped["RSS"].append(h)
        else:
            grouped["HTML"].append(h)
    return grouped
