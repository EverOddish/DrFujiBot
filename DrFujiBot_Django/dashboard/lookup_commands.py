from .models import Setting
from .lookup_helpers import *

from westwood.models import *

def handle_pokemon(args):
    output = ''
    pokemon_name = ' '.join(args)
    pokemon_name = correct_pokemon_name(pokemon_name)

    if pokemon_not_present(pokemon_name):
        return pokemon_name.title() + ' is not present in the current game'

    pokemon_matches = Pokemon.objects.filter(name__iexact=pokemon_name)
    if len(pokemon_matches) == 0:
        pokemon_matches = PokemonForm.objects.filter(name__iexact=pokemon_name)

    if len(pokemon_matches) > 0:
        pokemon = pokemon_matches[0]

        output = pokemon.name + ': ['

        type1, type2 = get_types_for_pokemon(pokemon.name)

        output += type1
        if len(type2) > 0:
            output += ', '
            output += type2
        output += '] '

        current_game_name = Setting.objects.filter(key='Current Game')[0]

        # First pass is to search for ROM hack stats. Second pass is to search for base game stats, if needed.
        # If not a ROM hack, stats should be found on the first pass every time.
        try_again = True
        check_base_game = False
        while try_again:
            for stat_sets_list_element in StatSetsListElement.objects.filter(list_id=pokemon.stat_sets):
                stat_set = stat_sets_list_element.element
                # Don't ask for base game stats if ROM hack stats aren't found, because they could be present in a later stat set
                if is_game_name_in_game_list(current_game_name.value, stat_set.games, check_base_game=check_base_game):
                    modified_stats = get_modified_stats(current_game_name.value, stat_set, pokemon.stat_sets)
                    output += 'HP(' + str(stat_set.hp) + ')' + modified_stats['hp'] + ' '
                    output += 'Attack(' + str(stat_set.attack) + ')' + modified_stats['attack'] + ' '
                    output += 'Defense(' + str(stat_set.defense) + ')' + modified_stats['defense'] + ' '
                    output += 'Sp. Atk(' + str(stat_set.special_attack) + ')' + modified_stats['special_attack'] + ' '
                    output += 'Sp. Def(' + str(stat_set.special_defense) + ')' + modified_stats['special_defense'] + ' '
                    output += 'Speed(' + str(stat_set.speed) + ')' + modified_stats['speed'] + ' '
                    try_again = False
                    break
            if try_again:
                check_base_game = True
                
        output += 'Abilities: '
        for ability_sets_list_element in AbilitySetsListElement.objects.filter(list_id=pokemon.ability_sets):
            ability_set = ability_sets_list_element.element
            if is_game_name_in_game_list(current_game_name.value, ability_set.games):
                for ability_records_list_element in AbilityRecordsListElement.objects.filter(list_id=ability_set.ability_records):
                    ability_record = ability_records_list_element.element
                    output += ability_record.name
                    if ability_record.hidden == 'Yes':
                        output += ' (HA)'
                    output += ', '
                break
        if output.endswith(', '):
            output = output[:-2]
    else:
        output = '"' + pokemon_name + '" was not found'
    return output

def handle_move(args):
    output = ''
    move_name = ' '.join(args)
    move_name = correct_move_name(move_name)

    if move_not_present(move_name):
        return move_name.title() + ' is not present in the current game'

    move_matches = Move.objects.filter(name__iexact=move_name)
    if move_matches:
        move = move_matches[0]

        current_game_name = Setting.objects.filter(key='Current Game')[0]

        # First pass is to search for ROM hack stats. Second pass is to search for base game stats, if needed.
        # If not a ROM hack, stats should be found on the first pass every time.
        try_again = True
        check_base_game = False
        while try_again:
            for move_records_list_element in MoveRecordsListElement.objects.filter(list_id=move.move_records):
                move_record = move_records_list_element.element
                # Don't ask for base game stats if ROM hack stats aren't found, because they could be present in a later stat set
                if is_game_name_in_game_list(current_game_name.value, move_record.games, check_base_game=check_base_game):
                    move_definition = move_record.move_definition
                    modified_move_details = get_modified_move_details(current_game_name.value, move_definition, move.move_records)
                    output = move.name + ': [' + move_definition.type_1 + ']' + modified_move_details['type'] + ' '
                    output += 'BasePower(' + str(move_definition.base_power) + ')' + modified_move_details['base_power'] + ' '
                    output += 'Class(' + move_definition.damage_category + ')' + modified_move_details['damage_category'] + ' '
                    output += 'Accuracy(' + str(move_definition.accuracy) + ')' + modified_move_details['accuracy'] + ' '
                    output += 'PP(' + str(move_definition.power_points) + ')' + modified_move_details['power_points'] + ' '
                    output += 'Priority(' + str(move_definition.priority) + ')' + modified_move_details['priority'] + ' '
                    if None != move_definition.description:
                        output += move_definition.description
                    try_again = False
                    break
            if try_again:
                check_base_game = True
    else:
        output = '"' + move_name + '" was not found'
    return output

def handle_ability(args):
    output = ''
    ability_name = ' '.join(args)
    ability_name = correct_ability_name(ability_name)
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
    pokemon_name = ' '.join(args)
    pokemon_name = correct_pokemon_name(pokemon_name)

    if pokemon_not_present(pokemon_name):
        return pokemon_name.title() + ' is not present in the current game'

    pokemon_learnset_matches = PokemonLearnsets.objects.filter(name__iexact=pokemon_name)
    if pokemon_learnset_matches:
        pokemon_learnset = pokemon_learnset_matches[0]

        current_game_name = Setting.objects.filter(key='Current Game')[0]

        output += pokemon_learnset.name + ' '
        # First pass is to search for ROM hack stats. Second pass is to search for base game stats, if needed.
        # If not a ROM hack, stats should be found on the first pass every time.
        try_again = True
        check_base_game = False
        while try_again:
            for learnsets_list_element in LearnsetsListElement.objects.filter(list_id=pokemon_learnset.learnsets):
                learnset = learnsets_list_element.element
                if is_game_name_in_game_list(current_game_name.value, learnset.games, check_base_game=check_base_game):
                    for learnset_moves_list_element in LearnsetMovesListElement.objects.filter(list_id=learnset.learnset_moves):
                        learnset_move = learnset_moves_list_element.element
                        output += '| ' + str(learnset_move.level) + ' ' + learnset_move.name + ' '
                    try_again = False
                    break
            if try_again:
                check_base_game = True
    else:
        output = 'Learnsets for "' + pokemon_name + '" were not found'
    return output

def handle_tmset(args):
    output = ''
    pokemon_name = ' '.join(args)
    pokemon_name = correct_pokemon_name(pokemon_name)

    if pokemon_not_present(pokemon_name):
        return pokemon_name.title() + ' is not present in the current game'

    pokemon_tmset_matches = PokemonTmSets.objects.filter(name__iexact=pokemon_name)
    if pokemon_tmset_matches:
        pokemon_tmset = pokemon_tmset_matches[0]

        current_game_name = Setting.objects.filter(key='Current Game')[0]

        output += pokemon_tmset.name + ': '
        # First pass is to search for ROM hack stats. Second pass is to search for base game stats, if needed.
        # If not a ROM hack, stats should be found on the first pass every time.
        try_again = True
        check_base_game = False
        while try_again:
            for tmsets_list_element in TmSetsListElement.objects.filter(list_id=pokemon_tmset.tm_sets):
                tm_set = tmsets_list_element.element
                if is_game_name_in_game_list(current_game_name.value, tm_set.games, check_base_game=check_base_game):
                    for tmset_moves_list_element in TmsetMovesListElement.objects.filter(list_id=tm_set.tmset_moves):
                        tmset_move = tmset_moves_list_element.element
                        output += tmset_move.name + ', '
                    try_again = False
                    break
            if try_again:
                check_base_game = True
        if output.endswith(', '):
            output = output[:-2]
    else:
        output = 'TM sets for "' + pokemon_name + '" were not found'
    return output

def handle_faster(args):
    output = ''
    pokemon_name_1 = args[0]
    pokemon_name_2 = args[1]

    pokemon_name_1 = correct_pokemon_name(pokemon_name_1)
    pokemon_name_2 = correct_pokemon_name(pokemon_name_2)

    if pokemon_not_present(pokemon_name_1):
        return pokemon_name_1.title() + ' is not present in the current game'
    if pokemon_not_present(pokemon_name_2):
        return pokemon_name_2.title() + ' is not present in the current game'

    pokemon_matches_1 = Pokemon.objects.filter(name__iexact=pokemon_name_1)
    pokemon_matches_2 = Pokemon.objects.filter(name__iexact=pokemon_name_2)

    if len(pokemon_matches_1) == 0:
        pokemon_matches_1 = PokemonForm.objects.filter(name__iexact=pokemon_name_1)
    if len(pokemon_matches_2) == 0:
        pokemon_matches_2 = PokemonForm.objects.filter(name__iexact=pokemon_name_2)

    if len(pokemon_matches_1) > 0:
        if len(pokemon_matches_2) > 0:
            pokemon_1 = pokemon_matches_1[0]
            pokemon_2 = pokemon_matches_2[0]
            speed_1 = 0
            speed_2 = 0

            current_game_name = Setting.objects.filter(key='Current Game')[0]

            # First pass is to search for ROM hack stats. Second pass is to search for base game stats, if needed.
            # If not a ROM hack, stats should be found on the first pass every time.
            try_again = True
            check_base_game = False
            while try_again:
                for stat_sets_list_element in StatSetsListElement.objects.filter(list_id=pokemon_1.stat_sets):
                    stat_set = stat_sets_list_element.element
                    # Don't ask for base game stats if ROM hack stats aren't found, because they could be present in a later stat set
                    if is_game_name_in_game_list(current_game_name.value, stat_set.games, check_base_game=check_base_game):
                        modified_stats_1 = get_modified_stats(current_game_name.value, stat_set, pokemon_1.stat_sets)
                        speed_1 = stat_set.speed
                        try_again = False
                        break
                if try_again:
                    check_base_game = True

            try_again = True
            check_base_game = False
            while try_again:
                for stat_sets_list_element in StatSetsListElement.objects.filter(list_id=pokemon_2.stat_sets):
                    stat_set = stat_sets_list_element.element
                    if is_game_name_in_game_list(current_game_name.value, stat_set.games, check_base_game=check_base_game):
                        modified_stats_2 = get_modified_stats(current_game_name.value, stat_set, pokemon_2.stat_sets)
                        speed_2 = stat_set.speed
                        try_again = False
                        break
                if try_again:
                    check_base_game = True

            if speed_1 == speed_2:
                output = pokemon_1.name + ' and ' + pokemon_2.name + ' are tied for speed (' + str(speed_1) + ')'
            elif speed_1 > speed_2:
                output = pokemon_1.name + ' (' + str(speed_1) + ')' + modified_stats_1['speed'] + ' is faster than ' + pokemon_2.name + ' (' + str(speed_2) + ')' + modified_stats_2['speed']
            elif speed_1 < speed_2:
                output = pokemon_1.name + ' (' + str(speed_1) + ')' + modified_stats_1['speed'] + ' is slower than ' + pokemon_2.name + ' (' + str(speed_2) + ')' + modified_stats_2['speed']
        else:
            output = '"' + pokemon_name_2 + '" was not found'
    else:
        output = '"' + pokemon_name_1 + '" was not found'
    return output

def handle_item(args):
    output = ''
    item_name = ' '.join(args)
    item_matches = Item.objects.filter(name__iexact=item_name)
    if item_matches:
        item = item_matches[0]
        output = item.name + ': ' + item.description + ' (Buy for $' + str(item.cost) + ')'
    else:
        output = '"' + item_name + '" was not found'
    return output

def handle_evolve(args):
    output = ''
    pokemon_name = ' '.join(args)
    pokemon_name = correct_pokemon_name(pokemon_name)

    if pokemon_not_present(pokemon_name):
        return pokemon_name.title() + ' is not present in the current game'

    pokemon_matches = Pokemon.objects.filter(name__iexact=pokemon_name)
    if pokemon_matches:
        pokemon = pokemon_matches[0]

        current_game_name = Setting.objects.filter(key='Current Game')[0]

        evolution_set_list_elements = EvolutionSetsListElement.objects.filter(list_id=pokemon.evolution_sets)
        if len(evolution_set_list_elements) > 0:
            for evolution_set_list_element in evolution_set_list_elements:
                evolution_set = evolution_set_list_element.element
                if is_game_name_in_game_list(current_game_name.value, evolution_set.games):
                    for evolution_records_list_element in EvolutionRecordsListElement.objects.filter(list_id=evolution_set.evolution_records):
                        evolution_record = evolution_records_list_element.element
                        output += pokemon.name + ' evolves into ' + str(evolution_record.evolves_to)
                        if evolution_record.level > 0:
                             output += ' at level ' + str(evolution_record.level)
                        if len(evolution_record.method) > 0:
                            output += ' ' + evolution_record.method
                        output += '. '
        else:
            output = pokemon.name + ' does not evolve.'
    else:
        output = '"' + pokemon_name + '" was not found'
    return output

def handle_weak(args):
    output = ''
    prefix = ' '.join(args).title()
    type_or_pokemon_name = ' '.join(args)
    weak_to = []
    type1 = ''
    type2 = ''

    if is_type(args[0]):
        type1 = args[0]
        if len(args) > 1:
            type2 = args[1]
    else:
        pokemon_name = correct_pokemon_name(type_or_pokemon_name)

        if pokemon_not_present(pokemon_name):
            return pokemon_name.title() + ' is not present in the current game'

        pokemon_objects = Pokemon.objects.filter(name__iexact=pokemon_name)

        if len(pokemon_objects) == 0:
            pokemon_objects = PokemonForm.objects.filter(name__iexact=pokemon_name)

        if len(pokemon_objects) > 0:
            pokemon = pokemon_objects[0]
            type1, type2 = get_types_for_pokemon(pokemon.name)
            prefix = pokemon.name
        else:
            # All lookups failed
            return '"' + type_or_pokemon_name + '" is not a type or a Pokemon'

    weak_to, resistances, no_damage = get_type_advantages_for_type_pair(type1, type2)
    weak_to = set(weak_to)

    if len(weak_to) > 0:
        output = prefix + ' is weak to: ' + ', '.join(weak_to)
    else:
        output = prefix + ' has no weaknesses'

    return output

def handle_resist(args):
    output = ''
    prefix = ' '.join(args).title()
    type_or_pokemon_name = ' '.join(args)
    resistant_to = []
    type1 = ''
    type2 = ''

    if is_type(args[0]):
        type1 = args[0]
        if len(args) > 1:
            type2 = args[1]
    else:
        pokemon_name = correct_pokemon_name(type_or_pokemon_name)

        if pokemon_not_present(pokemon_name):
            return pokemon_name.title() + ' is not present in the current game'

        pokemon_objects = Pokemon.objects.filter(name__iexact=pokemon_name)

        if len(pokemon_objects) == 0:
            pokemon_objects = PokemonForm.objects.filter(name__iexact=pokemon_name)

        if len(pokemon_objects) > 0:
            pokemon = pokemon_objects[0]
            type1, type2 = get_types_for_pokemon(pokemon.name)
            prefix = pokemon.name
        else:
            # All lookups failed
            return '"' + type_or_pokemon_name + '" is not a type or a Pokemon'

    weaknesses, resistant_to, no_damage = get_type_advantages_for_type_pair(type1, type2)
    resistant_to = set(resistant_to)

    if len(resistant_to) > 0:
        output = prefix + ' is resistant to: ' + ', '.join(resistant_to)
    else:
        output = prefix + ' has no resistances'

    return output

def handle_type(args):
    output = ''
    attacking_type_name = args[0].title()
    defending_type_1_name = args[2]
    defending_type_2_name = ''
    if len(args) >= 4:
        defending_type_2_name = args[3]

    if not is_type(attacking_type_name):
        return '"' + attacking_type_name + '" is not a valid type'
    if not is_type(defending_type_1_name):
        return '"' + defending_type_1_name + '" is not a valid type'
    if len(defending_type_2_name) > 0 and not is_type(defending_type_2_name):
        return '"' + defending_type_2_name + '" is not a valid type'

    weaknesses, resistances, no_damage = get_type_advantages_for_type_pair(defending_type_1_name, defending_type_2_name)

    output = attacking_type_name.capitalize()

    if attacking_type_name in no_damage:
        output += " does no damage"
    elif attacking_type_name in weaknesses:
        output += " is super effective ("
        if weaknesses.count(attacking_type_name) == 1:
            output += "2x)"
        elif weaknesses.count(attacking_type_name) == 2:
            output += "4x)"
    elif attacking_type_name in resistances:
        output += " is not very effective ("
        if resistances.count(attacking_type_name) == 1:
            output += "0.5x)"
        elif resistances.count(attacking_type_name) == 2:
            output += "0.25x)"
    else:
        output += " does normal damage"

    output += " against " + defending_type_1_name.capitalize()
    if len(defending_type_2_name) > 0:
        output += "/" + defending_type_2_name.capitalize()

    return output

def handle_catch_rate(args):
    output = ''
    pokemon_name = ' '.join(args)
    pokemon_name = correct_pokemon_name(pokemon_name)

    if pokemon_not_present(pokemon_name):
        return pokemon_name.title() + ' is not present in the current game'

    pokemon_matches = Pokemon.objects.filter(name__iexact=pokemon_name)
    if pokemon_matches:
        pokemon = pokemon_matches[0]

        output = pokemon.name + ' catch rate: ' + str(pokemon.catch_rate)
    else:
        output = '"' + pokemon_name + '" was not found'
    return output
 
def handle_exp_curve(args):
    output = ''
    pokemon_name = ' '.join(args)
    pokemon_name = correct_pokemon_name(pokemon_name)
    
    if pokemon_not_present(pokemon_name):
        return pokemon_name.title() + ' is not present in the current game'

    pokemon_matches = Pokemon.objects.filter(name__iexact=pokemon_name)
    if pokemon_matches:
        pokemon = pokemon_matches[0]

        output = pokemon.name + ' exp. curve/growth rate: ' + str(pokemon.growth_rate)
    else:
        output = '"' + pokemon_name + '" was not found'
    return output

def handle_offence(args):
    output = ''
    pokemon_name = ' '.join(args)
    pokemon_name = correct_pokemon_name(pokemon_name)

    if pokemon_not_present(pokemon_name):
        return pokemon_name.title() + ' is not present in the current game'

    pokemon_matches = Pokemon.objects.filter(name__iexact=pokemon_name)
    if len(pokemon_matches) == 0:
        pokemon_matches = PokemonForm.objects.filter(name__iexact=pokemon_name)

    if len(pokemon_matches) > 0:
        pokemon = pokemon_matches[0]
        output = pokemon.name + ': '

        current_game_name = Setting.objects.filter(key='Current Game')[0]

        # First pass is to search for ROM hack stats. Second pass is to search for base game stats, if needed.
        # If not a ROM hack, stats should be found on the first pass every time.
        try_again = True
        check_base_game = False
        while try_again:
            for stat_sets_list_element in StatSetsListElement.objects.filter(list_id=pokemon.stat_sets):
                stat_set = stat_sets_list_element.element
                # Don't ask for base game stats if ROM hack stats aren't found, because they could be present in a later stat set
                if is_game_name_in_game_list(current_game_name.value, stat_set.games, check_base_game=check_base_game):
                    modified_stats = get_modified_stats(current_game_name.value, stat_set, pokemon.stat_sets)
                    output += 'Attack(' + str(stat_set.attack) + ')' + modified_stats['attack'] + ' '
                    output += 'Sp. Atk(' + str(stat_set.special_attack) + ')' + modified_stats['special_attack'] + ' '
                    output += 'Speed(' + str(stat_set.speed) + ')' + modified_stats['speed'] + ' '
                    try_again = False
                    break
            if try_again:
                check_base_game = True
    else:
        output = '"' + pokemon_name + '" was not found'
    return output

def handle_defence(args):
    output = ''
    pokemon_name = ' '.join(args)
    pokemon_name = correct_pokemon_name(pokemon_name)

    if pokemon_not_present(pokemon_name):
        return pokemon_name.title() + ' is not present in the current game'

    pokemon_matches = Pokemon.objects.filter(name__iexact=pokemon_name)
    if len(pokemon_matches) == 0:
        pokemon_matches = PokemonForm.objects.filter(name__iexact=pokemon_name)

    if pokemon_matches:
        pokemon = pokemon_matches[0]
        output = pokemon.name + ': '

        current_game_name = Setting.objects.filter(key='Current Game')[0]

        # First pass is to search for ROM hack stats. Second pass is to search for base game stats, if needed.
        # If not a ROM hack, stats should be found on the first pass every time.
        try_again = True
        check_base_game = False
        while try_again:
            for stat_sets_list_element in StatSetsListElement.objects.filter(list_id=pokemon.stat_sets):
                stat_set = stat_sets_list_element.element
                # Don't ask for base game stats if ROM hack stats aren't found, because they could be present in a later stat set
                if is_game_name_in_game_list(current_game_name.value, stat_set.games, check_base_game=check_base_game):
                    modified_stats = get_modified_stats(current_game_name.value, stat_set, pokemon.stat_sets)
                    output += 'HP(' + str(stat_set.hp) + ')' + modified_stats['hp'] + ' '
                    output += 'Defense(' + str(stat_set.defense) + ')' + modified_stats['defense'] + ' '
                    output += 'Sp. Def(' + str(stat_set.special_defense) + ')' + modified_stats['special_defense'] + ' '
                    try_again = False
                    break
            if try_again:
                check_base_game = True
    else:
        output = '"' + pokemon_name + '" was not found'
    return output

def handle_whatis(args):
    output = ''
    move_or_ability_name = ' '.join(args)

    move_name = correct_move_name(move_or_ability_name)
    move_matches = Move.objects.filter(name__iexact=move_name)
    if move_matches:

        if move_not_present(move_name):
            return move_name.title() + ' is not present in the current game'

        output = 'Move: '
        return output + handle_move(args)

    ability_name = correct_ability_name(move_or_ability_name)
    ability_matches = Ability.objects.filter(name__iexact=ability_name)
    if ability_matches:
        output = 'Ability: '
        return output + handle_ability(args)

def handle_does(args):
    output = ''
    pokemon_name = []
    move_name = []
    found_learn = False

    for arg in args:
        if 'learn' == arg:
            found_learn = True
        else:
            if not found_learn:
                pokemon_name.append(arg)
            else:
                move_name.append(arg)

    pokemon_name = ' '.join(pokemon_name)
    pokemon_name = correct_pokemon_name(pokemon_name)

    if pokemon_not_present(pokemon_name):
        return pokemon_name.title() + ' is not present in the current game'

    move_name = ' '.join(move_name)
    move_name = correct_move_name(move_name)

    if move_not_present(move_name):
        return move_name.title() + ' is not present in the current game'

    pokemon_learnset_matches = PokemonLearnsets.objects.filter(name__iexact=pokemon_name)
    if pokemon_learnset_matches:
        pokemon_learnset = pokemon_learnset_matches[0]

        current_game_name = Setting.objects.filter(key='Current Game')[0]

        # First pass is to search for ROM hack stats. Second pass is to search for base game stats, if needed.
        # If not a ROM hack, stats should be found on the first pass every time.
        try_again = True
        check_base_game = False
        while try_again:
            for learnsets_list_element in LearnsetsListElement.objects.filter(list_id=pokemon_learnset.learnsets):
                learnset = learnsets_list_element.element
                if is_game_name_in_game_list(current_game_name.value, learnset.games, check_base_game=check_base_game):
                    for learnset_moves_list_element in LearnsetMovesListElement.objects.filter(list_id=learnset.learnset_moves):
                        learnset_move = learnset_moves_list_element.element
                        if learnset_move.name.lower() == move_name.lower():
                            output = pokemon_name.capitalize() + ' learns ' + learnset_move.name + ' at level ' + str(learnset_move.level)
                    try_again = False
                    break
            if try_again:
                check_base_game = True

        if len(output) == 0:
            pokemon_tmset_matches = PokemonTmSets.objects.filter(name__iexact=pokemon_name)
            if pokemon_tmset_matches:
                pokemon_tmset = pokemon_tmset_matches[0]

                # First pass is to search for ROM hack stats. Second pass is to search for base game stats, if needed.
                # If not a ROM hack, stats should be found on the first pass every time.
                try_again = True
                check_base_game = False
                while try_again:
                    for tmsets_list_element in TmSetsListElement.objects.filter(list_id=pokemon_tmset.tm_sets):
                        tm_set = tmsets_list_element.element
                        if is_game_name_in_game_list(current_game_name.value, tm_set.games, check_base_game=check_base_game):
                            for tmset_moves_list_element in TmsetMovesListElement.objects.filter(list_id=tm_set.tmset_moves):
                                tmset_move = tmset_moves_list_element.element
                                if tmset_move.name.lower() == move_name.lower():
                                    output = pokemon_name.capitalize() + ' learns ' + tmset_move.name + ' by TM/HM'
                            try_again = False
                            break
                    if try_again:
                        check_base_game = True

        if len(output) == 0:
            pokemon_tutor_set_matches = PokemonTutorSets.objects.filter(name__iexact=pokemon_name)
            if pokemon_tutor_set_matches:
                pokemon_tutor_set = pokemon_tutor_set_matches[0]

                # First pass is to search for ROM hack stats. Second pass is to search for base game stats, if needed.
                # If not a ROM hack, stats should be found on the first pass every time.
                try_again = True
                check_base_game = False
                while try_again:
                    for tutor_sets_list_element in TutorSetsListElement.objects.filter(list_id=pokemon_tutor_set.tutor_sets):
                        tutor_set = tutor_sets_list_element.element
                        if is_game_name_in_game_list(current_game_name.value, tutor_set.games, check_base_game=check_base_game):
                            for tutor_set_moves_list_element in TutorSetMovesListElement.objects.filter(list_id=tutor_set.tutor_set_moves):
                                tutor_set_move = tutor_set_moves_list_element.element
                                if tutor_set_move.name.lower() == move_name.lower():
                                    output = pokemon_name.capitalize() + ' learns ' + tutor_set_move.name + ' by Move Tutor'
                            try_again = False
                            break
                    if try_again:
                        if check_base_game:
                            # Already tried base game and still found nothing, so stop searching.
                            break
                        else:
                            check_base_game = True

        print(output)
        if len(output) == 0:
            output = pokemon_name.title() + ' does not learn ' + move_name.title()
    else:
        output = 'Move data for "' + pokemon_name + '" was not found in the current game'

    return output

def handle_grassknot(args):
    output = ''
    pokemon_name = ' '.join(args)
    pokemon_name = correct_pokemon_name(pokemon_name)

    if pokemon_not_present(pokemon_name):
        return pokemon_name.title() + ' is not present in the current game'

    pokemon_matches = Pokemon.objects.filter(name__iexact=pokemon_name)
    if len(pokemon_matches) == 0:
        pokemon_matches = PokemonForm.objects.filter(name__iexact=pokemon_name)

    if len(pokemon_matches) > 0:
        pokemon = pokemon_matches[0]
        output = 'Grass Knot/Low Kick has '
        if pokemon.weight < 100:
            bp = "20"
        elif pokemon.weight < 250:
            bp = "40"
        elif pokemon.weight < 500:
            bp = "60"
        elif pokemon.weight < 1000:
            bp = "80"
        elif pokemon.weight < 2000:
            bp = "100"
        else:
            bp = "120"

        output += bp
        output += " base power against " + pokemon.name + " ("
        output += str(float(pokemon.weight) / 10)
        output += " kg)"
    else:
        output = '"' + pokemon_name + '" was not found'
    return output

def handle_baseexp(args):
    output = ''
    pokemon_name = ' '.join(args)
    pokemon_name = correct_pokemon_name(pokemon_name)

    if pokemon_not_present(pokemon_name):
        return pokemon_name.title() + ' is not present in the current game'

    pokemon_matches = Pokemon.objects.filter(name__iexact=pokemon_name)
    if len(pokemon_matches) == 0:
        pokemon_matches = PokemonForm.objects.filter(name__iexact=pokemon_name)

    if len(pokemon_matches) > 0:
        pokemon = pokemon_matches[0]
        output = pokemon.name + ': '
        output += str(pokemon.base_exp)
        output += ' base exp.'
    else:
        output = '"' + pokemon_name + '" was not found'
    return output

def handle_evyield(args):
    output = ''
    pokemon_name = ' '.join(args)
    pokemon_name = correct_pokemon_name(pokemon_name)

    if pokemon_not_present(pokemon_name):
        return pokemon_name.title() + ' is not present in the current game'

    pokemon_matches = Pokemon.objects.filter(name__iexact=pokemon_name)
    if len(pokemon_matches) == 0:
        pokemon_matches = PokemonForm.objects.filter(name__iexact=pokemon_name)

    if len(pokemon_matches) > 0:
        pokemon = pokemon_matches[0]
        output = pokemon.name + ' EV Yield: '
        for ev_yields_list_element in EvYieldsListElement.objects.filter(list_id=pokemon.ev_yields):
            ev_yield = ev_yields_list_element.element
            output += ev_yield.stat + '(' + str(ev_yield.value) + ') '
    else:
        output = '"' + pokemon_name + '" was not found'
    return output

def handle_nature(args):
    output = ''
    nature_name = args[0]
    nature_matches = Nature.objects.filter(name__iexact=nature_name)
    if nature_matches:
        nature = nature_matches[0]
        output = nature.name + ': '
        if 'None' == nature.increased_stat:
            output += 'Neutral'
        else:
            output += '+' + nature.increased_stat + ' -' + nature.decreased_stat
    else:
        output = '"' + nature_name + '" was not found'
    return output

handlers = {'!pokemon': handle_pokemon,
            '!move': handle_move,
            '!ability': handle_ability,
            '!learnset': handle_learnset,
            '!tmset': handle_tmset,
            '!faster': handle_faster,
            '!item': handle_item,
            '!evolve': handle_evolve,
            '!weak': handle_weak,
            '!resist': handle_resist,
            '!type': handle_type,
            '!catchrate': handle_catch_rate,
            '!expcurve': handle_exp_curve,
            '!offence': handle_offence,
            '!offense': handle_offence,
            '!defence': handle_defence,
            '!defense': handle_defence,
            '!whatis': handle_whatis,
            '!does': handle_does,
            '!grassknot': handle_grassknot,
            '!lowkick': handle_grassknot,
            '!baseexp': handle_baseexp,
            '!evyield': handle_evyield,
            '!nature': handle_nature,
           }

expected_args = {'!pokemon': 1,
                 '!move': 1,
                 '!ability': 1,
                 '!learnset': 1,
                 '!tmset': 1,
                 '!faster': 2,
                 '!item': 1,
                 '!evolve': 1,
                 '!weak': 1,
                 '!resist': 1,
                 '!type': 3,
                 '!catchrate': 1,
                 '!expcurve': 1,
                 '!offence': 1,
                 '!offense': 1,
                 '!defence': 1,
                 '!defense': 1,
                 '!whatis': 1,
                 '!does': 3,
                 '!grassknot': 1,
                 '!lowkick': 1,
                 '!baseexp': 1,
                 '!evyield': 1,
                 '!nature': 1,
                }

usage = {'!pokemon': 'Usage: !pokemon <pokemon name>',
          '!move': 'Usage: !move <move name>',
          '!ability': 'Usage: !ability <ability name>',
          '!learnset': 'Usage: !learnset <pokemon name>',
          '!tmset': 'Usage: !tmset <pokemon name>',
          '!faster': 'Usage: !faster <pokemon name 1> <pokemon name 2>',
          '!item': 'Usage: !item <item name>',
          '!evolve': 'Usage: !evolve <pokemon name>',
          '!weak': 'Usage: !weak <type or pokemon name>',
          '!resist': 'Usage: !resist <type or pokemon name>',
          '!type': 'Usage: !type <type 1> against <type 2> <type 3>',
          '!catchrate': 'Usage: !catchrate <pokemon name>',
          '!expcurve': 'Usage: !expcurve <pokemon name>',
          '!offence': 'Usage: !offence <pokemon name>',
          '!offense': 'Usage: !offense <pokemon name>',
          '!defence': 'Usage: !defence <pokemon name>',
          '!defense': 'Usage: !defense <pokemon name>',
          '!whatis': 'Usage: !whatis <move or ability name>',
          '!does': 'Usage: !does <pokemon name> learn <move name>',
          '!grassknot': 'Usage: !grassknot <pokemon name>',
          '!lowkick': 'Usage: !lowkick <pokemon name>',
          '!baseexp': 'Usage: !baseexp <pokemon name>',
          '!evyield': 'Usage: !evyield <pokemon name>',
          '!nature': 'Usage: !nature <nature name>',
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
