import json
from playwright.sync_api import sync_playwright

def verify_bot_script_completeness():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Capture console logs
        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))
        page.on("pageerror", lambda exc: print(f"JS ERROR: {exc}"))

        page.goto("file:///app/dpe_app.html")

        # 1. Add Room (Room 2)
        page.click("text=+ Ajouter une Pièce")

        # 2. Add Elements to Pièce 1 (index 0)
        # Use simpler title-based locators
        print("Clicking Add Wall...")
        page.locator("button[title='Ajouter Mur']").first.click()

        print("Clicking Add Window...")
        page.locator("button[title='Ajouter Fenêtre']").first.click()

        # Wait a bit for render
        page.wait_for_timeout(500)

        # Debug: Print Room 1 HTML
        room1_html = page.locator(".room").first.inner_html()

        if "Vitrage" not in room1_html:
            print("ERROR: 'Vitrage' label not found in Room 1 HTML")

        # 3. Generate Script
        print("Generating Script...")
        page.click("text=Générer Script Bot")

        # 4. Get Output
        json_text = page.locator("#bot-output").input_value()
        data = json.loads(json_text)

        windows = [d for d in data if "Win" in d.get('selector', '')]
        print(f"Window instructions found: {len(windows)}")

        assert len(windows) > 0, "No Window instructions found"

        print("SUCCESS")
        browser.close()

if __name__ == "__main__":
    verify_bot_script_completeness()
