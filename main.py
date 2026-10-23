import telebot
from parser.parser import (
    get_schedule,
    get_next_day_lessons,
    format_schedule,
)
from dotenv import load_dotenv
import os

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")

bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, """
Бот показывает актуальное расписание занятий для группы ТРИС-1-26
Создатель @phlorense
Команды:
/start — начал
/next — ближайшие занятия
""")

@bot.message_handler(commands=["next"])
def next_command(message):
    try:
        lessons = get_schedule()
        next_lessons = get_next_day_lessons(lessons)
        response = format_schedule(next_lessons)

        bot.reply_to(message, response)

    except Exception as e:
        print(f"Ошибка при получении расписания: {e}")
        bot.reply_to(
            message,
            "Не удалось получить расписание. Попробуй позже."
        )

bot.infinity_polling()