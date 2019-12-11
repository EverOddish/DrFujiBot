from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from django.conf import settings
import os
import shutil

def backup_database():
    original_path = settings.DATABASES['default']['NAME']
    now = datetime.now()
    filename = 'db_2.0.7_' + now.strftime('%Y-%m-%d_%H-%M-%S') + '.sqlite3'
    backup_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'DrFujiBot_Backup', filename)
    print('Backing up database from ' + original_path + ' to ' + backup_path)
    shutil.copyfile(original_path, backup_path)

def start_backup_task():
    scheduler = BackgroundScheduler()
    scheduler.add_job(backup_database, 'interval', weeks=1)
    scheduler.start()
