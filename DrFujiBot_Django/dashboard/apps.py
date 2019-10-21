from scheduled_tasks import backup_task
from scheduled_tasks import chat_history
from scheduled_tasks import banned_phrase_expiry
from django.apps import AppConfig
from django.db.models.signals import post_save

class DashboardConfig(AppConfig):
    name = 'dashboard'

    def ready(self):
        backup_task.start_backup_task()
        chat_history.start_prune_task()
        banned_phrase_expiry.start_expiry_task()

        from .models import Setting
        from .signals import setting_changed
        post_save.connect(setting_changed, sender=Setting)
