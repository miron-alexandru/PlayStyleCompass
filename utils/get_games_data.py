"""
The get_games_data module calls the necessary functions to create
and populate the games database with the necessary data.
"""

from API_functions import fetch_game_ids_by_platforms, fetch_data
from data_extraction import extract_guids, extract_character_guids

from constants import (
    platform_ids,
    API_KEY,
    franchises_ids_to_add,
    game_ids_to_add,
    concept_ids,
)

from data_processing import (
    create_games_data_db,
    create_franchises_data,
    create_characters_data,
    create_game_modes_data,
    create_quiz_data,
)

# Obtain franchises data
# franchises = fetch_data(API_KEY, resource_type="franchises", offset=200, limit=50)
# franchises_ids = extract_guids(franchises, franchises_ids_to_add)
# create_franchises_data(franchises_ids)

# Obtain characters data
# characters = fetch_data(API_KEY, resource_type="characters", offset=300, limit=50)
# characters_ids = extract_character_guids(characters)
# create_characters_data(characters_ids)

# Obtain games data
game_ids = fetch_game_ids_by_platforms(platform_ids, API_KEY, offset=20, limit=1)
create_games_data_db(game_ids)

# Obtain game modes data
# guids = ["3015-6130", "3015-322"]
# mode_strings = ["Singleplayer", "Multiplayer"]
# create_game_modes_data(guids, mode_strings, num_games=10, offset=10)

# Obtain games based on concepts (used for preference quiz)
# create_quiz_data(concept_ids, num_games=2, offset=12)
