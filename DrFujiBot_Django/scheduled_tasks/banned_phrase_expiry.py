import datetime
from apscheduler.schedulers.background import BackgroundScheduler

def expire_banned_phrases():
    from dashboard.models import BannedPhrase
    utc_tz = datetime.timezone.utc
    now = datetime.datetime.now(utc_tz)
    expired_phrases = BannedPhrase.objects.filter(expiry__lte=now)
    for phrase in expired_phrases:
        phrase.delete()

def start_expiry_task():
    scheduler = BackgroundScheduler()
    scheduler.add_job(expire_banned_phrases, 'interval', minutes=1)
    scheduler.start()
