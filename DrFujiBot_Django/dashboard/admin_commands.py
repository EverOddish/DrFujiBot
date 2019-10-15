from .models import Setting, Command, SimpleOutput, Run, Death
from westwood.models import Game

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
        simple_output = command_matches[0].output
        simple_output.output_text = simple_output_text
        simple_output.save()

        command = Command(command=command_name, output=simple_output)
        command.save()

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

        output = 'Current run set to "' + run_object.name + '" playing ' + run_object.game_setting
    else:
        output = 'Run "' + run_name + '" not found'
    return output

def handle_rip(args):
    nickname = ' '.join(args)

    current_run_setting = Setting.objects.filter(key='Current Run')[0]
    run = Run.objects.filter(name=current_run_setting.value)[0]

    death_object = Death(nickname=nickname, run=run)
    death_object.save()

    death_count = Death.objects.filter(run=run).count()

    output = 'Death count: ' + str(death_count) + ' - Press F to pay respects to "' + nickname + '"'

    # TODO: Auto-marker

    return output

def handle_deaths(args):
    output = ''
    return output

def handle_fallen(args):
    output = ''
    return output

handlers = {'!setgame': handle_setgame,
            '!addcom': handle_addcom,
            '!delcom': handle_delcom,
            '!editcom': handle_editcom,
            '!alias': handle_alias,
            '!addrun': handle_addrun,
            '!setrun': handle_setrun,
            '!rip': handle_rip,
            '!deaths': handle_deaths,
            '!fallen': handle_fallen,
           }

expected_args = {'!setgame': 1,
                 '!addcom': 2,
                 '!delcom': 1,
                 '!editcom': 2,
                 '!alias': 2,
                 '!addrun': 1,
                 '!setrun': 1,
                 '!rip': 1,
                 '!deaths': 0,
                 '!fallen': 0,
                }

usage = {'!setgame': 'Usage: !setgame <pokemon game name>',
         '!addcom': 'Usage: !addcom <command> <output>',
         '!delcom': 'Usage: !delcom <command>',
         '!editcom': 'Usage: !editcom <command> <output>',
         '!alias': 'Usage: !alias <existing command> <new command>',
         '!addrun': 'Usage: !addrun <run name>',
         '!setrun': 'Usage: !setrun <run name>',
         '!rip': 'Usage: !rip <pokemon nickname>',
         '!deaths': 'Usage: !deaths',
         '!fallen': 'Usage: !fallen',
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
