from django.core.management import BaseCommand

from integrations.scraper import Scraper


class Command(BaseCommand):
    help = 'Run the Bet scraper'

    def handle(self, *args, **kwargs):
        print('Bet scraper is starting...')
        scraper = Scraper()
        scraper.start()

