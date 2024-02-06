"""
The get_games_data module calls the necessary functions to create
and populate the games database with the necessary data.
"""


from constants import platform_ids, API_KEY
from misc_functions import (
    fetch_game_ids_by_platforms,
    create_games_data_db,
    create_franchises_data,
    fetch_franchises,
    extract_guids,
)

# Create Franchises
#franchises = fetch_franchises(API_KEY, offset=270, limit=50)
#franchises_ids = extract_guids(franchises)
#create_franchises_data(franchises_ids)

# Create Games
game_ids = fetch_game_ids_by_platforms(platform_ids, API_KEY, offset=40, limit=5)
create_games_data_db(game_ids)
