from playwright.sync_api import sync_playwright

URL = "https://asia.nikkei.com/Latestheadlines"
SELECTOR = ".__next article div > h4 > a"  # May still need refining

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=100)
    page = browser.new_page()
    print("[INFO] Navigating...")
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)

    try:
        page.wait_for_selector(SELECTOR, timeout=10000)
        elements = page.query_selector_all(SELECTOR)
        print(f"[INFO] Found {len(elements)} headline elements.")
        for el in elements:
            print(el.inner_text())
    except Exception as e:
        print(f"[ERROR] Could not find elements: {e}")
        html = page.content()
        with open("page_dump.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("[INFO] Dumped page HTML to 'page_dump.html'")

    browser.close()
