from models.telegram_model import TelegramModel
from views.telegram_view import TelegramView
from controllers.tiktok_controller import capture_video_requests
from models.video_model import trim_video


class BotController:
    def __init__(self, token):
        self.telegram_model = TelegramModel(token)
        self.view = TelegramView()

    def handle_updates(self, offset=None):
        updates = self.telegram_model.get_updates(offset)
        if updates['result']:
            for update in updates['result']:
                if 'message' in update:
                    chat_id = update['message']['chat']['id']
                    message_text = update['message'].get('text')
                    self.process_message(chat_id, message_text)
                offset = update['update_id'] + 1
        return offset

    def process_message(self, chat_id, message_text):
        if "tiktok.com" in message_text:
            # Send initial processing message
            init_message = self.telegram_model.send_message(chat_id, "Processing your TikTok video...")['result']['message_id']

            # Extract URL and optional start/end times
            parts = message_text.split()
            url = parts[0]
            start_time, end_time = None, None
            for part in parts[1:]:
                if part.startswith('s='):
                    start_time = part.split('=')[1]
                elif part.startswith('e='):
                    end_time = part.split('=')[1]

            # Try capturing video
            video_buffer = capture_video_requests(url, start_time, end_time, self.telegram_model, chat_id)
            self.telegram_model.delete_message(chat_id, init_message)
            if video_buffer:
                if start_time and end_time:
                    # Trim video if start and end times are provided
                    trimmed_video = trim_video(video_buffer, start_time, end_time)
                    if trimmed_video:
                        self.telegram_model.send_video(chat_id, trimmed_video)
                else:
                    # Send the full video if no trimming is needed
                    self.telegram_model.send_video(chat_id, video_buffer)
        else:
            self.view.notify_no_video(chat_id, self.telegram_model)

