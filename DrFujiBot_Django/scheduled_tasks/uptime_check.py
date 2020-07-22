import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from dashboard.utility import get_stream_start_time

real_start_time = None
last_start_time = None

def get_uptime():
    uptime = None
    global real_start_time

    if real_start_time:
        utc_tz = datetime.timezone.utc
        now = datetime.datetime.now(utc_tz)
        uptime = now - real_start_time

    return uptime

def check_uptime():
    global last_start_time
    global real_start_time

    start_time = get_stream_start_time()
    if start_time:
        # Stream is live 

        # If our current uptime has become stale ("live" longer than 16 hours), force an update.
        # This could happen if the computer has gone to sleep and has woken up later.
        force_update = False
        if None != real_start_time:
            current_uptime = now - real_start_time
            if current_uptime > datetime.timedelta(hours=16):
                force_update = True

        if last_start_time and False == force_update:
            # Stream is still live since last check (may have gone offline and come back in between checks)
            pass
        else:
            # Stream came back online in the last 5+ minutes so reset the real start time
            real_start_time = start_time
    else:
        # Stream is offline
        if last_start_time:
            # Stream went offline in the last 5 minutes
            pass
        else:
            # Stream has been offline longer than 5 minutes
            real_start_time = None

    last_start_time = start_time

def start_uptime_check_task():
    global last_start_time
    global real_start_time

    last_start_time = get_stream_start_time()
    real_start_time = last_start_time

    scheduler = BackgroundScheduler()
    scheduler.add_job(check_uptime, 'interval', minutes=5)
    scheduler.start()
