import multiprocessing
import telebot
from telebot.types import Message
from database.operation import insert_user
from project_types.types import User
from bot.tasks import status_handler, start_handler, stop_handler, reset_handler


def start_bot(token: str, queue: multiprocessing.Queue):
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=['start'])
    def start(message: Message):
        insert_user(User(user_type="telegram", user_id=message.from_user.id, username=message.from_user.username,
                         name=message.from_user.full_name))
        bot.send_message(message.chat.id, "Bot Started Successfully!")

    @bot.message_handler(func=lambda message: True)
    def message_handle(message: Message):
        message_lower = message.text.lower()
        parts: list[str] = message_lower.split()
        command = parts[0]
        arguments = parts[1:]
        if command == "status":
            result = status_handler(arguments, message.from_user.id)
            bot.reply_to(message, result)
        elif command == "reset":
            result = reset_handler(arguments, message.from_user.id, queue)
            bot.reply_to(message, result)
        elif command == "start":
            result = start_handler(arguments, message.from_user.id, queue)
            bot.reply_to(message, result)
        elif command == "stop":
            result = stop_handler(arguments, message.from_user.id, queue)
            bot.reply_to(message, result)
        else:
            bot.reply_to(message, "Invalid Command")

    bot.infinity_polling()
