from .models import Setting, Command, SimpleOutput

def handle_setgame(args):
    output = ''
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

handlers = {'!setgame': handle_setgame,
            '!addcom': handle_addcom,
            '!delcom': handle_delcom,
            '!editcom': handle_editcom,
           }

expected_args = {'!setgame': 1,
                 '!addcom': 2,
                 '!delcom': 1,
                 '!editcom': 2,
                }

usage = {'!setgame': 'Usage: !setgame <pokemon game name>',
         '!addcom': 'Usage: !addcom <command> <output>',
         '!delcom': 'Usage: !delcom <command>',
         '!editcom': 'Usage: !editcom <command> <output>',
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
