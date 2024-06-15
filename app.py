import os
import asyncio
from flask import Flask, jsonify, render_template, render_template_string, request, redirect, url_for, flash, send_file
from playwright.async_api import async_playwright
from pydub import AudioSegment
from pydub.utils import make_chunks
from threading import Thread

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Ensure the uploads folder exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER'] = 'uploads/'
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
                "--disable-blink-features=AutomationControlled",
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
            # await page.wait_for_timeout(5000)
            await page.click('div.dP0OSd')
            await page.click('div.GOH7Zb')
            # await page.wait_for_timeout(5000)
            await page.fill('input[type="text"]', "Bala Bot")
            await page.click('button:has-text("Ask to join")')
            await page.wait_for_selector('div.uGOf1d', state='visible')
            await page.click('span.mUIrbf-RLmnJb')
            await page.click('button:has-text("closed_caption_off")')
            # Ensure the page is fully loaded
            await page.wait_for_load_state('networkidle')

            await page.wait_for_selector('button[aria-label="Chat with everyone"]')
            await page.click('button[aria-label="Chat with everyone"]')
            textarea_selector = 'textarea#bfTqV.qdOxv-fmcmS-wGMbrd.xYOaDe'
            await page.fill(textarea_selector, 'Hello i am Bala Bot i am here to take notes for Thabo Monamodi')
            await page.wait_for_load_state('networkidle')
            await page.wait_for_selector('button[aria-label="Send a message"]')
            await page.click('button[aria-label="Send a message"]')

            await page1.bring_to_front()
            await page1.click("#start")
            participant_count = int(await page.locator('div.uGOf1d').inner_text())
            print(f"The initial participant count is: {participant_count}")

            transcript = []
            processed_captions = set()

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
    return render_template('form.html')

@app.route("/ccc")
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Record Screen</title>
</head>
<body>
  <button id="start">Start</button>
  <button id="stop">Stop</button>
  <script>
    let stream;
    let mr;
    let chunks = [];

    document.getElementById("start").addEventListener("click", async () => {
      try {
        stream = await navigator.mediaDevices.getDisplayMedia({
          video: true,
          audio: true,
        });
        mr = new MediaRecorder(stream);

        mr.ondataavailable = (e) => {
          chunks.push(e.data);
        };

        mr.onstop = () => {
          const blob = new Blob(chunks, { type: chunks[0].type });
          chunks = []; // Clear chunks for next recording

          const el = document.createElement("a");
          el.href = URL.createObjectURL(blob);
          el.download = "test.webm";
          el.style.display = 'none';
          document.body.appendChild(el);
          el.click();
          document.body.removeChild(el);

          // Send the file to the server
          const formData = new FormData();
          formData.append('file', blob, 'test.webm');
          fetch('/upload', {
            method: 'POST',
            body: formData,
          }).then(response => response.text())
            .then(data => console.log(data))
            .catch(error => console.error('Upload error:', error));
        };

        mr.start();
      } catch (error) {
        console.error('Error accessing media devices:', error);
      }
    });

    document.getElementById("stop").addEventListener("click", () => {
      if (mr && mr.state !== 'inactive') {
        mr.stop();
      }
    });
  </script>
</body>
</html>
    """)

@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    
    if file:
        # Validate file type and secure filename (already done in your code)
        if not file.filename.endswith('.webm'):
            return 'Invalid file type', 400
        
        # Save the uploaded file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        # Convert webm to WAV using pydub and ffmpeg
        try:
            audio = AudioSegment.from_file(file_path, format='webm')
            wav_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.wav')
            audio.export(wav_path, format='wav')
            return send_file(wav_path, as_attachment=True)
        except Exception as e:
            return f'Conversion error: {str(e)}', 500
        
    return 'File upload failed', 400
    

from moviepy.editor import VideoFileClip
@app.route('/covert')
def covert():
    try:
        video_file = "test"
        audio_file = "out_audio.wav"

        clip = VideoFileClip(video_file)
        clip.audio.write_audiofile(audio_file)

        return jsonify({"message": "Audio conversion successful", "audio_file": audio_file})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
