from .models import Setting, Command, SimpleOutput, Run, Death, Quote, ChatLog, BannedPhrase, TimedMessage
from apscheduler.schedulers.background import BackgroundScheduler
from westwood.models import Game

import datetime

def update_run(command_name, simple_output):
    if '!lastrun' == command_name or '!howfar' == command_name:
        current_run_setting = Setting.objects.filter(key='Current Run')[0]
        run_matches = Run.objects.filter(name__iexact=current_run_setting.value)
        if len(run_matches) > 0:
            run_object = run_matches[0]
            if '!lastrun' == command_name:
                run_object.last_run_output = simple_output
                run_object.save()
            elif '!howfar' == command_name:
                run_object.how_far_output = simple_output
                run_object.save()

def handle_setgame(args):
    game_name = ' '.join(args)
    output = 'Game "' + game_name + '" not found'
    game_objects = Game.objects.all()
    for game_object in game_objects:
        short_name = game_object.name.replace('Pokemon ', '').lower()
        if game_name.lower() == short_name or game_name.replace(' ', '').lower() == short_name:
            game_setting_matches = Setting.objects.filter(key__exact='Current Game')
            if len(game_setting_matches) > 0:
                game_setting_matches[0].value = game_object.name
                game_setting_matches[0].save()
                return 'Current game set to ' + game_object.name
    return output

def handle_addcom(args):
    output = ''
    command_name = args[0]
    simple_output_text = ' '.join(args[1:])

    if not command_name.startswith('!'):
        return 'Command must start with "!"'

    if len(simple_output_text) > 5000:
        return 'Command output too long (over 5000 characters)'

    command_matches = Command.objects.filter(command__iexact=command_name)
    if len(command_matches) == 0:
        simple_output = SimpleOutput(output_text=simple_output_text)
        simple_output.save()

        command = Command(command=command_name, output=simple_output)
        command.save()

        update_run(command_name, simple_output)

        output = 'Command "' + command_name + '" successfully created'
    else:
        output = 'Command "' + command_name + '" already exists'
    return output

def handle_delcom(args):
    output = ''
    command_name = args[0]

    if not command_name.startswith('!'):
        return 'Command must start with "!"'

    command_matches = Command.objects.filter(command__iexact=command_name)
    if len(command_matches) == 1:
        command_matches[0].delete()
        output = 'Command "' + command_name + '" successfully deleted'
    else:
        output = 'Command "' + command_name + '" not found'
    return output

def handle_editcom(args):
    output = ''
    command_name = args[0]
    simple_output_text = ' '.join(args[1:])

    if not command_name.startswith('!'):
        return 'Command must start with "!"'

    if len(simple_output_text) > 5000:
        return 'Command output too long (over 5000 characters)'

    command_matches = Command.objects.filter(command__iexact=command_name)
    if len(command_matches) == 1:
        command_object = command_matches[0]
        simple_output = command_object.output

        # We need to check if the current SimpleOutput is referenced by any Run that is not the current Run
        need_new_simple_output = False
        current_run_setting = Setting.objects.filter(key='Current Run')[0]
        run_matches = Run.objects.all()
        for run in run_matches:
            if run.name != current_run_setting.value:
                if simple_output == run.last_run_output or simple_output == run.how_far_output:
                    need_new_simple_output = True

        if need_new_simple_output:
            # Create a new SimpleOutput and point the Command to it, in order to preserve other Run references to the current SimpleOutput
            new_simple_output = SimpleOutput(prefix=simple_output.prefix, output_text=simple_output_text)
            new_simple_output.save()
            command_object.output = new_simple_output
            command_object.save()
            simple_output = new_simple_output
        else:
            # No other Run references the current SimpleOutput, so it's safe to just edit it
            simple_output.output_text = simple_output_text
            simple_output.save()

        update_run(command_name, simple_output)

        output = 'Command "' + command_name + '" successfully modified'
    else:
        output = 'Command "' + command_name + '" not found'
    return output

def handle_alias(args):
    output = ''
    existing_command_name = args[0]
    new_command_name = args[1]

    if not new_command_name.startswith('!'):
        return 'New command must start with "!"'

    existing_command_matches = Command.objects.filter(command__iexact=existing_command_name)
    found = (len(existing_command_matches) == 1)

    if not found:
        # Try reversing the order
        temp = existing_command_name
        existing_command_name = new_command_name
        new_command_name = temp

        existing_command_matches = Command.objects.filter(command__iexact=existing_command_name)
        found = (len(command_matches) == 1)

    if found:
        # Make sure the new command doesn't already exist
        new_command_matches = Command.objects.filter(command__iexact=new_command_name)
        if len(new_command_matches) == 0:
            existing_command = existing_command_matches[0]
            if not existing_command.is_built_in:
                new_command = Command(command=new_command_name, permissions=existing_command.permissions, output=existing_command.output)
                new_command.save()
                output = new_command_name + ' is now aliased to ' + existing_command_name
            else:
                output = 'Cannot create an alias for a built-in command'
        else:
            output = 'New command already exists'
    else:
        output = 'Existing command not found'
    return output

def handle_addrun(args):
    output = ''
    run_name = ' '.join(args)

    run_matches = Run.objects.filter(name__iexact=run_name)
    if len(run_matches) == 0:
        current_game_setting = Setting.objects.filter(key='Current Game')[0]
        run_object = Run(name=run_name, game_setting=current_game_setting.value)
        run_object.save()

        output = 'Added new run "' + run_object.name + '" playing ' + run_object.game_setting
    else:
        output = 'Run "' + run_name + '" already exists'
    return output

def handle_setrun(args):
    output = ''
    run_name = ' '.join(args)

    run_matches = Run.objects.filter(name__iexact=run_name)
    if len(run_matches) > 0:
        run_object = run_matches[0]
        current_game_setting = Setting.objects.filter(key='Current Game')[0]
        current_game_setting.value = run_object.game_setting
        current_game_setting.save()

        current_run_setting = Setting.objects.filter(key='Current Run')[0]
        current_run_setting.value = run_name
        current_run_setting.save()

        command_matches = Command.objects.filter(command__iexact='!lastrun')
        if len(command_matches) > 0:
            lastrun_command = command_matches[0]
            lastrun_command.output = run_object.last_run_output
            lastrun_command.save()

        command_matches = Command.objects.filter(command__iexact='!howfar')
        if len(command_matches) > 0:
            howfar_command = command_matches[0]
            howfar_command.output = run_object.how_far_output
            howfar_command.save()

        output = 'Current run set to "' + run_object.name + '" playing ' + run_object.game_setting
    else:
        output = 'Run "' + run_name + '" not found'
    return output

def handle_riprun(args):
    output = ''
    last_run_text = ' '.join(args)

    current_run_setting = Setting.objects.filter(key='Current Run')[0]

    run_matches = Run.objects.filter(name__iexact=current_run_setting.value)
    if len(run_matches) > 0:
        current_run_object = run_matches[0]
        current_run_object.attempt_number += 1

        last_run_simple_output = None
        command_matches = Command.objects.filter(command__iexact='!lastrun')
        if len(command_matches) > 0:
            lastrun_command = command_matches[0]

            prefix = ''
            if lastrun_command.output:
                prefix = lastrun_command.output.prefix
            last_run_simple_output = SimpleOutput(prefix=prefix, output_text=last_run_text)
            last_run_simple_output.save()

            lastrun_command.output = last_run_simple_output
            lastrun_command.save()
        else:
            last_run_simple_output = SimpleOutput(output_text=last_run_text)
            last_run_simple_output.save()

        current_run_object.last_run_output = last_run_simple_output
        current_run_object.save()

        output = 'Attempt number for "' + current_run_object.name + '" run is now ' + str(current_run_object.attempt_number) + ', and !lastrun was updated'
    else:
        output = 'Run "' + current_run_setting.value + '" not found'
    return output

def update_respects(death_object_id):
    death_matches = Death.objects.filter(id=death_object_id)
    if len(death_matches) > 0:
        death_object = death_matches[0]

        utc_tz = datetime.timezone.utc
        twenty_seconds_ago = datetime.datetime.now(utc_tz) - datetime.timedelta(seconds=20)

        f_matches = ChatLog.objects.filter(line__iexact='F').filter(timestamp__gte=twenty_seconds_ago)
        f_users = set()
        for match in f_matches:
            f_users.add(match.username)
            
        pokemof_matches = ChatLog.objects.filter(line__exact='pokemoF').filter(timestamp__gte=twenty_seconds_ago)
        pokemof_users = set()
        for match in pokemof_matches:
            pokemof_users.add(match.username)

        respect_count = len(f_users) + len(pokemof_users)

        death_object.respect_count = respect_count
        death_object.save()

        output = str(respect_count) + ' respects for ' + death_object.nickname
        respects_output = SimpleOutput(output_text=output)
        respects_output.save()
        two_minutes_ago = datetime.datetime.now(utc_tz) - datetime.timedelta(minutes=2)
        respects_message = TimedMessage(minutes_interval=1, last_output_time=two_minutes_ago, max_output_count=1, message=respects_output)
        respects_message.save()

def handle_rip(args):
    nickname = ' '.join(args)

    current_run_setting = Setting.objects.filter(key='Current Run')[0]
    run = Run.objects.filter(name=current_run_setting.value)[0]

    death_object = Death(nickname=nickname, run=run)
    death_object.save()

    death_count = Death.objects.filter(run=run).count()

    output = 'Death count: ' + str(death_count) + ' - Press F to pay respects to "' + nickname + '"'

    utc_tz = datetime.timezone.utc
    twenty_seconds_from_now = datetime.datetime.now(utc_tz) + datetime.timedelta(seconds=20)
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_respects, 'date', run_date=twenty_seconds_from_now, args=[death_object.id])
    scheduler.start()

    # TODO: Auto-marker

    return output

def handle_deaths(args):
    current_run_setting = Setting.objects.filter(key='Current Run')[0]
    run = Run.objects.filter(name=current_run_setting.value)[0]

    death_count = Death.objects.filter(run=run).count()
    death_objects = Death.objects.filter(run=run).order_by('-time_of_death')[:3]
    death_names = [death.nickname for death in death_objects]

    if death_count == 1:
        output = 'There has been ' + str(death_count) + ' death so far. Most recent deaths (latest first): '
    else:
        output = 'There have been ' + str(death_count) + ' deaths so far. Most recent deaths (latest first): '
    output += ', '.join(death_names)

    return output

def handle_fallen(args):
    current_run_setting = Setting.objects.filter(key='Current Run')[0]
    run = Run.objects.filter(name=current_run_setting.value)[0]

    death_objects = Death.objects.filter(run=run).order_by('respect_count')
    if len(death_objects) > 3:
        death_objects = death_objects[:3]

    output = 'The most respected fallen: '
    for death in death_objects:
        output += death.nickname + ' (' + str(death.respect_count) + '), '

    if output.endswith(', '):
        output = output[:-2]
    return output

def handle_quote(args):
    output = ''
    quote_matches = []
    quote_num = 0
    if len(args) > 0:
        if args[0].isnumeric():
            quote_num = int(args[0])
            quote_matches = Quote.objects.filter(id=quote_num)
        else:
            keyword = args[0]
            quote_matches = Quote.objects.filter(quote_text__icontains=keyword)
    else:
        quote_matches = Quote.objects.all().order_by('?')

    if len(quote_matches) > 0:
        quote = quote_matches[0]
        output = 'Quote #' + str(quote.id) + ' "' + quote.quote_text + '" -' + quote.quotee
    else:
        output = 'Quote not found'
    return output

def handle_latestquote(args):
    output = ''
    quote_matches = Quote.objects.all().order_by('-id')
    if len(quote_matches) > 0:
        quote = quote_matches[0]
        output = 'Quote #' + str(quote.id) + ' "' + quote.quote_text + '" -' + quote.quotee
    else:
        output = 'Quote not found'
    return output

def handle_addquote(args):
    if args[0] == "-q":
        quotee = args[1]
        quote_text = ' '.join(args[2:])
        quote_object = Quote(quote_text=quote_text, quotee=quotee)
    else:
        quote_text = ' '.join(args)
        quotee_setting = Setting.objects.get(key='Quotee')
        quote_object = Quote(quote_text=quote_text, quotee=quotee_setting.value)
    quote_object.save()
    return 'Quote #' + str(quote_object.id) + ' successfully added'

def handle_delquote(args):
    output = ''
    if args[0].isnumeric():
        quote_number = int(args[0])
        quote_matches = Quote.objects.filter(id=quote_number)
        if len(quote_matches) > 0:
            quote_matches[0].delete()
            output = 'Quote #' + args[0] + ' successfully deleted'
    else:
        output = 'Invalid quote number'
    return output

def handle_nuke(args):
    expiry = None
    expiry_minutes = 0
    maybe_expiry = args[0]
    phrase = ' '.join(args)
    if maybe_expiry.isnumeric():
        expiry_minutes = int(maybe_expiry)
        phrase = ' '.join(args[1:])
        utc_tz = datetime.timezone.utc
        expiry = datetime.datetime.now(utc_tz) + datetime.timedelta(minutes=expiry_minutes)

    banned_phrase = BannedPhrase(phrase=phrase, expiry=expiry)
    banned_phrase.save()

    output_text = 'The phrase "' + phrase + '" is now banned'
    if expiry_minutes > 0:
        output_text += ' for ' + str(expiry_minutes) + ' minutes'
    output = [output_text]

    chat_log_matches = ChatLog.objects.filter(line__icontains=phrase)
    for match in chat_log_matches:
        output.append('/timeout ' + match.username + ' 1')

    return output

def handle_unnuke(args):
    phrase = ' '.join(args)
    output = 'Phrase "' + phrase + '" not found'

    banned_phrase_matches = BannedPhrase.objects.filter(phrase__icontains=phrase)
    if len(banned_phrase_matches) > 0:
        for banned_phrase in banned_phrase_matches:
            banned_phrase.delete()
        output = 'The phrase "' + phrase + '" is no longer banned'

    return output

handlers = {'!setgame': handle_setgame,
            '!addcom': handle_addcom,
            '!delcom': handle_delcom,
            '!editcom': handle_editcom,
            '!alias': handle_alias,
            '!addrun': handle_addrun,
            '!setrun': handle_setrun,
            '!riprun': handle_riprun,
            '!rip': handle_rip,
            '!deaths': handle_deaths,
            '!fallen': handle_fallen,
            '!quote': handle_quote,
            '!latestquote': handle_latestquote,
            '!addquote': handle_addquote,
            '!delquote': handle_delquote,
            '!nuke': handle_nuke,
            '!unnuke': handle_unnuke,
           }

expected_args = {'!setgame': 1,
                 '!addcom': 2,
                 '!delcom': 1,
                 '!editcom': 2,
                 '!alias': 2,
                 '!addrun': 1,
                 '!setrun': 1,
                 '!riprun': 1,
                 '!rip': 1,
                 '!deaths': 0,
                 '!fallen': 0,
                 '!quote': 0,
                 '!latestquote': 0,
                 '!addquote': 1,
                 '!delquote': 1,
                 '!nuke': 1,
                 '!unnuke': 1,
                }

usage = {'!setgame': 'Usage: !setgame <pokemon game name>',
         '!addcom': 'Usage: !addcom <command> <output>',
         '!delcom': 'Usage: !delcom <command>',
         '!editcom': 'Usage: !editcom <command> <output>',
         '!alias': 'Usage: !alias <existing command> <new command>',
         '!addrun': 'Usage: !addrun <run name>',
         '!setrun': 'Usage: !setrun <run name>',
         '!riprun': 'Usage: !riprun <!lastrun text>',
         '!rip': 'Usage: !rip <pokemon nickname>',
         '!deaths': 'Usage: !deaths',
         '!fallen': 'Usage: !fallen',
         '!quote': 'Usage: !quote <optional quote number or keyword>',
         '!latestquote': 'Usage: !latestquote',
         '!addquote': 'Usage: !addquote <quote>',
         '!delquote': 'Usage: !delquote <quote number>',
         '!nuke': 'Usage: !nuke <word or phrase>',
         '!unnuke': 'Usage: !nuke <word or phrase>',
        }

def handle_admin_command(line):
    output = ''
    args = line.split(' ')
    command = args[0]
    handler = handlers.get(command)
    if handler:
        args = args[1:]
        if len(args) >= expected_args[command]:
            output = handler(args)
        else:
            output = usage[command]
    return output
