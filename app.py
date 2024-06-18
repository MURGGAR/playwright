import os
import asyncio
import time
from flask import Flask, jsonify, render_template, render_template_string, request, redirect, url_for, flash, send_file
from playwright.async_api import async_playwright
from pydub import AudioSegment
from threading import Thread
from moviepy.editor import VideoFileClip

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Ensure the uploads folder exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

async def join_google_meet(meeting_url):
    meeting_id = meeting_url.split("/")[-1]
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--allow-http-screen-capture",
                "--auto-select-tab-capture-source-by-title=Meet",
                "--autoplay-policy=no-user-gesture-required",
            ]
        )
        context = await browser.new_context()
        await context.grant_permissions(['microphone', 'camera'])
        page1 = await context.new_page()
        await page1.goto("http://localhost:5000/ccc")
        page = await context.new_page()

        try:
            await page.goto(meeting_url)
            print('Joining Google Meet...')
            await page.wait_for_load_state('load')
            await page.wait_for_load_state('networkidle')
            await page.click('button:has-text("Got it")')
            await page.click('div.dP0OSd')
            await page.click('div.GOH7Zb')
            await page.fill('input[type="text"]', "Bala Bot")
            await page.click('button:has-text("Ask to join")')
            await page.wait_for_selector('div.uGOf1d', state='visible')
            await page.click('span.mUIrbf-RLmnJb')
            await page.click('button:has-text("closed_caption_off")')

            await page.wait_for_selector('button[aria-label="Chat with everyone"]')
            await page.click('button[aria-label="Chat with everyone"]')
            textarea_selector = 'textarea#bfTqV.qdOxv-fmcmS-wGMbrd.xYOaDe'
            await page.fill(textarea_selector, 'Hello i am Bala Bot i am here to take notes for Thabo Monamodi')
            await page.wait_for_selector('button[aria-label="Send a message"]')
            await page.click('button[aria-label="Send a message"]')

            await page1.bring_to_front()
            await page1.click("#start")
            participant_count = int(await page.locator('div.uGOf1d').inner_text())
            print(f"The initial participant count is: {participant_count}")

            while participant_count > 1:
                await asyncio.sleep(5)
                participant_count = int(await page.locator('div.uGOf1d').inner_text())
                print(f"Participant count: {participant_count}")

            print('No other participants left in the meeting. Leaving...')
            await page.click('button[aria-label="Leave call"]')
            await page1.bring_to_front()
            await page1.click("#stop")
            await page.wait_for_timeout(5000)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

@app.route('/', methods=['GET', 'POST'])
async def form():
    if request.method == 'POST':
        meeting_url = request.form['meeting_url']
        if meeting_url:
            await join_google_meet(meeting_url)
            flash('Joined the Google Meet successfully!', 'success')
        else:
            flash('Please enter a valid Google Meet URL.', 'error')
        return redirect(url_for('form'))
    return render_template('online-ui.html')

@app.route("/ccc")
def index():
    # name the file of webm as recording + current timestamp
    filename = "recording_" + str(round(time.time() * 1000)) + ".webm"
    
    return render_template("onlineRec.html", filename=filename)

@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        print('No file part')
        return 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        print('No selected file')
        return 'No selected file', 400

    if file:
        # Validate file type
        if not file.filename.endswith('.webm'):
            print('Invalid file type')
            return 'Invalid file type', 400

        # Save the uploaded file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        print(f'Saving file to {file_path}')
        file.save(file_path)

        # Name the file of webm as recording + current timestamp
        filename = "monamodi68@mail.com_" + str(round(time.time() * 1000)) + ".wav"
        

        # Convert webm to WAV using pydub
        try:
            print(f'Converting {file_path} to WAV')
            audio = AudioSegment.from_file(file_path, format='webm')
            wav_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            audio.export(wav_path, format='wav')
            print(f'Conversion successful, saved to {wav_path}')
            
            # Send the WAV file to the client
            response = send_file(wav_path, as_attachment=True)
            
            # Delete the original .webm file after sending the WAV file
            print(f'Deleting original file {file_path}')
            os.remove(file_path)
            
            return response
        except Exception as e:
            print(f'Conversion error: {str(e)}')
            return f'Conversion error: {str(e)}', 500

    print('File upload failed')
    return 'File upload failed', 400


if __name__ == '__main__':
    app.run(debug=True)
