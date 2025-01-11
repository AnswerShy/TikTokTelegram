import re
import requests
import time
import os
import tempfile
from io import BytesIO
from playwright.sync_api import sync_playwright
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.fx.all import crop

TOKEN = 'TG_BOT_TOKEN'
BASE_URL = f'https://api.telegram.org/bot{TOKEN}/'

def send_video_to_telegram(video_buffer, chat_id):
    if not video_buffer:
        print("Video buffer is None. Cannot send to Telegram.")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendVideo"

    video_buffer.name = 'video.mp4' 
    files = {
        'video': ('video.mp4', video_buffer, 'video/mp4')
    }
    data = {
        'chat_id': chat_id
    }

    telegram_response = requests.post(url, files=files, data=data)

    if telegram_response.status_code == 200:
        print("Video sent successfully to Telegram!")
    else:
        print(f"Failed to send video: {telegram_response.text}")

def capture_video_requests_from_tiktok(url, chat_id, start_time, end_time):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36')
        page = browser.new_page()

        video_urls = [] 

        def handle_response(response):
            if response.url.startswith('https://v16-webapp-prime.tiktok.com'):
                video_info = {
                    'url': response.url,
                    'headers': response.request.headers,
                    'cookies': context.cookies()
                }
                video_urls.append(video_info)

        page.on('response', handle_response)

        page.goto(url)
        page.wait_for_load_state('networkidle')

        if video_urls:
            send_message(chat_id, "downloading video")
            for i, video_info in enumerate(video_urls, start=1):
                response = page.request.get(video_info['url'], headers=video_info['headers'])

                if response.status in [200, 206]:
                    video_buffer = BytesIO(response.body())
                    video_buffer.seek(0)
                    if start_time is not None and end_time is not None:
                        trimmed_video_buffer = trim_video(video_buffer, start_time, end_time)
                        if trimmed_video_buffer:
                            send_video_to_telegram(trimmed_video_buffer, chat_id)
                        else:
                            print(f"Failed to trim video {i}.")
                    else:
                        send_video_to_telegram(video_buffer, chat_id)
                else:
                    print("error on response status line 73")
                    break
        else:
            send_message(chat_id, "No tiktok founded")
            return

        browser.close()

def trim_video(input_buffer, start_time, end_time):
    try:
        start_seconds = convert_time_to_seconds(start_time)
        end_seconds = convert_time_to_seconds(end_time)

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_input:
            temp_input.write(input_buffer.getvalue())
            temp_input_path = temp_input.name

        with VideoFileClip(temp_input_path) as clip:
            trimmed_clip = clip.subclip(start_seconds, end_seconds)

            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_output:
                trimmed_clip.write_videofile(temp_output.name, codec='libx264', audio_codec='aac')
                temp_output_path = temp_output.name

        with open(temp_output_path, 'rb') as output_file:
            output_buffer = BytesIO(output_file.read())

        os.remove(temp_input_path)
        os.remove(temp_output_path)

        print(f"Video trimmed successfully from {start_time} to {end_time}.")
        return output_buffer

    except Exception as e:
        print(f"Failed to trim video: {e}")
        return None

def convert_time_to_seconds(time_str):
    match = re.match(r'(?:(\d+):)?(\d+):(\d+)(?:\.(\d+))?', time_str)
    if not match:
        raise ValueError("Invalid time format. Use HH:MM:SS.mmm or MM:SS.mmm or SS.mmm.")
    groups = match.groups()
    hours = int(groups[0]) if groups[0] else 0
    minutes = int(groups[1]) if groups[1] else 0
    seconds = int(groups[2]) if groups[2] else 0
    milliseconds = int(groups[3]) if groups[3] else 0
    total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
    print(total_seconds, hours * 3600, minutes * 60, seconds, milliseconds)
    return total_seconds

def get_updates(offset=None):
    url = BASE_URL + 'getUpdates'
    params = {'offset': offset, 'timeout': 100}
    response = requests.get(url, params=params)
    return response.json()

def send_message(chat_id, text):
    url = BASE_URL + 'sendMessage'
    params = {'chat_id': chat_id, 'text': text}
    response = requests.get(url, params=params)
    return response.json()

def main():
    offset = None
    last_url = None
    while True:
        updates = get_updates(offset)
        if updates['result']:
            for update in updates['result']:
                if 'edited_message' in update:
                    continue
                chat_id = update['message']['chat']['id']
                message_text = update['message'].get('text')
    
                if message_text and "tiktok.com" in message_text:
                    parts = message_text.split()
                    url = parts[0]
                    start_time = None
                    end_time = None
                    if url == last_url:
                        send_message(chat_id, "This URL has already been processed.")
                        continue
                    if len(parts) > 1:
                        for part in parts[1:]:
                            if part.startswith('s=') or part.startswith('start='):
                                start_time = part.split('=')[1]
                            elif part.startswith('e=') or part.startswith('end='):
                                end_time = part.split('=')[1]
                    capture_video_requests_from_tiktok(url, chat_id, start_time, end_time)
                    last_url = url
                else:
                    send_message(chat_id, "No tiktok founded")
                offset = update['update_id'] + 1
        time.sleep(1)

if __name__ == '__main__':
    main()
