class TelegramView:
    @staticmethod
    def notify_processing(chat_id, telegram_model):
        telegram_model.send_message(chat_id, "Processing your request...")

    @staticmethod
    def notify_error(chat_id, telegram_model):
        telegram_model.send_message(chat_id, "An error occurred. Please try again.")

    @staticmethod
    def notify_no_video(chat_id, telegram_model):
        telegram_model.send_message(chat_id, "No TikTok video found at the provided URL.")
