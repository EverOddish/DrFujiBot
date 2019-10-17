import datetime
from apscheduler.schedulers.background import BackgroundScheduler

def prune_chat_history():
    from dashboard.models import ChatLog
    utc_tz = datetime.timezone.utc
    five_minutes_ago = datetime.datetime.now(utc_tz) - datetime.timedelta(minutes=5)
    chat_logs = ChatLog.objects.filter(timestamp__lte=five_minutes_ago)
    for chat_log in chat_logs:
        chat_log.delete()

def start_prune_task():
    scheduler = BackgroundScheduler()
    scheduler.add_job(prune_chat_history, 'interval', minutes=5)
    scheduler.start()
