import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from django.db.models import Q

def prune_chat_history():
    from dashboard.models import ChatLog
    utc_tz = datetime.timezone.utc
    now = datetime.datetime.now(utc_tz)
    five_minutes_ago = now - datetime.timedelta(minutes=5)
    future = now + datetime.timedelta(minutes=5)

    # Remove any chat logs that have a timestamp more than 5 minutes into the future,
    # in case the system time was changed for game cheating or something. Added the 5 minutes
    # so that we don't race with chat logs coming in at this moment.
    chat_logs = ChatLog.objects.filter(Q(timestamp__lte=five_minutes_ago) | Q(timestamp__gte=future))
    for chat_log in chat_logs:
        chat_log.delete()

def start_prune_task():
    scheduler = BackgroundScheduler()
    scheduler.add_job(prune_chat_history, 'interval', minutes=5)
    scheduler.start()
