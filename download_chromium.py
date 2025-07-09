import pyppeteer.chromium_downloader as chromium_downloader

chromium_downloader.download_chromium()
print("Chromium downloaded to:", chromium_downloader.chromium_executable())
