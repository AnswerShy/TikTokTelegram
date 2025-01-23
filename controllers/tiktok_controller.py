from playwright.sync_api import sync_playwright
from io import BytesIO
from models.video_model import trim_video

def capture_video_requests(url, start_time, end_time, telegram_model, chat_id):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        video_urls = []

        # Event handler for responses
        def handle_response(response):
            if response.url.startswith('https://v16-webapp-prime.tiktok.com'):
                video_urls.append(response.url)

        page.on('response', handle_response)

        # Send "searching" message
        progress_message = telegram_model.send_message(chat_id, "Searching for video...")['result']['message_id']

        try:
            page.goto(url)
            page.wait_for_load_state('networkidle')

            if video_urls:
                telegram_model.delete_message(chat_id, progress_message)
                downloading_message = telegram_model.send_message(chat_id, "Downloading video...")['result']['message_id']


                for video_url in video_urls:
                    response = page.request.get(video_url)
                    if response.status == 200:
                        # Retrieve video data
                        video_data = response.body()
                        video_buffer = BytesIO(video_data)

                        # Trim and send the video
                        if start_time and end_time:
                            trimmed_video = trim_video(video_buffer, start_time, end_time)
                            if trimmed_video:
                                telegram_model.send_video(chat_id, trimmed_video)
                        else:
                            telegram_model.send_video(chat_id, video_buffer)

                        telegram_model.delete_message(chat_id, downloading_message)

                        break  # Stop after processing the first valid video
            else:
                telegram_model.edit_message(chat_id, progress_message, "No video found.")

        except Exception as e:
            telegram_model.edit_message(chat_id, progress_message, f"An error occurred: {str(e)}")
        
        finally:
            # Delete the progress message after completion
            telegram_model.delete_message(chat_id, progress_message)

        browser.close()

