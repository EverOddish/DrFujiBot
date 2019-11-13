from django.core.cache import cache
from spellchecker import SpellChecker

from dashboard.models import Setting
from westwood.models import Ability, Game, GamesListElement, Move, Pokemon, PokemonForm, RomHack, StatSetsListElement, MoveRecordsListElement, TypeSetsListElement

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
