import requests
import feedparser
from datetime import datetime
import re

USER_AGENT = "Chris Moon cmoon@trlm.com - Python EDGAR Scraper v1.0"
SEC_EDGAR_ATOM_URL_8K = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&CIK=&type=8-K&company=&dateb=&owner=include&start=0&count=100&output=atom"
SEC_EDGAR_ATOM_URL_6K = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&CIK=&type=6-K&company=&dateb=&owner=include&start=0&count=100&output=atom"

def fetch_sec_8k_filings():
    headers = {
        "User-Agent": USER_AGENT,
        "Accept-Encoding": "gzip, deflate",
        "Host": "www.sec.gov",
        "Connection": "keep-alive"
    }
    try:
        response = requests.get(SEC_EDGAR_ATOM_URL_8K, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{time_str}] ERROR fetching SEC 8-K filings: {type(e).__name__} - {e}")
        return []

    try:
        feed = feedparser.parse(response.text)
    except Exception as e:
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{time_str}] ERROR parsing SEC 8-K feed: {type(e).__name__} - {e}")
        return []

    filings = []
    item_pattern = re.compile(r"Item (\d{1,2}\.\d{2})", re.IGNORECASE)

    for entry in feed.entries:
        if len(filings) >= 5:
            break
        try:
            title = entry.title
            if "8-K" not in title:
                continue

            link = None
            for l in entry.links:
                if l.rel == "alternate" and l.type == "text/html":
                    link = l.href
                    break

            summary_html = entry.get("summary", "")
            items_found = item_pattern.findall(summary_html)
            items_str = ", ".join(items_found) if items_found else "N/A"

            time_str = datetime.now().strftime("%H:%M:%S")
            if "updated" in entry:
                try:
                    dt = datetime.fromisoformat(entry.updated)
                    time_str = dt.strftime("%H:%M:%S")
                except Exception:
                    pass

            filings.append({
                "time": time_str,
                "title": title,
                "items": items_str,
                "link": link,
                "type": "8-K"
            })

        except Exception as e:
            time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{time_str}] ERROR processing SEC 8-K entry: {type(e).__name__} - {e}")
            continue

    return filings

def fetch_sec_6k_filings():
    headers = {
        "User-Agent": USER_AGENT,
        "Accept-Encoding": "gzip, deflate",
        "Host": "www.sec.gov",
        "Connection": "keep-alive"
    }
    try:
        response = requests.get(SEC_EDGAR_ATOM_URL_6K, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{time_str}] ERROR fetching SEC 6-K filings: {type(e).__name__} - {e}")
        return []

    try:
        feed = feedparser.parse(response.text)
    except Exception as e:
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{time_str}] ERROR parsing SEC 6-K feed: {type(e).__name__} - {e}")
        return []

    filings = []

    for entry in feed.entries:
        if len(filings) >= 5:
            break
        try:
            title = entry.title
            if "6-K" not in title:
                continue

            link = None
            for l in entry.links:
                if l.rel == "alternate" and l.type == "text/html":
                    link = l.href
                    break

            time_str = datetime.now().strftime("%H:%M:%S")
            if "updated" in entry:
                try:
                    dt = datetime.fromisoformat(entry.updated)
                    time_str = dt.strftime("%H:%M:%S")
                except Exception:
                    pass

            filings.append({
                "time": time_str,
                "title": title,
                "link": link,
                "type": "6-K"
            })

        except Exception as e:
            time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{time_str}] ERROR processing SEC 6-K entry: {type(e).__name__} - {e}")
            continue

    return filings
