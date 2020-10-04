from django.db import migrations
from dashboard.models import MODERATOR_ONLY

def create_egg_commands(apps, schema_editor):
    Command = apps.get_model('dashboard', 'Command')

    egg_commands = ['!pickegg', '!useegg', '!reseteggs']

    commands = []
    for egg_command in egg_commands:
        is_cooldown = (egg_command == '!pickegg')
        cmd = Command(command=egg_command, permissions=MODERATOR_ONLY, invocation_count=0, is_built_in=True, cooldown=is_cooldown, output=None)
        commands.append(cmd)

    Command.objects.bulk_create(commands)

    Setting = apps.get_model('dashboard', 'Setting')

    setting_object = Setting(key='Used Eggs', value='')
    setting_object.save()

    setting_object = Setting(key='Total Eggs', value='0')
    setting_object.save()

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0027_youtube_channel_id_setting'),
    ]

    operations = [
        migrations.RunPython(create_egg_commands),
    ]
