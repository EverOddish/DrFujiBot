from .models import Setting
from .lookup_helpers import *

from westwood.models import *

def handle_pokemon(args):
    output = ''
    pokemon_name = ' '.join(args)
    pokemon_name = correct_pokemon_name(pokemon_name)

    pokemon_matches = Pokemon.objects.filter(name__iexact=pokemon_name)
    if len(pokemon_matches) == 0:
        pokemon_matches = PokemonForm.objects.filter(name__iexact=pokemon_name)

    if len(pokemon_matches) > 0:
        pokemon = pokemon_matches[0]
        output = pokemon.name + ': ['

        current_game_name = Setting.objects.filter(key='Current Game')[0]

        for type_sets_list_element in TypeSetsListElement.objects.filter(list_id=pokemon.type_sets):
            type_set = type_sets_list_element.element
            if is_game_name_in_game_list(current_game_name.value, type_set.games):
                output += type_set.type1
                if len(type_set.type2) > 0:
                    output += ', '
                    output += type_set.type2
                break
        output += '] '

        for stat_sets_list_element in StatSetsListElement.objects.filter(list_id=pokemon.stat_sets):
            stat_set = stat_sets_list_element.element
            # Don't ask for base game stats if ROM hack stats aren't found, because they could be present in a later stat set
            if is_game_name_in_game_list(current_game_name.value, stat_set.games, check_base_game=False):
                modified_stats = get_modified_stats(current_game_name.value, stat_set, pokemon.stat_sets)
                output += 'HP(' + str(stat_set.hp) + ')' + modified_stats['hp'] + ' '
                output += 'Attack(' + str(stat_set.attack) + ')' + modified_stats['attack'] + ' '
                output += 'Defense(' + str(stat_set.defense) + ')' + modified_stats['defense'] + ' '
                output += 'Sp. Atk(' + str(stat_set.special_attack) + ')' + modified_stats['special_attack'] + ' '
                output += 'Sp. Def(' + str(stat_set.special_defense) + ')' + modified_stats['special_defense'] + ' '
                output += 'Speed(' + str(stat_set.speed) + ')' + modified_stats['speed'] + ' '
                break
                
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
    move_matches = Move.objects.filter(name__iexact=move_name)
    if move_matches:
        move = move_matches[0]

        current_game_name = Setting.objects.filter(key='Current Game')[0]

        for move_records_list_element in MoveRecordsListElement.objects.filter(list_id=move.move_records):
            move_record = move_records_list_element.element
            if is_game_name_in_game_list(current_game_name.value, move_record.games):
                move_definition = move_record.move_definition
                output = move.name + ': [' + move_definition.type_1 + '] '
                output += 'BasePower(' + str(move_definition.base_power) + ') '
                output += 'Class(' + move_definition.damage_category + ') '
                output += 'Accuracy(' + str(move_definition.accuracy) + ') '
                output += 'PP(' + str(move_definition.power_points) + ') '
                output += 'Priority(' + str(move_definition.priority) + ') '
                #output += move.description
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
    pokemon_learnset_matches = PokemonLearnsets.objects.filter(name__iexact=pokemon_name)
    if pokemon_learnset_matches:
        pokemon_learnset = pokemon_learnset_matches[0]

        current_game_name = Setting.objects.filter(key='Current Game')[0]

        output += pokemon_learnset.name + ' '
        for learnsets_list_element in LearnsetsListElement.objects.filter(list_id=pokemon_learnset.learnsets):
            learnset = learnsets_list_element.element
            if is_game_name_in_game_list(current_game_name.value, learnset.games):
                for learnset_moves_list_element in LearnsetMovesListElement.objects.filter(list_id=learnset.learnset_moves):
                    learnset_move = learnset_moves_list_element.element
                    output += '| ' + str(learnset_move.level) + ' ' + learnset_move.name + ' '
                break
    else:
        output = 'Learnsets for "' + pokemon_name + '" were not found'
    return output

def handle_tmset(args):
    output = ''
    pokemon_name = ' '.join(args)
    pokemon_name = correct_pokemon_name(pokemon_name)
    pokemon_tmset_matches = PokemonTmSets.objects.filter(name__iexact=pokemon_name)
    if pokemon_tmset_matches:
        pokemon_tmset = pokemon_tmset_matches[0]

        current_game_name = Setting.objects.filter(key='Current Game')[0]

        output += pokemon_tmset.name + ': '
        for tmsets_list_element in TmSetsListElement.objects.filter(list_id=pokemon_tmset.tm_sets):
            tm_set = tmsets_list_element.element
            if is_game_name_in_game_list(current_game_name.value, tm_set.games):
                for tmset_moves_list_element in TmsetMovesListElement.objects.filter(list_id=tm_set.tmset_moves):
                    tmset_move = tmset_moves_list_element.element
                    output += tmset_move.name + ', '
                break
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

            for stat_sets_list_element in StatSetsListElement.objects.filter(list_id=pokemon_1.stat_sets):
                stat_set = stat_sets_list_element.element
                if is_game_name_in_game_list(current_game_name.value, stat_set.games):
                    speed_1 = stat_set.speed
                    break

            for stat_sets_list_element in StatSetsListElement.objects.filter(list_id=pokemon_2.stat_sets):
                stat_set = stat_sets_list_element.element
                if is_game_name_in_game_list(current_game_name.value, stat_set.games):
                    speed_2 = stat_set.speed
                    break

            if speed_1 == speed_2:
                output = pokemon_1.name + ' and ' + pokemon_2.name + ' are tied for speed (' + str(speed_1)
            elif speed_1 > speed_2:
                output = pokemon_1.name + ' (' + str(speed_1) + ') is faster than ' + pokemon_2.name + ' (' + str(speed_2) + ')'
            elif speed_1 < speed_2:
                output = pokemon_1.name + ' (' + str(speed_1) + ') is slower than ' + pokemon_2.name + ' (' + str(speed_2) + ')'
        else:
            output = '"' + pokemon_name_2 + '" was not found'
    else:
        output = '"' + pokemon_name_1 + '" was not found'
    return output

def handle_item(args):
    output = ''
    item_name = args[0]
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
                             + ' at level ' + str(evolution_record.level)
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
    type_name = args[0]
    weak_to = []

    current_game_name = Setting.objects.filter(key='Current Game')[0]

    for effectiveness_sets_list_element in EffectivenessSetsListElement.objects.all():
        effectiveness_set = effectiveness_sets_list_element.element
        if is_game_name_in_game_list(current_game_name.value, effectiveness_set.games):
            for effectiveness_records_list_element in EffectivenessRecordsListElement.objects.filter(list_id=effectiveness_set.effectiveness_records):
                effectiveness_record = effectiveness_records_list_element.element
                if effectiveness_record.target_type.lower() == type_name.lower() and effectiveness_record.damage_factor > 100:
                    weak_to.append(effectiveness_record.source_type)
            break

    if len(weak_to) > 0:
        output = type_name.title() + ' is weak to: ' + ', '.join(weak_to)
    else:
        output = type_name.title() + ' has no weaknesses'

    return output

def handle_resist(args):
    output = ''
    type_name = args[0]
    resistant_to = []

    current_game_name = Setting.objects.filter(key='Current Game')[0]

    for effectiveness_sets_list_element in EffectivenessSetsListElement.objects.all():
        effectiveness_set = effectiveness_sets_list_element.element
        if is_game_name_in_game_list(current_game_name.value, effectiveness_set.games):
            for effectiveness_records_list_element in EffectivenessRecordsListElement.objects.filter(list_id=effectiveness_set.effectiveness_records):
                effectiveness_record = effectiveness_records_list_element.element
                if effectiveness_record.target_type.lower() == type_name.lower() and effectiveness_record.damage_factor != 0 and effectiveness_record.damage_factor < 100:
                    resistant_to.append(effectiveness_record.source_type)
            break

    if len(resistant_to) > 0:
        output = type_name.title() + ' is resistant to: ' + ', '.join(resistant_to)
    else:
        output = type_name.title() + ' has no resistances'

    return output

def handle_type(args):
    output = ''
    attacking_type_name = args[0].title()
    defending_type_1_name = args[2]
    defending_type_2_name = ''
    if len(args) >= 4:
        defending_type_2_name = args[3]

    current_game_name = Setting.objects.filter(key='Current Game')[0]

    weaknesses = []
    resistances = []
    no_damage = []

    for effectiveness_sets_list_element in EffectivenessSetsListElement.objects.all():
        effectiveness_set = effectiveness_sets_list_element.element
        if is_game_name_in_game_list(current_game_name.value, effectiveness_set.games):
            for effectiveness_records_list_element in EffectivenessRecordsListElement.objects.filter(list_id=effectiveness_set.effectiveness_records):
                effectiveness_record = effectiveness_records_list_element.element

                if effectiveness_record.target_type.lower() == defending_type_1_name.lower() or effectiveness_record.target_type.lower() == defending_type_2_name.lower():
                    if effectiveness_record.damage_factor == 0:
                        no_damage.append(effectiveness_record.source_type)
                    elif effectiveness_record.damage_factor > 100:
                        weaknesses.append(effectiveness_record.source_type)
                    elif effectiveness_record.damage_factor < 100:
                        resistances.append(effectiveness_record.source_type)
            break

    # Take out no-damage types outright.
    weaknesses = [
        w for w in weaknesses if w not in no_damage
    ]
    resistances = [
        r for r in resistances if r not in no_damage
    ]

    weaknesses_copy = weaknesses[:]

    # Reduce weakness instance by one for each resistance.
    for r in resistances:
        if r in weaknesses:
            weaknesses.remove(r)

    # Reduce resistance instance by one for each weakness.
    for w in weaknesses_copy:
        if w in resistances:
            resistances.remove(w)

    output = attacking_type_name.capitalize()
    print(weaknesses)
    print(resistances)

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

    pokemon_matches = Pokemon.objects.filter(name__iexact=pokemon_name)
    if len(pokemon_matches) == 0:
        pokemon_matches = PokemonForm.objects.filter(name__iexact=pokemon_name)

    if len(pokemon_matches) > 0:
        pokemon = pokemon_matches[0]
        output = pokemon.name + ': '

        current_game_name = Setting.objects.filter(key='Current Game')[0]

        for stat_sets_list_element in StatSetsListElement.objects.filter(list_id=pokemon.stat_sets):
            stat_set = stat_sets_list_element.element
            if is_game_name_in_game_list(current_game_name.value, stat_set.games):
                output += 'Attack(' + str(stat_set.attack) + ') '
                output += 'Defense(' + str(stat_set.defense) + ') '
                output += 'Speed(' + str(stat_set.speed) + ') '
                break
    else:
        output = '"' + pokemon_name + '" was not found'
    return output

def handle_defence(args):
    output = ''
    pokemon_name = ' '.join(args)
    pokemon_name = correct_pokemon_name(pokemon_name)

    pokemon_matches = Pokemon.objects.filter(name__iexact=pokemon_name)
    if len(pokemon_matches) == 0:
        pokemon_matches = PokemonForm.objects.filter(name__iexact=pokemon_name)

    if pokemon_matches:
        pokemon = pokemon_matches[0]
        output = pokemon.name + ': '

        current_game_name = Setting.objects.filter(key='Current Game')[0]

        for stat_sets_list_element in StatSetsListElement.objects.filter(list_id=pokemon.stat_sets):
            stat_set = stat_sets_list_element.element
            if is_game_name_in_game_list(current_game_name.value, stat_set.games):
                output += 'HP(' + str(stat_set.hp) + ') '
                output += 'Sp. Atk(' + str(stat_set.special_attack) + ') '
                output += 'Sp. Def(' + str(stat_set.special_defense) + ') '
                break
    else:
        output = '"' + pokemon_name + '" was not found'
    return output

def handle_whatis(args):
    output = ''
    move_or_ability_name = ' '.join(args)

    move_name = correct_move_name(move_or_ability_name)
    move_matches = Move.objects.filter(name__iexact=move_name)
    if move_matches:
        output = 'Move: '
        return output + handle_move(args)

    ability_name = correct_ability_name(move_or_ability_name)
    ability_matches = Ability.objects.filter(name__iexact=ability_name)
    if ability_matches:
        output = 'Ability: '
        return output + handle_ability(args)

def handle_does(args):
    output = ''
    pokemon_name = args[0]
    move_name = args[2]

    pokemon_learnset_matches = PokemonLearnsets.objects.filter(name__iexact=pokemon_name)
    if pokemon_learnset_matches:
        pokemon_learnset = pokemon_learnset_matches[0]

        current_game_name = Setting.objects.filter(key='Current Game')[0]

        for learnsets_list_element in LearnsetsListElement.objects.filter(list_id=pokemon_learnset.learnsets):
            learnset = learnsets_list_element.element
            if is_game_name_in_game_list(current_game_name.value, learnset.games):
                for learnset_moves_list_element in LearnsetMovesListElement.objects.filter(list_id=learnset.learnset_moves):
                    learnset_move = learnset_moves_list_element.element
                    if learnset_move.name.lower() == move_name.lower():
                        output = pokemon_name.capitalize() + ' learns ' + learnset_move.name + ' at level ' + str(learnset_move.level)
                break

        if len(output) == 0:
            pokemon_tmset_matches = PokemonTmSets.objects.filter(name__iexact=pokemon_name)
            if pokemon_tmset_matches:
                pokemon_tmset = pokemon_tmset_matches[0]

                for tmsets_list_element in TmSetsListElement.objects.filter(list_id=pokemon_tmset.tm_sets):
                    tm_set = tmsets_list_element.element
                    if is_game_name_in_game_list(current_game_name.value, tm_set.games):
                        for tmset_moves_list_element in TmsetMovesListElement.objects.filter(list_id=tm_set.tmset_moves):
                            tmset_move = tmset_moves_list_element.element
                            if tmset_move.name.lower() == move_name.lower():
                                output = pokemon_name.capitalize() + ' learns ' + tmset_move.name + ' by TM/HM'
                        break
    else:
        output = 'Learnsets for "' + pokemon_name + '" were not found'

    return output

def handle_grassknot(args):
    output = ''
    pokemon_name = ' '.join(args)
    pokemon_name = correct_pokemon_name(pokemon_name)

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
          '!weak': 'Usage: !weak <type>',
          '!resist': 'Usage: !resist <type>',
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
