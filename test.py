from flask import Flask, render_template, request, redirect, url_for, flash
from playwright.sync_api import sync_playwright
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'

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
                page.click('button:has-text("closed_caption_off")')

                participant_count = int(page.locator('div.uGOf1d').inner_text())
                print(f"The initial participant count is: {participant_count}")

                transcript = []
                processed_captions = set()

                while participant_count > 1:
                    captions = page.locator('div.TBMuR.bj4p3b')
                    for i in range(captions.count()):
                        caption = captions.nth(i)
                        speaker = caption.locator('div.zs7s8d.jxFHg').inner_text()
                        text_spans = caption.locator('div.iTTPOb.VbkSUe span')
                        text = ' '.join([span.inner_text() for span in text_spans.all()])
                        caption_text = f"{speaker} : {text.strip()}"
                        if caption_text not in processed_captions and text.strip():
                            transcript.append(caption_text)
                            processed_captions.add(caption_text)
                    time.sleep(5)
                    participant_count = int(page.locator('div.uGOf1d').inner_text())
                    print(f"Participant count: {participant_count}")

                with open('transcript.txt', 'w') as f:
                    for line in transcript:
                        f.write(line + '\n')

                print('Transcript saved to transcript.txt')
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
