import math

from django.core.cache import cache
from spellchecker import SpellChecker

from dashboard.models import Setting
from westwood.models import *

def is_game_name_in_game_list(current_game_name, game_list_id, check_base_game=True):
    games_list_element_objects = GamesListElement.objects.filter(list_id=game_list_id)
    for games_list_element in games_list_element_objects:
        game = games_list_element.element
        if game.name == current_game_name:
            return True

    if check_base_game:
        # Check if any ROM hack base games match
        rom_hack_matches = RomHack.objects.filter(title__iexact=current_game_name)
        if len(rom_hack_matches) > 0:
            base_game = rom_hack_matches[0].base_game
            for games_list_element in games_list_element_objects:
                game = games_list_element.element
                if game.name == base_game:
                    return True

    return False

def get_modified_stats(current_game_name, rom_hack_stat_set, pokemon_stat_sets_id):
    modified_stats = {'hp': '', 'attack': '', 'defense': '', 'special_attack': '', 'special_defense': '', 'speed': ''}

    # Check if the current game is a ROM hack
    rom_hack_matches = RomHack.objects.filter(title__iexact=current_game_name)
    if len(rom_hack_matches) > 0:
        base_game = rom_hack_matches[0].base_game

        # Find the stat set for the base game so we can compare
        for stat_sets_list_element in StatSetsListElement.objects.filter(list_id=pokemon_stat_sets_id):
            base_game_stat_set = stat_sets_list_element.element
            if is_game_name_in_game_list(base_game, base_game_stat_set.games):
                # Found the base game
                if rom_hack_stat_set.hp < base_game_stat_set.hp:
                    modified_stats['hp'] = '-'
                elif rom_hack_stat_set.hp > base_game_stat_set.hp:
                    modified_stats['hp'] = '+'

                if rom_hack_stat_set.attack < base_game_stat_set.attack:
                    modified_stats['attack'] = '-'
                elif rom_hack_stat_set.attack > base_game_stat_set.attack:
                    modified_stats['attack'] = '+'

                if rom_hack_stat_set.defense < base_game_stat_set.defense:
                    modified_stats['defense'] = '-'
                elif rom_hack_stat_set.defense > base_game_stat_set.defense:
                    modified_stats['defense'] = '+'

                if rom_hack_stat_set.special_attack < base_game_stat_set.special_attack:
                    modified_stats['special_attack'] = '-'
                elif rom_hack_stat_set.special_attack > base_game_stat_set.special_attack:
                    modified_stats['special_attack'] = '+'

                if rom_hack_stat_set.special_defense < base_game_stat_set.special_defense:
                    modified_stats['special_defense'] = '-'
                elif rom_hack_stat_set.special_defense > base_game_stat_set.special_defense:
                    modified_stats['special_defense'] = '+'

                if rom_hack_stat_set.speed < base_game_stat_set.speed:
                    modified_stats['speed'] = '-'
                elif rom_hack_stat_set.speed > base_game_stat_set.speed:
                    modified_stats['speed'] = '+'

                break

    return modified_stats

def get_modified_move_details(current_game_name, rom_hack_move_definition, move_records_id):
    modified_move_details = {'type': '', 'base_power': '', 'damage_category': '', 'accuracy': '', 'power_points': '', 'priority': ''}

    # Check if the current game is a ROM hack
    rom_hack_matches = RomHack.objects.filter(title__iexact=current_game_name)
    if len(rom_hack_matches) > 0:
        base_game = rom_hack_matches[0].base_game

        # Find the move record for the base game so we can compare
        for move_records_list_element in MoveRecordsListElement.objects.filter(list_id=move_records_id):
            base_game_move_record = move_records_list_element.element
            if is_game_name_in_game_list(base_game, base_game_move_record.games):
                # Found the base game
                base_game_move_definition = base_game_move_record.move_definition
                if rom_hack_move_definition.type_1 != base_game_move_definition.type_1:
                    modified_move_details['type'] = '*'

                if rom_hack_move_definition.base_power < base_game_move_definition.base_power:
                    modified_move_details['base_power'] = '-'
                elif rom_hack_move_definition.base_power > base_game_move_definition.base_power:
                    modified_move_details['base_power'] = '+'

                if rom_hack_move_definition.damage_category != base_game_move_definition.damage_category:
                    modified_move_details['damage_category'] = '*'

                if rom_hack_move_definition.accuracy < base_game_move_definition.accuracy:
                    modified_move_details['accuracy'] = '-'
                elif rom_hack_move_definition.accuracy > base_game_move_definition.accuracy:
                    modified_move_details['accuracy'] = '+'

                if rom_hack_move_definition.power_points < base_game_move_definition.power_points:
                    modified_move_details['power_points'] = '-'
                elif rom_hack_move_definition.power_points > base_game_move_definition.power_points:
                    modified_move_details['power_points'] = '+'

                if rom_hack_move_definition.priority < base_game_move_definition.priority:
                    modified_move_details['priority'] = '-'
                elif rom_hack_move_definition.priority > base_game_move_definition.priority:
                    modified_move_details['priority'] = '+'

                break

    return modified_move_details

def correct_pokemon_name(name_to_correct):
    pokemon_corrector = cache.get('pokemon_corrector')
    if None == pokemon_corrector:
        pokemon_list = [pokemon.name for pokemon in Pokemon.objects.all()]
        pokemon_form_list = [pokemon_form.name for pokemon_form in PokemonForm.objects.all()]
        combined_list = pokemon_list + pokemon_form_list
        pokemon_corrector = SpellChecker(language=None, case_sensitive=False)
        pokemon_corrector.word_frequency.load_words(combined_list)
        cache.set('pokemon_corrector', pokemon_corrector, timeout=None)

    correction = pokemon_corrector.correction(name_to_correct)
    return correction if len(correction) > 0 else name_to_correct

def correct_move_name(name_to_correct):
    move_corrector = cache.get('move_corrector')
    if None == move_corrector:
        move_list = [move.name for move in Move.objects.all()]
        move_corrector = SpellChecker(language=None, case_sensitive=False)
        move_corrector.word_frequency.load_words(move_list)
        cache.set('move_corrector', move_corrector, timeout=None)

    correction = move_corrector.correction(name_to_correct)
    return correction if len(correction) > 0 else name_to_correct

def correct_ability_name(name_to_correct):
    ability_corrector = cache.get('ability_corrector')
    if None == ability_corrector:
        ability_list = [ability.name for ability in Ability.objects.all()]
        ability_corrector = SpellChecker(language=None, case_sensitive=False)
        ability_corrector.word_frequency.load_words(ability_list)
        cache.set('ability_corrector', ability_corrector, timeout=None)

    correction = ability_corrector.correction(name_to_correct)
    return correction if len(correction) > 0 else name_to_correct

def pokemon_not_present(pokemon_name):
    pokemon_matches = Pokemon.objects.filter(name__iexact=pokemon_name)
    if len(pokemon_matches) == 0:
        pokemon_matches = PokemonForm.objects.filter(name__iexact=pokemon_name)

    if len(pokemon_matches) > 0:
        pokemon = pokemon_matches[0]

        current_game_name = Setting.objects.get(key='Current Game')

        for type_sets_list_element in TypeSetsListElement.objects.filter(list_id=pokemon.type_sets):
            type_set = type_sets_list_element.element
            if is_game_name_in_game_list(current_game_name.value, type_set.games, check_base_game=True):
                return False
    return True

def move_not_present(move_name):
    move_matches = Move.objects.filter(name__iexact=move_name)

    if len(move_matches) > 0:
        move = move_matches[0]

        current_game_name = Setting.objects.get(key='Current Game')

        for move_records_list_element in MoveRecordsListElement.objects.filter(list_id=move.move_records):
            move_record = move_records_list_element.element
            if is_game_name_in_game_list(current_game_name.value, move_record.games, check_base_game=True):
                return False
    return True

def get_types_for_pokemon(pokemon_name):
    type1 = ''
    type2 = ''
    current_game_name = Setting.objects.filter(key='Current Game')[0]

    pokemon_matches = Pokemon.objects.filter(name__iexact=pokemon_name)
    if len(pokemon_matches) == 0:
        pokemon_matches = PokemonForm.objects.filter(name__iexact=pokemon_name)

    if len(pokemon_matches) > 0:
        pokemon = pokemon_matches[0]

        try_again = True
        check_base_game = False
        while try_again:
            for type_sets_list_element in TypeSetsListElement.objects.filter(list_id=pokemon.type_sets):
                type_set = type_sets_list_element.element
                if is_game_name_in_game_list(current_game_name.value, type_set.games, check_base_game=check_base_game):
                    type1 = type_set.type1
                    if len(type_set.type2) > 0:
                        type2 = type_set.type2
                    try_again = False
                    break
            if try_again:
                check_base_game = True

    return type1, type2

def get_type_advantages_for_type_pair(type1, type2):
    current_game_name = Setting.objects.filter(key='Current Game')[0]

    weaknesses = []
    resistances = []
    no_damage = []

    for effectiveness_sets_list_element in EffectivenessSetsListElement.objects.all():
        effectiveness_set = effectiveness_sets_list_element.element
        if is_game_name_in_game_list(current_game_name.value, effectiveness_set.games):
            for effectiveness_records_list_element in EffectivenessRecordsListElement.objects.filter(list_id=effectiveness_set.effectiveness_records):
                effectiveness_record = effectiveness_records_list_element.element

                if effectiveness_record.target_type.lower() == type1.lower() or effectiveness_record.target_type.lower() == type2.lower():
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

    #print(weaknesses)
    #print(resistances)
    #print(no_damage)

    return weaknesses, resistances, no_damage

def is_type(possible_type):
    type_objects = Type.objects.filter(value__iexact=possible_type)
    return len(type_objects) > 0

def calculate_stat(base_stat, level=100, ev=0.0, iv=31.0, hindered=False, beneficial=False, choice_item=False):
    base_stat = base_stat * 1.0
    nature = 1.0
    if hindered:
        nature = 0.9
    if beneficial:
        nature = 1.1
    stat = math.floor((math.floor((((2 * base_stat) + iv + math.floor(ev / 4)) * level) / 100) + 5) * nature)
    if choice_item:
        stat = math.floor(stat * 1.5)
    return stat

def calculate_hp(base_hp, level=100, ev=0.0, iv=31.0):
    base_hp = base_hp * 1.0
    hp_stat = math.floor((((2 * base_hp) + iv + math.floor(ev / 4)) * level) / 100) + level + 10
    return hp_stat
