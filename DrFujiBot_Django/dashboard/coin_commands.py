from .models import CoinEntry, ChatLog, BettingEvent, Bet, OPEN, CLOSED, RESOLVED, CANCELLED
from apscheduler.schedulers.background import BackgroundScheduler
from django.db.models import Q
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
    event_name = args[0]
    prize_coins = args[1]
    if is_num(prize_coins):
        existing_events = BettingEvent.objects.filter(name__iexact=event_name, status=OPEN)
        if len(existing_events) == 0:
            betting_event = BettingEvent(name=event_name, prize_coins=prize_coins)
            betting_event.save()
            output = 'Betting has opened! Use !bet <guess> to play!'
        else:
            output = 'An open event named "' + event_name + '" already exists!'
    else:
        output = 'Please enter a valid number of prize coins'
    return output

def handle_close(username, args):
    output = ''
    event_name = args[0]
    existing_events = BettingEvent.objects.filter(name__iexact=event_name, status=OPEN)
    if len(existing_events) > 0:
        betting_event = existing_events[0]
        betting_event.status = CLOSED
        betting_event.closed_timestamp = datetime.datetime.now(datetime.timezone.utc)
        betting_event.save()
        output = 'Betting for the "' + event_name + '" event has now closed!'
    else:
        output = 'Open event "' + event_name + '" not found!'
    return output

def handle_resolve(username, args):
    output = ''
    event_name = args[0]
    result = args[1]

    # For now, the result can only be 0-6 (number of deaths in the party)
    if is_num(result) and int(result) >= 0 and int(result) <= 6:
        existing_events = BettingEvent.objects.filter(name__iexact=event_name).filter(Q(status=OPEN) | Q(status=CLOSED))
        if len(existing_events) > 0:
            betting_event = existing_events[0]
            betting_event.status = RESOLVED
            betting_event.resolved_timestamp = datetime.datetime.now(datetime.timezone.utc)

            winners = Bet.objects.filter(value__iexact=result, event=betting_event)

            betting_event.result = result
            betting_event.num_winners = len(winners)
            betting_event.save()

            if len(winners) > 0:
                prize = int(betting_event.prize_coins / len(winners))
                winner_usernames = []
                first_time_winners = []
                for winner in winners:
                    coin_entries = CoinEntry.objects.filter(username=winner.username)
                    if len(coin_entries) == 0:
                        last_daily = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
                        coin_entry = CoinEntry(username=winner.username, last_daily=last_daily)
                    else:
                        coin_entry = coin_entries[0]

                    bonus_amount = 0
                    if not coin_entry.has_won:
                        first_time_winners.append(winner.username)
                        bonus_amount = 1000

                    coin_entry.coins += prize + bonus_amount
                    coin_entry.has_won = True
                    coin_entry.save()

                    winner_usernames.append(winner.username)
                output = []
                output.append('"' + event_name + '" event had ' + str(len(winners)) + ' winners that got a payout of ' + str(prize) + ' coins each!')
                output.append('Winners: ' + ', '.join(winner_usernames))
                output.append('First-time winners receiving a 1000 coin bonus: ' + ', '.join(first_time_winners))
            else:
                output = 'Unfortuantely, there were no winners for the "' + event_name + '" event'
        else:
            output = 'Event "' + event_name + '" not found!'
    else:
        output = 'Please specify a valid result'
    return output

def handle_unresolve(username, args):
    output = ''
    event_name = args[0]

    existing_events = BettingEvent.objects.filter(name__iexact=event_name, status=RESOLVED).order_by('-resolved_timestamp')
    if len(existing_events) > 0:
        betting_event = existing_events[0]
        betting_event.status = CLOSED
        betting_event.save()

        if betting_event.num_winners > 0:
            winners = Bet.objects.filter(value__iexact=betting_event.result, event=betting_event)

            prize = int(betting_event.prize_coins / betting_event.num_winners)
            for winner in winners:
                coin_entry = CoinEntry.objects.get(username=winner.username)
                if coin_entry:
                    coin_entry.coins -= prize
                    coin_entry.save()

        output = 'Event "' + event_name + '" has been un-resolved. You may now resolve the event again.'
    else:
        output = 'Resolved event "' + event_name + '" not found!'
    return output

def handle_cancel(username, args):
    output = ''
    event_name = args[0]
    existing_events = BettingEvent.objects.filter(name__iexact=event_name, status=OPEN)
    if len(existing_events) > 0:
        betting_event = existing_events[0]
        betting_event.status = CANCELLED
        betting_event.cancelled_timestamp = datetime.datetime.now(datetime.timezone.utc)
        betting_event.save()
        output = 'The "' + event_name + '" event has been cancelled!'
    else:
        output = 'Open event "' + event_name + '" not found!'
    return output

def handle_bet(username, args):
    output = ''
    guess = args[0]

    existing_events = BettingEvent.objects.filter(status=OPEN)
    if len(existing_events) > 0:
        # For now, the result can only be 0-6 (number of deaths in the party)
        if is_num(guess) and int(guess) >= 0 and int(guess) <= 6:
            existing_bets = Bet.objects.filter(username__iexact=username, event_id=existing_events[0])
            if len(existing_bets) > 0:
                bet = existing_bets[0]
                bet.value = guess
                bet.save()
            else:
                bet = Bet(username=username, value=guess, event=existing_events[0])
                bet.save()
        else:
            output = 'Valid guesses are 0 to 6 (number of deaths)'
    else:
        output = 'There are no open events!'
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
            if now < coin_entry.last_daily:
                # The last daily time is in the future.
                # This can occur if system time was modified for Desmume/in-game clock purposes.
                # Allow the daily to proceed, and the last daily time will be set back to a normal value.
                do_daily = True
            elif coin_entry.last_daily < (now - stream_uptime):
                do_daily = True
            else:
                output = '@' + username + ' You have already received a daily bonus this stream!'

        if do_daily:
            crit_string = ''
            miss_string = ''

            amount = random.randint(0, 100)

            if amount >= 50:
                crit = random.randint(1, 16)
                if 16 == crit:
                    amount *= 2
                    crit_string = 'A critical hit! '
            elif amount == 0:
                miss_string = 'It missed! '

            coin_entry.coins += amount
            coin_entry.last_daily = now
            coin_entry.save()

            output = '@' + username + ' You received ' + str(amount) + ' coins! '
            output += crit_string
            output += miss_string
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
    
    coin_entries = CoinEntry.objects.all().order_by('-coins')[:10]
    if len(coin_entries) > 0:
        for entry in coin_entries:
            output += f'{entry.username}({entry.coins}) '
    else:
        output += 'None'

    return output

def handle_resetcoins(username, args):
    output = ''

    reset_matches = ChatLog.objects.filter(line__iexact='!resetcoins').filter(username__iexact=username)
    if len(reset_matches) > 1:
        # The same user has already done !resetcoins once and is now confirming the reset

        coin_entries = CoinEntry.objects.all()
        for entry in coin_entries:
            entry.delete()

        # Delete the !resetcoins chat logs in case a user wants to do it again immediately
        for reset in reset_matches:
            reset.delete()

        output = 'All coins have been reset!'
    else:
        # The same user has not yet done a second !resetcoins, so ask for confirmation
        output = '@' + username + ' Are you sure you want to reset coins? Do !resetcoins again to confirm.'

    return output

def handle_userbalance(username, args):
    output = ''
    
    coin_entry = CoinEntry.objects.filter(username__iexact=args[0])
    if len(coin_entry) > 0:
        coins = coin_entry[0].coins
        output = args[0] + ' has ' + str(coins) + ' coins.'
    else:
        output = 'User "' + args[0] + '" not found.'

    return output

handlers = {'!open': handle_open,
            '!event': handle_open,
            '!close': handle_close,
            '!resolve': handle_resolve,
            '!unresolve': handle_unresolve,
            '!cancel': handle_cancel,
            '!bet': handle_bet,
            '!daily': handle_daily,
            '!credit': handle_credit,
            '!balance': handle_balance,
            '!coins': handle_balance,
            '!leaderboard': handle_leaderboard,
            '!resetcoins': handle_resetcoins,
            '!userbalance': handle_userbalance,
           }

expected_args = {'!open': 2,
                 '!event': 2,
                 '!close': 1,
                 '!resolve': 2,
                 '!unresolve': 1,
                 '!cancel': 1,
                 '!bet': 1,
                 '!daily': 0,
                 '!credit': 2,
                 '!balance': 0,
                 '!coins': 0,
                 '!leaderboard': 0,
                 '!resetcoins': 0,
                 '!userbalance': 1,
                }

usage = {'!open': 'Usage: !open <event name> <prize coins>',
         '!event': 'Usage: !event <event name> <prize coins>',
         '!close': 'Usage: !close <event name>',
         '!resolve': 'Usage: !resolve <event name> <result>',
         '!unresolve': 'Usage: !unresolve <event name>',
         '!cancel': 'Usage: !cancel <event name>',
         '!bet': 'Usage: !bet <guess>',
         '!daily': 'Usage: !daily',
         '!credit': 'Usage: !credit <username> <number of coins>',
         '!balance': 'Usage: !balance',
         '!coins': 'Usage: !coins',
         '!leaderboard': 'Usage: !leaderboard',
         '!resetcoins': 'Usage: !resetcoins',
         '!userbalance': 'Usage: !userbalance <username>',
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
