# Generated by Django 2.2.5 on 2019-12-29 19:50

from django.db import migrations
from dashboard.models import MODERATOR_ONLY

stats_commands = ['!speed',
                  '!speedev',
                 ]

def create_stats_commands(apps, schema_editor):
    Command = apps.get_model('dashboard', 'Command')

    commands = []
    for stat_command in stats_commands:
        cmd = Command(command=stat_command, permissions=MODERATOR_ONLY, invocation_count=0, is_built_in=True, cooldown=False, output=None)
        commands.append(cmd)

    Command.objects.bulk_create(commands)

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0021_debug_command'),
    ]

    operations = [
        migrations.RunPython(create_stats_commands),
    ]
