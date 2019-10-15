from backup_task import backup_task
from django.apps import AppConfig

class DashboardConfig(AppConfig):
    name = 'dashboard'

    def ready(self):
        backup_task.start()
