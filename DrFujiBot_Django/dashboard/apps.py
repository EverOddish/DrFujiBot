import sys

from scheduled_tasks import backup_task
from scheduled_tasks import chat_history
from scheduled_tasks import banned_phrase_expiry
from scheduled_tasks import uptime_check
from django.apps import AppConfig
from django.db.models.signals import post_save

class DashboardConfig(AppConfig):
    name = 'dashboard'

    def ready(self):
        # Don't run during manage commands
        if not 'manage.py' in sys.argv or 'runserver' in sys.argv:
            backup_task.start_backup_task()
            chat_history.start_prune_task()
            banned_phrase_expiry.start_expiry_task()
            uptime_check.start_uptime_check_task()

            from .models import Setting
            from .signals import setting_changed
            post_save.connect(setting_changed, sender=Setting)
