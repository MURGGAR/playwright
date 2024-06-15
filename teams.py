from playwright.sync_api import sync_playwright

def run(playwright):
    try:
        browser = playwright.chromium.launch(
            args=[
                    "--disable-blink-features=AutomationControlled",
                    "--use-fake-device-for-media-stream", 
                    "--use-fake-ui-for-media-stream",
                    "--disable-popup-blocking",
                    "--allow-http-screen-capture",
                    "--auto-select-tab-capture-source-by-title=Meet",
                    "--autoplay-policy=no-user-gesture-required",
                    "--disable-blink-features=AutomationControlled",

                ],
                headless=False)
        context = browser.new_context(viewport={"width": 800, "height": 600})
        page = context.new_page()

        # Define a more specific dialog handler
        def handle_dialog(dialog):
            if "Teams" in dialog.message and "open links" in dialog.message:
                dialog.dismiss()  # Dismiss the dialog if it mentions Teams and opening links

        # Add the dialog handler
        page.on("dialog", handle_dialog)

        meeting_url = "https://teams.live.com/meet/9433807611067?p=TYwXu4TLkPeZQtOBNi"
        page.goto(meeting_url)

        # Wait for the page to load completely
        page.wait_for_load_state("networkidle")

        # Use a more specific selector to locate the button
        page.wait_for_selector('button:has-text("Continue on this browser")')
        page.click('button:has-text("Continue on this browser")')

        # Give some time for any actions to complete
        page.wait_for_timeout(5000)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
