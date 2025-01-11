import re
import requests
import time
import os
from io import BytesIO
from playwright.sync_api import sync_playwright
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.fx.all import crop

TOKEN = 'TG_BOT_TOKEN'
BASE_URL = f'https://api.telegram.org/bot{TOKEN}/'

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
            for i, video_info in enumerate(video_urls, start=1):
                response = page.request.get(video_info['url'], headers=video_info['headers'])
                file_name = f'dowloaded_video_{i}.mp4'

                with open(file_name, 'wb') as video_file:
                    video_file.write(response.body())
                
                print(f"Video {i} downloaded successfully!")
                if start_time is not None and end_time is not None:
                    trimmed_file_name = f'trimmed_video_{i}.mp4'
                    trim_video(file_name, trimmed_file_name, start_time, end_time)
                    send_video_to_telegram(trimmed_file_name, chat_id)
                    os.remove(trimmed_file_name)
                else:
                    send_video_to_telegram(file_name, chat_id)
                    os.remove(file_name)
                print(f"Video {i} file deleted after sending.")
        else:
            print("No TikTok video URLs found.")

        browser.close()

def trim_video(input_file, output_file, start_time, end_time):
    try:
        start_seconds = convert_time_to_seconds(start_time)
        end_seconds = convert_time_to_seconds(end_time)

        with VideoFileClip(input_file) as clip:
            trimmed_clip = clip.subclip(start_seconds, end_seconds)
            trimmed_clip.write_videofile(output_file, codec='libx264', audio_codec='aac')
        print(f"Video trimmed successfully from {start_time} to {end_time}.")
    except Exception as e:
        print(f"Failed to trim video: {e}")

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

def send_video_to_telegram(file_path, chat_id):
    url = f"https://api.telegram.org/bot{TOKEN}/sendVideo"
    
    with open(file_path, 'rb') as video_file:
        files = {
            'video': (file_path, video_file, 'video/mp4')
        }
        data = {
            'chat_id': chat_id
        }

        telegram_response = requests.post(url, files=files, data=data)

        if telegram_response.status_code == 200:
            print("Video sent successfully to Telegram!")
        else:
            print(f"Failed to send video: {telegram_response.text}")

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
    while True:
        updates = get_updates(offset)
        if updates['result']:
            for update in updates['result']:
                chat_id = update['message']['chat']['id']
                message_text = update['message'].get('text')
    
                if message_text and "tiktok.com" in message_text:
                    parts = message_text.split()
                    url = parts[0]
                    start_time = None
                    end_time = None

                    if len(parts) > 1:
                        for part in parts[1:]:
                            if part.startswith('start='):
                                start_time = part.split('=')[1]
                            elif part.startswith('end='):
                                end_time = part.split('=')[1]

                    capture_video_requests_from_tiktok(url, chat_id, start_time, end_time)
                else:
                    send_message(chat_id, "No tiktok founded")
                offset = update['update_id'] + 1
        time.sleep(1)

if __name__ == '__main__':
    main()
