import sys

from scheduled_tasks import backup_task
from scheduled_tasks import chat_history
from scheduled_tasks import banned_phrase_expiry
from scheduled_tasks import uptime_check
from scheduled_tasks import coins
from scheduled_tasks import irc_monitor
from django.apps import AppConfig
from django.db.models.signals import post_save

class DashboardConfig(AppConfig):
    name = 'dashboard'

    def ready(self):
        # Don't run during manage commands
        is_manage = False
        for arg in sys.argv:
            if 'manage.py' in arg:
                is_manage = True
        if not is_manage or 'runserver' in sys.argv:
            #backup_task.start_backup_task()
            chat_history.start_prune_task()
            banned_phrase_expiry.start_expiry_task()
            # Disabled these due to get_stream_start_time() being broken due to Twitch token changes
            #uptime_check.start_uptime_check_task()
            #coins.start_coins_task()
            #irc_monitor.start_irc_monitor_task()

            from .models import Setting
            from .signals import setting_changed
            post_save.connect(setting_changed, sender=Setting)
