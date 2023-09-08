"""
The get_games_data module calls the necessary functions to create
and populate the games database with the necessary data.
"""


from constants import platform_ids, API_KEY
from misc_functions import fetch_game_ids_by_platforms, create_games_data_db


game_ids = fetch_game_ids_by_platforms(platform_ids, API_KEY)
create_games_data_db(game_ids)