from scheduled_tasks import backup_task
from scheduled_tasks import chat_history
from django.apps import AppConfig

class DashboardConfig(AppConfig):
    name = 'dashboard'

    def ready(self):
        backup_task.start_backup_task()
        chat_history.start_prune_task()
