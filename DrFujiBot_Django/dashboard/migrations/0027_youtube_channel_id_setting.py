from django.db import migrations

def create_youtube_setting(apps, schema_editor):
    Setting = apps.get_model('dashboard', 'Setting')

    setting_object = Setting(key='YouTube Channel ID', value='')
    setting_object.save()

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0026_tm_commands'),
    ]

    operations = [
        migrations.RunPython(create_youtube_setting),
    ]
