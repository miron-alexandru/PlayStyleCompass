"""The "data_processing" module contains functions for parsing and creating/managing the database. """


import uuid
import sys
import sqlite3

from constants import API_KEY

from API_functions import (
    fetch_game_data,
    fetch_object_images,
    fetch_user_reviews,
    fetch_data_by_guid,
    search_gameplay_videos,
    FetchDataException,
)

from data_extraction import (
    extract_overview_content,
    get_embed_links,
    extract_data,
    extract_names,
    get_franchises,
    get_similar_games,
    get_dlcs,
    get_image,
    get_release_date,
    get_developers,
    extract_first_game,
    extract_description_text,
    get_franchise_games,
    get_franchise_games_count,
    extract_game_data,
    )

from sql_queries import (
    create_table_sql,
    remove_duplicates_sql,
    inserting_sql,
    remove_empty,
    create_reviews_table,
    insert_reviews_sql,
    remove_duplicates_reviews,
    create_franchises_table,
    insert_franchise_sql,
    remove_duplicate_franchises,
    create_characters_table,
    insert_characters_sql,
    remove_duplicate_characters,
    create_game_modes_table,
    insert_game_modes_sql,
    remove_duplicate_game_modes,
)



def parse_game_data(game_id, youtube_api_client):
    """Parse the game data."""
    try:
        game_data = fetch_game_data(game_id)["results"]
    except FetchDataException as e:
        print(f"Fetching data failed: {e}")
        sys.exit()

    game_images = fetch_object_images(game_id)
    reviews_data = process_user_reviews(game_id)

    guid = extract_data(game_data, "id")
    title = extract_data(game_data, "name")
    gameplay_video_ids = search_gameplay_videos(title, youtube_api_client)
    description = extract_data(game_data, "deck")
    overview = extract_overview_content(game_data)
    genres = extract_names(game_data, "genres")
    platforms = extract_names(game_data, "platforms")
    themes = extract_names(game_data, "themes")
    image = get_image(game_data)
    release_date = get_release_date(game_data)
    developers = get_developers(game_data)
    similar_games = get_similar_games(game_data)
    dlcs = get_dlcs(game_data)
    franchises = get_franchises(game_data)
    videos = get_embed_links(gameplay_video_ids)

    return (
        guid,
        title,
        description,
        overview,
        genres,
        platforms,
        themes,
        image,
        release_date,
        developers,
        game_images,
        similar_games,
        reviews_data,
        dlcs,
        franchises,
        videos,
    )


def process_user_reviews(game_id):
    """Process user reviews."""
    user_reviews_data = fetch_user_reviews(game_id)
    if user_reviews_data:
        reviews = []
        for review in user_reviews_data["results"]:
            reviewer = review["reviewer"]
            deck = review["deck"]
            description_text = review["description"]
            score = review["score"]
            description = extract_description_text(description_text)
            reviews.append(
                {
                    "reviewer": reviewer,
                    "deck": deck,
                    "description": description,
                    "score": score,
                }
            )

        return reviews
    else:
        return None


def create_games_data_db(game_ids, youtube_api_client):
    """Inserts game data and reviews data into the database using the provided game IDs."""
    with sqlite3.connect("games_data.db") as db_connection:
        cursor = db_connection.cursor()
        cursor.execute(create_table_sql)
        cursor.execute(create_reviews_table)
        db_connection.commit()

        for game_id in game_ids:
            (
                guid,
                title,
                description,
                overview,
                genres,
                platforms,
                themes,
                image,
                release_date,
                developers,
                game_images,
                similar_games,
                reviews_data,
                dlcs,
                franchises,
                videos,
            ) = parse_game_data(game_id, youtube_api_client)

            game_values = (
                guid,
                title,
                description,
                overview,
                genres,
                platforms,
                themes,
                image,
                release_date,
                developers,
                game_images,
                similar_games,
                dlcs,
                franchises,
                videos,
            )
            cursor.execute(inserting_sql, game_values)

            game_id = guid

            if reviews_data:
                for review in reviews_data:
                    reviewers = review["reviewer"]
                    review_deck = review["deck"]
                    review_description = review["description"]
                    score = str(review["score"])

                    user_id = str(uuid.uuid4())

                    review_values = (
                        reviewers,
                        review_deck,
                        review_description,
                        score,
                        user_id,
                        game_id,
                    )
                    cursor.execute(insert_reviews_sql, review_values)

            db_connection.commit()

        cursor.execute(remove_duplicates_sql)
        cursor.execute(remove_duplicates_reviews)
        cursor.execute(remove_empty)
        db_connection.commit()


def parse_franchise_data(franchise_id):
    """Parse franchise data."""
    try:
        franchise_data = fetch_data_by_guid(
            franchise_id,
            API_KEY,
            resource_type="franchise",
            format="json",
            field_list=["name", "deck", "description", "games", "image"],
        )
    except FetchDataException as e:
        print(f"Fetching data failed: {e}")
        sys.exit()

    description = extract_overview_content(franchise_data)
    title = extract_data(franchise_data, "name")
    overview = extract_data(franchise_data, "deck")
    games = get_franchise_games(franchise_data)
    image = get_image(franchise_data)
    images = fetch_object_images(franchise_id)
    games_count = get_franchise_games_count(games)

    return (
        title,
        overview,
        description,
        games,
        image,
        images,
        games_count,
    )


def create_franchises_data(franchises_ids):
    """Insert the data for each franchise in the database."""
    with sqlite3.connect("games_data.db") as db_connection:
        cursor = db_connection.cursor()
        cursor.execute(create_franchises_table)
        db_connection.commit()

        for franchise_id in franchises_ids:
            (
                title,
                overview,
                description,
                games,
                image,
                images,
                games_count,
            ) = parse_franchise_data(franchise_id)

            franchise_values = (
                title,
                overview,
                description,
                games,
                image,
                images,
                games_count,
            )
            cursor.execute(insert_franchise_sql, franchise_values)

            db_connection.commit()

        cursor.execute(remove_duplicate_franchises)

        db_connection.commit()


def parse_character_data(character_id):
    """Parse character data."""
    try:
        character_data = fetch_data_by_guid(
            character_id,
            API_KEY,
            resource_type="character",
            format="json",
            field_list=[
                "name",
                "deck",
                "description",
                "birthday",
                "friends",
                "enemies",
                "games",
                "franchises",
                "image",
                "images",
                "first_appeared_in_game",
                "id",
            ],
        )
    except FetchDataException as e:
        print(f"Fetching data failed: {e}")
        sys.exit()

    name = extract_data(character_data, "name")
    deck = extract_data(character_data, "deck")
    description = extract_overview_content(character_data)
    birthday = extract_data(character_data, "birthday")
    friends = extract_names(character_data, "friends")
    enemies = extract_names(character_data, "enemies")
    games = extract_names(character_data, "games")
    first_game = extract_first_game(character_data)
    franchises = extract_names(character_data, "franchises")
    image = get_image(character_data)
    images = fetch_object_images(character_id)
    character_id = character_data.get("id", None)

    return (
        name,
        deck,
        description,
        birthday,
        friends,
        enemies,
        games,
        first_game,
        franchises,
        image,
        images,
        character_id,
    )


def create_characters_data(characters_ids):
    """Insert the data for each franchise in the database."""
    with sqlite3.connect("games_data.db") as db_connection:
        cursor = db_connection.cursor()
        cursor.execute(create_characters_table)
        db_connection.commit()

        for character_id in characters_ids:
            (
                name,
                deck,
                description,
                birthday,
                friends,
                enemies,
                games,
                first_game,
                franchises,
                image,
                images,
                character_id,
            ) = parse_character_data(character_id)

            character_values = (
                name,
                deck,
                description,
                birthday,
                friends,
                enemies,
                games,
                first_game,
                franchises,
                image,
                images,
                character_id,
            )
            cursor.execute(insert_characters_sql, character_values)

            db_connection.commit()

        cursor.execute(remove_duplicate_characters)

        db_connection.commit()

def parse_game_modes_data(game, game_mode):
    """Parse game modes data."""

    game_id = extract_game_data(game, "id")
    game_name = extract_game_data(game, "name")

    return (
        game_id,
        game_name,
        game_mode
    )

def create_game_modes_data(guids, mode_strings, youtube_api_client=None):
    """Insert game modes data into the database."""
    with sqlite3.connect("games_data.db") as db_connection:
        cursor = db_connection.cursor()
        cursor.execute(create_game_modes_table)
        db_connection.commit()

        for guid, mode_string in zip(guids, mode_strings):
            game_modes_data = fetch_data_by_guid(guid, API_KEY, 'concept', field_list=["games"])

            for game in game_modes_data['games']:
                (
                    game_id,
                    game_name,
                    game_mode,
                ) = parse_game_modes_data(game, mode_string)

                game_mode_values = (
                    game_id,
                    game_name,
                    game_mode,
                )
                cursor.execute(insert_game_modes_sql, game_mode_values)

                db_connection.commit()

            game_ids = []

            for game in game_modes_data['games']:
                game_id = extract_game_data(game, "id")
                game_ids.append("3030-" + str(game_id))

            for game_id in game_ids[:10]:
                (
                    guid,
                    title,
                    description,
                    overview,
                    genres,
                    platforms,
                    themes,
                    image,
                    release_date,
                    developers,
                    game_images,
                    similar_games,
                    reviews_data,
                    dlcs,
                    franchises,
                    videos,
                ) = parse_game_data(game_id, youtube_api_client)

                game_values = (
                    guid,
                    title,
                    description,
                    overview,
                    genres,
                    platforms,
                    themes,
                    image,
                    release_date,
                    developers,
                    game_images,
                    similar_games,
                    dlcs,
                    franchises,
                    videos,
                )
                cursor.execute(inserting_sql, game_values)

                game_id = guid

                if reviews_data:
                    for review in reviews_data:
                        reviewers = review["reviewer"]
                        review_deck = review["deck"]
                        review_description = review["description"]
                        score = str(review["score"])

                        user_id = str(uuid.uuid4())

                        review_values = (
                            reviewers,
                            review_deck,
                            review_description,
                            score,
                            user_id,
                            game_id,
                        )
                        cursor.execute(insert_reviews_sql, review_values)

                db_connection.commit()

            cursor.execute(remove_duplicates_sql)
            cursor.execute(remove_duplicates_reviews)

            db_connection.commit()

        cursor.execute(remove_duplicate_game_modes)

        db_connection.commit()
