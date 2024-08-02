from django.core.management import BaseCommand

from integrations.relay import Relay


class Command(BaseCommand):
    help = 'Run the Chat Relay with local config'

    def handle(self, *args, **kwargs):
        print('Chat Relay is starting...')
        relay = Relay()
        relay.init()
