import os
import requests


def send(chat, msg):
    requests.get(f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/sendMessage?chat_id={chat}&text={msg}")
