from django.core.management.base import BaseCommand
from bot.telegram.bot import run_bot

class Command(BaseCommand):
    help = 'Start the Telegram bot'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting Telegram bot...")
        run_bot()
