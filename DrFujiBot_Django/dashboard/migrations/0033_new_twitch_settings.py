from django.db import migrations

default_settings = [('Twitch Bot Username', ''),
                    ('Twitch Channel', ''),
                   ]

def create_default_settings(apps, schema_editor):
    Setting = apps.get_model('dashboard', 'Setting')

    twitch_username = None
    existing_settings = Setting.objects.filter(key='Twitch Username')
    if len(existing_settings) > 0:
        twitch_username = existing_settings[0]

    setting_objects = []
    for setting in default_settings:
        value = setting[1]
        if setting[0] == 'Twitch Channel' and twitch_username is not None:
            value = twitch_username.value
        setting_object = Setting(key=setting[0], value=value)
        setting_objects.append(setting_object)

    Setting.objects.bulk_create(setting_objects)

    if twitch_username is not None:
        twitch_username.delete()

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0032_bannedphrase_timeout'),
    ]

    operations = [
        migrations.RunPython(create_default_settings),
    ]
