import time
import webbrowser
from data_pipeline import fetch_website_headlines, group_headlines_by_type
from colorama import init, Fore, Style
import pyglet
import os

init(autoreset=True)

COLOR_MAP = {
    "BLACK": Fore.BLACK,
    "RED": Fore.RED,
    "GREEN": Fore.GREEN,
    "YELLOW": Fore.YELLOW,
    "BLUE": Fore.BLUE,
    "MAGENTA": Fore.MAGENTA,
    "CYAN": Fore.CYAN,
    "WHITE": Fore.WHITE,
}

SHOW_SCRAPE_TIMES = False  # Toggle this to enable/disable scrape time output

audio_players = {}

def play_audio_for_source(audio_path):
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

def main():
    print("[INFO] Starting website headline scraper (RSS + HTML)...")
    last_seen_set = set()

    while True:
        try:
            start_time = time.perf_counter()
            headlines = fetch_website_headlines()
            elapsed = time.perf_counter() - start_time

            if SHOW_SCRAPE_TIMES:
                print(f"[INFO] Website scrape time: {elapsed:.2f} seconds")

        except Exception as e:
            print(f"[ERROR] Failed to fetch website headlines: {e}")
            time.sleep(1)
            continue

        current_set = set((h['source'], h['title']) for h in headlines)

        if current_set != last_seen_set:
            print("[INFO] Update detected!\n")

            # Process only new headlines (not seen before)
            new_items = current_set - last_seen_set
            new_headlines = [h for h in headlines if (h['source'], h['title']) in new_items]

            grouped = group_headlines_by_type(new_headlines)

            for group in ["RSS", "HTML"]:
                for h in grouped.get(group, []):
                    color_code = COLOR_MAP.get(h.get("color", "WHITE").upper(), Fore.WHITE)
                    output_line = f"{h['time']} | {h['source']} | {h['title']} | {h['link']}"
                    print(f"{color_code}{output_line}{Style.RESET_ALL}")
                    webbrowser.open(h["link"])

                    audio_path = h.get("audio")
                    if audio_path:
                        play_audio_for_source(audio_path)

            last_seen_set = current_set

        time.sleep(1)

if __name__ == "__main__":
    main()
