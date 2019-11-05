from .models import Setting, CoinEntry
from apscheduler.schedulers.background import BackgroundScheduler
from scheduled_tasks.uptime_check import get_uptime

import datetime
import random

def is_num(num):
    try:
        int(num)
    except:
        return False
    else:
        return True

def handle_open(username, args):
    output = ''
    return output

def handle_close(username, args):
    output = ''
    return output

def handle_resolve(username, args):
    output = ''
    return output

def handle_cancel(username, args):
    output = ''
    return output

def handle_daily(username, args):
    output = ''
    do_daily = False

    stream_uptime = get_uptime()
    if stream_uptime:
        now = datetime.datetime.now(datetime.timezone.utc)

        coin_entries = CoinEntry.objects.filter(username__iexact=username)
        if len(coin_entries) == 0:
            coin_entry = CoinEntry(username=username)
            do_daily = True
        else:
            coin_entry = coin_entries[0]
            if coin_entry.last_daily < (now - stream_uptime):
                do_daily = True
            else:
                output = '@' + username + ' You have already received a daily bonus this stream!'

        if do_daily:
            amount = random.randint(0, 100)

            crit = random.randint(1, 16)
            crit_string = ''
            if 16 == crit:
                amount *= 2
                crit_string = 'A critical hit! '

            coin_entry.coins += amount
            coin_entry.last_daily = now
            coin_entry.save()

            output = '@' + username + ' You received ' + str(amount) + ' coins! '
            output += crit_string
            output += 'Your balance is now ' + str(coin_entry.coins) + ' coins'
    else:
        output = 'Try !daily again next time the stream is live!'

    return output

def handle_credit(username, args):
    output = ''

    username = args[0]
    amount = args[1]

    if not is_num(amount):
        username = args[1]
        amount = args[0]

    if is_num(amount):
        amount = int(amount)
        coin_entries = CoinEntry.objects.filter(username__iexact=username)
        if len(coin_entries) == 0:
            coin_entry = CoinEntry(username=username)
        else:
            coin_entry = coin_entries[0]
        coin_entry.coins += amount
        coin_entry.save()
        output = f'Credited {amount} coins to {username}'
    else:
        output = 'Invalid number of coins'

    return output

def handle_balance(username, args):
    output = '@' + username + ' Your balance is '
    
    coin_entries = CoinEntry.objects.filter(username__iexact=username)
    if len(coin_entries) > 0:
        coin_entry = coin_entries[0]
        output += f'{coin_entry.coins} coins'
    else:
        output += '0 coins'

    return output

def handle_leaderboard(username, args):
    output = 'Leaderboard: '
    
    coin_entries = CoinEntry.objects.all().order_by('-coins')[:3]
    if len(coin_entries) > 0:
        for entry in coin_entries:
            output += f'{entry.username}({entry.coins}) '
    else:
        output += 'None'

    return output

def handle_resetcoins(username, args):
    output = ''
    return output

handlers = {'!open': handle_open,
            '!event': handle_open,
            '!close': handle_close,
            '!resolve': handle_resolve,
            '!cancel': handle_cancel,
            '!daily': handle_daily,
            '!credit': handle_credit,
            '!balance': handle_balance,
            '!coins': handle_balance,
            '!leaderboard': handle_leaderboard,
            '!resetcoins': handle_resetcoins,
           }

expected_args = {'!open': 1,
                 '!event': 1,
                 '!close': 1,
                 '!resolve': 1,
                 '!cancel': 1,
                 '!daily': 0,
                 '!credit': 2,
                 '!balance': 0,
                 '!coins': 0,
                 '!leaderboard': 0,
                 '!resetcoins': 0,
                }

usage = {'!open': 'Usage: !open <event name>',
         '!event': 'Usage: !event <event name>',
         '!close': 'Usage: !close <event name>',
         '!resolve': 'Usage: !resolve <event name>',
         '!cancel': 'Usage: !cancel <event name>',
         '!daily': 'Usage: !daily',
         '!credit': 'Usage: !credit <username> <number of coins>',
         '!balance': 'Usage: !balance',
         '!coins': 'Usage: !coins',
         '!leaderboard': 'Usage: !leaderboard',
         '!resetcoins': 'Usage: !resetcoins',
        }

def handle_coin_command(line, username):
    output = ''
    args = line.split(' ')
    command = args[0]
    handler = handlers.get(command)
    if handler:
        args = args[1:]
        if len(args) >= expected_args[command]:
            output = handler(username, args)
        else:
            output = usage[command]
    return output
