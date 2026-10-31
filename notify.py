import os                                    # built-in: read settings from the computer's environment
import requests                              # library: make web requests
from dotenv import load_dotenv               # reads the .env file

load_dotenv()                                # load secrets from .env into environment variables

TOKEN = os.environ["TELEGRAM_TOKEN"]         # bot token. CAPS = constant, a value that doesn't change while the program runs
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]     # your chat ID


def send_message(text):                      # reusable function: give it any text, it sends it to you on Telegram
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"  # Telegram's "send message" address, with the token filled in
    response = requests.post(                # POST = send data to the server
        url,
        json={"chat_id": CHAT_ID, "text": text},  # who gets the message, and what it says
        timeout=10,                          # give up after 10 seconds so a dead connection can't hang the bot forever
    )
    response.raise_for_status()              # if Telegram replies with an error, crash loudly instead of failing silently


if __name__ == "__main__":                   # runs only when you run THIS file directly, not when another file imports it
    send_message("Test message from notify.py ✅")  # quick self-test