from flask import Flask, render_template_string, request, redirect, url_for
import asyncio
from playwright.async_api import async_playwright
import os
from urllib.parse import urljoin
from threading import Thread

app = Flask(__name__)

# Ensure the uploads folder exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <title>Test</title>
  </head>
  <body>
    <button id="start">Start</button>
    <button id="stop">Stop</button>
    <script>
let stream;
let mr;
let chunks = [];

document.getElementById("start").addEventListener("click", async () => {
  stream = await window.navigator.mediaDevices.getDisplayMedia({
    video: true,
    audio: true,
  });
  mr = new MediaRecorder(stream);

  mr.ondataavailable = (e) => {
    chunks.push(e.data);
  };
  mr.onstop = () => {
    const blob = new Blob(chunks, { type: chunks[0].type });
    stream.getTracks().forEach(track => track.stop());

    const el = document.createElement("a");
    el.id = "dl";
    el.href = URL.createObjectURL(blob);
    el.download = "test.webm";
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
      .catch(error => console.error(error));
  };

  mr.start();
});

document.getElementById("stop").addEventListener("click", () => {
  mr.stop();
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
        # Validate file type and secure filename
        if not file.filename.endswith('.webm'):
            return 'Invalid file type', 400
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        return 'File uploaded successfully', 200
    return 'File upload failed', 400


async def run_playwright():
    async with async_playwright() as p:
        browser = await p.firefox.launch(
            headless=False,
            # firefox_user_prefs={
            #         "media.navigator.permission.disabled": True,
            #         "media.navigator.streams.fake": True,
            #     },
            args=[
                "--allow-http-screen-capture",
                "--auto-select-tab-capture-source-by-title=Rick Astley - Never Gonna Give You Up (Official Music Video) - YouTube",
                "--autoplay-policy=no-user-gesture-required",
            ]
        )
        context = await browser.new_context()

        # Open the first page (Flask app)
        page1 = await context.new_page()
        await page1.goto("http://localhost:5000")

        # Open the second page (YouTube)
        page2 = await context.new_page()
        await page2.goto("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

        # Bring the first page to the front and start recording
        await page1.bring_to_front()
        await page1.click("#start")

        await asyncio.sleep(40)

        # Bring the first page to the front and stop recording
        await page1.bring_to_front()
        await page1.click("#stop")
        await asyncio.sleep(40)
        await browser.close()


def run_flask():
    app.run(port=5000)


if __name__ == "__main__":
    # Run Flask server in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Run Playwright in the main thread
    asyncio.run(run_playwright())
