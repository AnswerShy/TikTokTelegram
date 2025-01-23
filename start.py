import os
import sys
from controllers.bot_controller import BotController
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    token = os.getenv("TELEGRAM_BOT_KEY")

    if len(sys.argv) > 1:
        token = sys.argv[1]
    
    if not token:
        raise ValueError("Telegram Bot token is not provided. Set TELEGRAM_BOT_KEY in the .env file or pass it as an argument.")

    bot = BotController(token)
    offset = None

    while True:
        offset = bot.handle_updates(offset)

if __name__ == "__main__":
    main()
