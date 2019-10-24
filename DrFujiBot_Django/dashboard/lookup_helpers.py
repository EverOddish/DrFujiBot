from django.core.cache import cache
from spellchecker import SpellChecker

from westwood.models import Ability, Game, GamesListElement, Move, Pokemon, PokemonForm, RomHack, StatSetsListElement

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
