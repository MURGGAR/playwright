from flask import Flask, render_template, request, redirect, url_for, flash
from playwright.sync_api import sync_playwright
import time

app = Flask(__name__)

def join_google_meet(meeting_url):
    with sync_playwright() as p:
        for browser_type in [p.firefox]:
            browser = browser_type.launch(
                headless=False,
                firefox_user_prefs={
                    "media.navigator.permission.disabled": True,
                    "media.navigator.streams.fake": True,
                }
            )
            context = browser.new_context(viewport={"width": 800, "height": 600})
            page = context.new_page()
            try:
                page.goto(meeting_url)
                print('Joining Google Meet...')
                page.wait_for_load_state('load')
                page.click('button:has-text("Got it")')
                page.wait_for_timeout(5000)
                page.click('div.dP0OSd')
                page.click('div.GOH7Zb')
                page.wait_for_timeout(5000)
                page.fill('input[type="text"]', "Bala Bot")
                page.click('button:has-text("Ask to join")')
                page.wait_for_selector('div.uGOf1d', state='visible')
                page.click('span.mUIrbf-RLmnJb')
                participant_count = int(page.locator('div.uGOf1d').inner_text())
                print(f"The initial participant count is: {participant_count}")
                
                
                while participant_count > 1:
                    time.sleep(30)
                    participant_count = int(page.locator('div.uGOf1d').inner_text())
                    print(f"Participant count: {participant_count}")

                print('No other participants left in the meeting. Leaving...')
                page.click('button[aria-label="Leave call"]')
                page.wait_for_timeout(5000)
            except Exception as e:
                print(f"Error in {browser_type.name}: {e}")
            finally:
                browser.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        meeting_url = request.form['meeting_url']
        if meeting_url:
            join_google_meet(meeting_url)
            flash('Joined the Google Meet successfully!', 'success')
        else:
            flash('Please enter a valid Google Meet URL.', 'error')
        return redirect(url_for('index'))
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
