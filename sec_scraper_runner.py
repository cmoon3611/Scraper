import time
import webbrowser
from datetime import datetime
from scrapers.sec_scraper import fetch_sec_8k_filings, fetch_sec_6k_filings
from utils import get_filing_html_url, get_ticker_from_title
from colorama import init, Fore, Back, Style
import pyglet
import os

init(autoreset=True)

SEC_AUDIO_PATH = "audio/SEC Scrape Audio.wav"
audio_players = {}

# Optional: Filter only for certain 8-K items. Leave empty set to disable filtering.
TARGET_8K_ITEMS = {"2.02", "7.01", "8.01", "4.01", "1.01"}

# Toggle scrape timer output on/off here:
SHOW_SCRAPE_TIMES = False

def play_audio(audio_path):
    audio_abs_path = os.path.abspath(audio_path)
    if audio_abs_path not in audio_players:
        try:
            source = pyglet.media.load(audio_abs_path, streaming=False)
            player = pyglet.media.Player()
            player.queue(source)
            audio_players[audio_abs_path] = player
        except Exception as e:
            print(f"[ERROR] Failed to load audio '{audio_abs_path}': {e}")
            return

    player = audio_players[audio_abs_path]
    player.pause()
    player.seek(0)
    player.play()

def has_target_item(items_str):
    if not TARGET_8K_ITEMS:
        return True
    if not items_str or items_str == "N/A":
        return False
    item_set = set(item.strip() for item in items_str.split(","))
    return bool(item_set & TARGET_8K_ITEMS)

def main():
    print("[INFO] Starting SEC 8-K and 6-K scraper...")
    last_seen = set()

    while True:
        try:
            start_time = time.time()
            filings_8k = fetch_sec_8k_filings()
            filings_6k = fetch_sec_6k_filings()
            elapsed = time.time() - start_time
            if SHOW_SCRAPE_TIMES:
                print(f"[INFO] SEC website scrape time: {elapsed:.2f} seconds")
        except Exception as e:
            print(f"[ERROR] Failed to fetch SEC filings: {type(e).__name__} - {e}")
            time.sleep(1)
            continue

        # Filter only those with tickers and valid item codes (for 8-Ks)
        filings_8k = [f for f in filings_8k if get_ticker_from_title(f["title"]) and has_target_item(f.get("items"))]
        filings_6k = [f for f in filings_6k if get_ticker_from_title(f["title"])]

        filings_8k = filings_8k[:5]
        filings_6k = filings_6k[:5]

        all_filings = []

        for f in filings_8k:
            ticker = get_ticker_from_title(f["title"])
            ticker_str = f"{Fore.RED}{ticker}{Style.RESET_ALL} | " if ticker else ""
            cleaned_title = f["title"].replace("8-K - ", "").replace("8-K ", "")
            all_filings.append({
                "key": (f["title"], f["link"]),
                "output": f"{ticker_str}{f['time']} | 8-K | {cleaned_title} | {f['items']} | {f['link']}",
                "link": f["link"]
            })

        for f in filings_6k:
            ticker = get_ticker_from_title(f["title"])
            ticker_str = f"{Fore.RED}{ticker}{Style.RESET_ALL} | " if ticker else ""
            cleaned_title = f["title"].replace("6-K - ", "").replace("6-K ", "")
            all_filings.append({
                "key": (f["title"], f["link"]),
                "output": f"{ticker_str}{f['time']} | 6-K | {cleaned_title} | {f['link']}",
                "link": f["link"]
            })

        current_set = set(f["key"] for f in all_filings)

        if current_set != last_seen:
            for f in all_filings:
                if f["key"] not in last_seen:
                    try:
                        print(f["output"])
                    except Exception as e:
                        print(f"[ERROR] Printing filing info: {type(e).__name__} - {e}")

                    try:
                        html_url = get_filing_html_url(f["link"])
                    except Exception:
                        html_url = f["link"]

                    try:
                        webbrowser.open(html_url)
                    except Exception:
                        pass

                    try:
                        play_audio(SEC_AUDIO_PATH)
                    except Exception as e:
                        print(f"[ERROR] Playing SEC audio: {e}")

            last_seen = current_set

        time.sleep(1)

if __name__ == "__main__":
    main()
