import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from dashboard.utility import get_stream_start_time, get_viewer_list

def award_coins():
    from dashboard.models import Setting, CoinEntry

    coins_per_minute = int(Setting.objects.get(key='Coins Per Minute').value)

    start_time = get_stream_start_time()
    if start_time:
        # Stream is live, award coins
        viewer_list = get_viewer_list()
        for viewer in viewer_list:
            coin_entries = CoinEntry.objects.filter(username__iexact=viewer)
            if len(coin_entries) == 0:
                coin_entry = CoinEntry(username=viewer)
            else:
                coin_entry = coin_entries[0]
            coin_entry.coins += coins_per_minute
            coin_entry.save()

def start_coins_task():
    scheduler = BackgroundScheduler()
    scheduler.add_job(award_coins, 'interval', minutes=1)
    scheduler.start()
