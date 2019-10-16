from django.core.cache import cache
from spellchecker import SpellChecker

from westwood.models import Ability, Game, GamesListElement, Move, Pokemon, PokemonForm

def is_game_name_in_game_list(current_game_name, game_list_id):
    games_list_element_objects = GamesListElement.objects.filter(list_id=game_list_id)
    for games_list_element in games_list_element_objects:
        game = games_list_element.element
        if game.name == current_game_name:
            return True
    return False

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
