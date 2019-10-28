import argparse
import json
from dashboard.models import SimpleOutput, TimedMessage, EVERYONE, Quote
from dashboard.models import Command as DashboardCommand
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Migrates JSON configuration from DrFujiBot 1.0 into the DrFujiBot 2.0 database'

    def migrate_legacy_config(self, legacy_json):
        self.stdout.write('Migrating legacy config...')

        extra_commands = legacy_json.get('extra_commands')
        if extra_commands:
            for extra_command in extra_commands.keys():
                output_text = extra_commands[extra_command]
                simple_output_object = SimpleOutput(output_text=output_text)
                simple_output_object.save()
                command_object = DashboardCommand(command=extra_command, permissions=EVERYONE, output=simple_output_object)
                command_object.save()

        timed_messages = legacy_json.get('timed_messages')
        if timed_messages:
            for timed_message in timed_messages:
                for message in timed_message.keys():
                    minutes = timed_message[message] / 60
                    simple_output_object = SimpleOutput(output_text=message)
                    simple_output_object.save()
                    timed_message_object = TimedMessage(minutes_interval=minutes, message=simple_output_object)
                    timed_message_object.save()
        
        streamer = legacy_json.get('streamer')
        quotes = legacy_json.get('quotes')
        if quotes:
            for quote_num in quotes.keys():
                quote_text = quotes[quote_num]
                quote_object = Quote(id=int(quote_num), quote_text=quote_text, quotee=streamer)
                quote_object.save()

        self.stdout.write('Done!')

    def add_arguments(self, parser):
        parser.add_argument('--file', nargs='?', type=argparse.FileType('r'))

    def handle(self, *args, **options):
        json_file = options['file']
        with json_file as f:
            config = json.loads(f.read())
            self.migrate_legacy_config(config)
