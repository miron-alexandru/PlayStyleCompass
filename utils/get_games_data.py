"""
The get_games_data module calls the necessary functions to create
and populate the games database with the necessary data.
"""

import googleapiclient.discovery
from constants import (
    platform_ids,
    API_KEY,
    franchises_ids_to_add,
    game_ids_to_add,
    GOOGLE_API_KEY,
)
from misc_functions import (
    fetch_game_ids_by_platforms,
    create_games_data_db,
    create_franchises_data,
    fetch_data,
    extract_guids,
    extract_character_guids,
    create_characters_data,
)

# Create Franchises
# franchises = fetch_data(API_KEY, resource_type="franchises", offset=150, limit=50)
# franchises_ids = extract_guids(franchises, franchises_ids_to_add)
# create_franchises_data(franchises_ids)

# characters = fetch_data(API_KEY, resource_type="characters", offset=200, limit=100)
# characters_ids = extract_character_guids(characters)
# create_characters_data(characters_ids)

# Create Games
youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=GOOGLE_API_KEY)
game_ids = fetch_game_ids_by_platforms(platform_ids, API_KEY, offset=15, limit=5)
create_games_data_db(game_ids, youtube)
