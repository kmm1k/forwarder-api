from django.core.management.base import BaseCommand

from telegram_bot.message_forwarder import MessageForwarder


class Command(BaseCommand):
    help = 'Run the Telethon client'

    def handle(self, *args, **kwargs):
        print('Telegram bot is starting...')
        message_forwarder = MessageForwarder()
        message_forwarder.startDef()
