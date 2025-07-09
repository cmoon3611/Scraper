import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

def fetch_html_headlines(source):
    response = requests.get(source["url"], timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    selector = source.get("selector")
    limit = source.get("limit", 5)

    headlines = []
    elements = soup.select(selector)[:limit]
    for el in elements:
        title = el.get_text(strip=True)
        link = urljoin(source["url"], el.get("href"))
        time_str = datetime.now().strftime("%H:%M:%S")

        headlines.append({
            "title": title,
            "link": link,
            "source": source["name"],
            "time": time_str
        })

    return headlines
