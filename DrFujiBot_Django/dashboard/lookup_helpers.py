from westwood.models import Game, GamesListElement

def is_game_name_in_game_list(current_game_name, game_list_id):
    games_list_element_objects = GamesListElement.objects.filter(list_id=game_list_id)
    for games_list_element in games_list_element_objects:
        game = games_list_element.element
        if game.name == current_game_name:
            return True
    return False
