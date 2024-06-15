import asyncio
from pyppeteer import launch

async def join_google_meet(meeting_url):
    browser = await launch(executablePath=r'C:\Users\monam\AppData\Local\pyppeteer\pyppeteer\local-chromium\1181205\chrome-win\chrome-win\chrome.exe', headless=False)
    page = await browser.newPage()

    try:
        await page.goto(meeting_url)
        print('Joining Google Meet...')
        
        # Handling initial prompt, if any
        await page.waitForSelector('button[data-testid="ucwsnc"]')
        await page.click('button[data-testid="ucwsnc"]')

        await page.waitForTimeout(5000)
        await page.click('div.DPvwYc')
        await page.click('div.CwaK9')
        await page.waitForTimeout(5000)
        
        # Typing the name and joining
        await page.type('input[placeholder="Enter your name"]', "Bala Bot")
        await page.click('button[jsname="NPE9H"]')
        await page.waitForSelector('div.uGOf1d', visible=True)
        
        # Mute and turn off captions
        await page.click('div.qs41qe')
        await page.click('div.vgJExf')
        
        # Wait for participant count to become stable
        await page.waitForSelector('div.uGOf1d', visible=True)
        participant_count = await page.evaluate('parseInt(document.querySelector("div.uGOf1d").innerText)')
        print(f"The initial participant count is: {participant_count}")

        transcript = []
        processed_captions = set()

        while participant_count > 1:
            captions = await page.querySelectorAll('div.H7du2')
            for caption in captions:
                speaker = await caption.querySelectorEval('div.IYwVEf', 'el => el.innerText')
                text_spans = await caption.querySelectorAll('div.SLDxxb span')
                text = await page.evaluate('(elements) => elements.map(span => span.innerText).join(" ")', text_spans)
                caption_text = f"{speaker} : {text.strip()}"
                if caption_text not in processed_captions and text.strip():
                    transcript.append(caption_text)
                    processed_captions.add(caption_text)
            await asyncio.sleep(5)
            participant_count = await page.evaluate('parseInt(document.querySelector("div.uGOf1d").innerText)')
            print(f"Participant count: {participant_count}")

        with open('transcript.txt', 'w') as f:
            for line in transcript:
                f.write(line + '\n')

        print('Transcript saved to transcript.txt')
        print('No other participants left in the meeting. Leaving...')
        await page.click('button[aria-label="Leave call"]')
        await page.waitForTimeout(5000)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        await browser.close()

if __name__ == '__main__':
    meet_url = 'https://meet.google.com/pxj-xhhu-kyp'
    asyncio.get_event_loop().run_until_complete(join_google_meet(meet_url))
