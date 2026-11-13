"""Open each Streamlit app and wake it if Streamlit Community Cloud put it to sleep."""
import os
import sys

from playwright.sync_api import sync_playwright

APPS = [
    "https://partycohesion.streamlit.app/",
    "https://campaign-money.streamlit.app/",
    "https://grant-matcher.streamlit.app/",
]
WAKE_BUTTON = "button:has-text('get this app back up')"


def visit(page, url):
    page.goto(url, wait_until="domcontentloaded", timeout=90_000)
    page.wait_for_timeout(8_000)
    button = page.locator(WAKE_BUTTON)
    if button.count() > 0:
        button.first.click()
        print(f"{url}: was asleep, wake requested")
        page.wait_for_timeout(60_000)
        if page.locator(WAKE_BUTTON).count() > 0:
            return False
        print(f"{url}: awake")
    else:
        # Stay long enough for the app session to register as a visit.
        page.wait_for_timeout(20_000)
        print(f"{url}: already awake")
    return True


def main():
    failed = []
    launch = {"args": ["--no-sandbox"]}
    if os.environ.get("CHROME_PATH"):
        launch["executable_path"] = os.environ["CHROME_PATH"]
    if os.environ.get("HTTPS_PROXY"):
        launch["proxy"] = {"server": os.environ["HTTPS_PROXY"]}
    with sync_playwright() as p:
        browser = p.chromium.launch(**launch)
        page = browser.new_page()
        for url in APPS:
            try:
                if not visit(page, url):
                    failed.append(url)
            except Exception as exc:  # keep going so one app does not block the other
                print(f"{url}: error {exc}")
                failed.append(url)
        browser.close()
    if failed:
        print("Could not confirm awake: " + ", ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    main()
