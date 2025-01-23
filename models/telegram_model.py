import requests
from datetime import datetime

class TelegramModel:
    def __init__(self, token):
        self.base_url = f"https://api.telegram.org/bot{token}/"

    def get_updates(self, offset=None):
        """
        Fetch updates from the Telegram bot API.
        """
        url = self.base_url + "getUpdates"
        params = {'offset': offset, 'timeout': 100}
        response = requests.get(url, params=params)
        return response.json()

    def send_message(self, chat_id, text):
        """
        Send a message to a specific chat.
        """
        url = self.base_url + "sendMessage"
        response = requests.post(url, data={'chat_id': chat_id, 'text': text})

        data = response.json()
        messageID = data['result']['message_id']

        current_time = datetime.now().strftime('%H:%M:%S')
        print(f"[{current_time}] Sending message {messageID} to {chat_id}: {text}")

        return data

    def delete_message(self, chat_id, message_id):
        url = self.base_url + "deleteMessage"
        response = requests.post(url, data={'chat_id': chat_id, 'message_id': message_id})
        current_time = datetime.now().strftime('%H:%M:%S')
        print(f"[{current_time}] Delete message {message_id} to {chat_id}")
        return response.json()

    def send_video(self, chat_id, video_buffer):
        """
        Send a video file to a specific chat.
        """
        url = self.base_url + "sendVideo"
        video_buffer.name = 'video.mp4'
        files = {'video': ('video.mp4', video_buffer, 'video/mp4')}
        data = {'chat_id': chat_id}
        response = requests.post(url, files=files, data=data)
        return response.json()
