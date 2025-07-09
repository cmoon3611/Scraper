import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

def fetch_html_headlines(source):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
    }
    try:
        response = requests.get(source["url"], headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{time_str}] ERROR fetching {source['url']}: {type(e).__name__} - {e}")
        return []

    try:
        soup = BeautifulSoup(response.text, "html.parser")
        selector = source.get("selector")
        limit = source.get("limit", 5)

        elements = soup.select(selector)[:limit]
        if not elements:
            time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{time_str}] WARNING: No elements found for selector '{selector}' on {source['url']}")
    except Exception as e:
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{time_str}] ERROR parsing HTML from {source['url']}: {type(e).__name__} - {e}")
        return []

    headlines = []
    for el in elements:
        try:
            title = el.get_text(strip=True)

            # Handle Morpheus case where headline link is on the <a> inside <article> > a > header > h2 (no href on h2)
            # So get href from el.parent if needed, otherwise el.get("href")
            link = None
            if el.has_attr("href"):
                link = urljoin(source["url"], el.get("href"))
            else:
                # Try parent or grandparent for <a> href
                parent = el.parent
                while parent and parent.name != "a":
                    parent = parent.parent
                if parent and parent.name == "a" and parent.has_attr("href"):
                    link = urljoin(source["url"], parent.get("href"))
                else:
                    link = source["url"]

            time_str = datetime.now().strftime("%H:%M:%S")

            headlines.append({
                "title": title,
                "link": link,
                "source": source["name"],
                "time": time_str
            })
        except Exception as e:
            time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{time_str}] ERROR processing headline element from {source['url']}: {type(e).__name__} - {e}")
            continue

    return headlines
