from django.core.management.base import BaseCommand
from bot.telegram.bot import run_bot
import logging

# Настройка логов
logging.basicConfig(filename='bot_runtime.log', level=logging.INFO)

class Command(BaseCommand):
    help = 'Start the Telegram bot'

    def handle(self, *args, **kwargs):
        try:
            self.stdout.write("Starting Telegram bot...")
            logging.info("Бот запущен")
            run_bot()
        except Exception as e:
            logging.error(f"Ошибка при запуске бота: {e}")
            self.stderr.write(f"Ошибка: {e}")
