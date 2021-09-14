import argparse
from dashboard.models import SimpleOutput
from dashboard.models import Command as DashboardCommand
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Resets SimpleOutput of built-in commands to empty in order to fix a specific bug that occurred'

    def handle(self, *args, **options):
        dashboard_commands = DashboardCommand.objects.filter(is_built_in=True)
        for cmd in dashboard_commands:
            cmd.output = None
            cmd.save()
