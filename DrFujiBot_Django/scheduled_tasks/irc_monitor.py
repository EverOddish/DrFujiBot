from apscheduler.schedulers.background import BackgroundScheduler

import subprocess

def check_irc_service():
    from dashboard.models import Setting
    irc_setting = Setting.objects.get(key='IRC Service')
    if 'Running' == irc_setting.value:
        try:
            args = ['net', 'start', 'DrFujiBot IRC']
            subprocess.run(args)
        except:
            pass

def start_irc_monitor_task():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_irc_service, 'interval', seconds=10)
    scheduler.start()
