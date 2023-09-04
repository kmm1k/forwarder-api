import yaml
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run the Migration for old bot'
    config = None
    chat_pairs = {}

    def handle(self, *args, **kwargs):
        print('Migration script is starting...')
        with open('./telegram_bot/old_config.yml', 'rb') as f:
            self.config = yaml.safe_load(f)

        self.migrate_forwarding()

    def migrate_forwarding(self):
        # add bot pairs to dictionary so that we would have no repeating pairs
        for i in self.config['channel_pairs']:
            if i[0] not in self.chat_pairs:
                self.chat_pairs[i[0]] = []
                self.chat_pairs[i[0]].append(str(i[1]))
            else:
                if i[1] not in self.chat_pairs[i[0]]:
                    self.chat_pairs[i[0]].append(str(i[1]))
        # add bot data to database
        from bot.models import Forwarding
        for i in self.chat_pairs:
            print(f"migrating {i} to {self.chat_pairs[i]}")
            Forwarding.objects.create(from_chat=i, to_chats=self.chat_pairs[i])











