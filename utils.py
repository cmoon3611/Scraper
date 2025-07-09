import json
import os
import re
import requests
from bs4 import BeautifulSoup

# Load CIK to Ticker map at startup
CIK_TO_TICKER = {}

try:
    with open("company_tickers_exchange.json", "r") as f:
        data = json.load(f)
        fields = data["fields"]
        cik_idx = fields.index("cik")
        ticker_idx = fields.index("ticker")
        for row in data["data"]:
            cik = str(row[cik_idx])
            ticker = row[ticker_idx]
            if ticker and not ticker.upper().endswith("W"):
                CIK_TO_TICKER[cik] = ticker
except Exception as e:
    print(f"[ERROR] Failed to load CIK-to-Ticker mapping: {type(e).__name__} - {e}")

def get_filing_html_url(index_url):
    try:
        if not index_url.endswith("-index.htm"):
            return index_url

        headers = {
            "User-Agent": "MyResearchBot/1.0 (your-email@example.com)"
        }

        response = requests.get(index_url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"[ERROR] SEC index page returned {response.status_code}")
            return index_url

        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")
        if not table:
            print("[ERROR] No table found on SEC index page")
            return index_url

        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 3:
                continue

            doc_type = cells[0].get_text(strip=True).lower()
            link_tag = cells[2].find("a")
            if link_tag and (link_tag["href"].endswith(".htm") or link_tag["href"].endswith(".html")):
                href = link_tag["href"]
                if "8-k" in doc_type or "form8-k" in href.lower():
                    return f"https://www.sec.gov{href}"

        first_link = soup.select_one("table a[href$='.htm'], table a[href$='.html']")
        if first_link:
            return f"https://www.sec.gov{first_link['href']}"

    except Exception as e:
        print(f"[ERROR] Failed to extract SEC .htm link: {e}")

    return index_url

def get_ticker_from_title(title):
    try:
        match = re.search(r"\((000\d+|\d{6,})\)", title)
        if not match:
            return None

        cik = match.group(1).lstrip("0")
        ticker = CIK_TO_TICKER.get(cik)
        if ticker:
            # Remove trailing W or WT from ticker (case insensitive)
            ticker = re.sub(r"[-]?W[T]?$", "", ticker, flags=re.IGNORECASE)
        return ticker
    except Exception as e:
        print(f"[ERROR] Extracting ticker from title: {type(e).__name__} - {e}")
        return None
