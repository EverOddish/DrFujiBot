from westwood.models import *

def handle_pokemon(args):
    output = ''
    pokemon_name = args[0]
    pokemon_matches = Pokemon.objects.filter(name__iexact=pokemon_name)
    if pokemon_matches:
        pokemon = pokemon_matches[0]
        output = pokemon.name + ': [type] HP('
    else:
        output = '"' + pokemon_name + '" was not found'
    return output

def handle_move(args):
    output = ''
    move_name = args[0]
    move_matches = Move.objects.filter(name__iexact=move_name)
    if move_matches:
        move = move_matches[0]
        output = move.name + ': [' + move.type_1 + '] '
        output += 'BasePower(' + move.base_power + ') '
        output += 'Class(' + move.damage_category + ') '
        output += 'Accuracy(' + move.accuracy + ') '
        output += 'PP(' + str(move.power_points) + ') '
        output += 'Priority(' + move.priority + ') '
        #output += move.description
    else:
        output = '"' + move_name + '" was not found'
    return output

def handle_ability(args):
    output = ''
    ability_name = args[0]
    ability_matches = Ability.objects.filter(name__iexact=ability_name)
    if ability_matches:
        ability = ability_matches[0]
        # TODO: Say which generation the ability was introduced in
        output = ability.name + ': ' + ability.description
    else:
        output = '"' + ability_name + '" was not found'
    return output

def handle_learnset(args):
    output = ''
    pokemon_name = args[0]
    pokemon_learnset_matches = PokemonLearnsets.objects.filter(name__iexact=pokemon_name)
    if pokemon_learnset_matches:
        pokemon_learnset = pokemon_learnset_matches[0]
        output += pokemon_learnset.name + ' '
        for learnsets_list_element in LearnsetsListElement.objects.filter(list_id=pokemon_learnset.learnsets):
            learnset = learnsets_list_element.element
            # TODO: Filter based on current game
            for learnset_moves_list_element in LearnsetMovesListElement.objects.filter(list_id=learnset.learnset_moves):
                learnset_move = learnset_moves_list_element.element
                output += '| ' + str(learnset_move.level) + ' ' + learnset_move.name + ' '
    else:
        output = 'Learnsets for "' + ability_name + '" were not found'
    return output

def handle_tmset(args):
    output = ''
    pokemon_name = args[0]
    return output

handlers = {'!pokemon': handle_pokemon,
            '!move': handle_move,
            '!ability': handle_ability,
            '!learnset': handle_learnset,
            '!tmset': handle_tmset,
           }

expected_args = {'!pokemon': 1,
                 '!move': 1,
                 '!ability': 1,
                 '!learnset': 1,
                 '!tmset': 1,
                }

usage = {'!pokemon': 'Usage: !pokemon <pokemon name>',
          '!move': 'Usage: !move <move name>',
          '!ability': 'Usage: !ability <ability name>',
          '!learnset': 'Usage: !learnset <pokemon name>',
          '!tmset': 'Usage: !tmset <pokemon name>',
         }

def handle_lookup_command(line):
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
