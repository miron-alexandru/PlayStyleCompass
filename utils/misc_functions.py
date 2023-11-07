"""
The misc_functions module contains misc functions used in different parts
of the application.
"""

import uuid
import sys
import sqlite3
import datetime
from datetime import datetime
import requests
from bs4 import BeautifulSoup

from constants import BASE_URL, headers, API_KEY, game_ids_to_add
from sql_queries import (
    create_table_sql,
    remove_duplicates_sql,
    inserting_sql,
    remove_empty,
    create_reviews_table,
    insert_reviews_sql,
    remove_duplicates_reviews,
)


def fetch_game_ids_by_platforms(platform_ids, api_key):
    """
    Fetches game IDs for multiple platform IDs and returns a set of all fetched game IDs.
    """
    all_game_ids = set()
    current_date = datetime.now().date()
    current_date = datetime(2019, 1, 1).date()

    for platform_id in platform_ids:
        url = f"{BASE_URL}games/?api_key={api_key}&format=json&platforms={platform_id}&filter=original_release_date:|{current_date}&sort=original_release_date:desc&limit=20"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                game_ids = [result["guid"] for result in response.json()["results"]]
                all_game_ids.update(game_ids)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching game IDs for platform {platform_id}: {e}")

    #add_custom_game_ids(all_game_ids, game_ids_to_add)
    return all_game_ids


def add_custom_game_ids(all_game_ids, game_ids_to_add):
    """Add custom game ids's"""
    all_game_ids.update(game_ids_to_add)


def fetch_game_data(game_id):
    """Fetch game data from Giant Bomb's API."""
    url = f"{BASE_URL}game/{game_id}/?api_key={API_KEY}&format=json"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request Exception: {e}")
        raise FetchDataException(f"Failed to fetch game data for game ID {game_id}")
    except ValueError as e:
        print(f"JSON Decoding Error: {e}")
        raise FetchDataException(f"Failed to decode JSON data for game ID {game_id}")


def fetch_game_images(game_id):
    """Fetch images for a game using Giant Bomb's API."""
    url = f"{BASE_URL}images/{game_id}/?api_key={API_KEY}&format=json&limit=15"

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            images = data.get("results", [])

            medium_urls = [
                image["medium_url"] for image in images if "medium_url" in image
            ]

            return ", ".join(medium_urls) if medium_urls else None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching game images for game ID {game_id}: {e}")

    return None


def extract_overview_content(data):
    """Extract overview content from game data."""
    if "description" in data and data["description"]:
        soup = BeautifulSoup(data["description"], "html.parser")

        overview_tag = soup.find("h2", string="Overview")

        if overview_tag:
            overview_content = []

            current_element = overview_tag.find_next_sibling()
            while current_element and current_element.name != "h2":
                if current_element.name == "p":
                    overview_content.append(current_element.get_text())
                current_element = current_element.find_next_sibling()

            overview_text = "\n".join(overview_content)

            return overview_text

    return None


def parse_game_data(game_id):
    """Parse the game data."""
    try:
        game_data = fetch_game_data(game_id)["results"]
    except FetchDataException as e:
        print(f"Fetching data failed: {e}")
        sys.exit()

    game_images = fetch_game_images(game_id)
    reviews_data = process_user_reviews(game_id)

    title = get_title(game_data)
    description = get_description(game_data)
    overview = extract_overview_content(game_data)
    genres = get_genres(game_data)
    platforms = get_platforms(game_data)
    themes = get_themes(game_data)
    image = get_image(game_data)
    release_date = get_release_date(game_data)
    developers = get_developers(game_data)
    similar_games = get_similar_games(game_data)

    return (
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
    )


def get_title(game_data):
    """Get game title."""
    return game_data.get("name", None) if isinstance(game_data, dict) else None


def get_description(game_data):
    """Get game description."""
    return game_data.get("deck", None) if isinstance(game_data, dict) else None


def get_genres(game_data):
    """Get game genres."""
    if not isinstance(game_data, dict):
        return None
    genre_names = [genre["name"] for genre in game_data.get("genres", [])]
    return ", ".join(genre_names) if genre_names else None


def get_platforms(game_data):
    """Get game platforms."""
    if not isinstance(game_data, dict):
        return None
    platform_names = [platform["name"] for platform in game_data["platforms"]]
    return ", ".join(platform_names) if platform_names else None


def get_similar_games(game_data, max_count=5):
    if not isinstance(game_data, dict):
        return None
    similar_games = game_data.get("similar_games")
    if similar_games is not None:
        similar_games = [game["name"] for game in similar_games]

        if max_count:
            similar_games = similar_games[:max_count]

        return ", ".join(similar_games) if similar_games else None
    return None


def get_themes(game_data):
    """Get game platforms."""
    if not isinstance(game_data, dict):
        return None
    theme_names = [theme["name"] for theme in game_data.get("themes", [])]
    return ", ".join(theme_names) if theme_names else None


def get_image(game_data):
    """Get game image."""
    if not isinstance(game_data, dict):
        return None
    image_url = game_data["image"].get("small_url", None)
    return (
        "https://i.ibb.co/HnJFgmy/default-psc.jpg"
        if image_url and "default" in image_url
        else image_url
    )


def get_release_date(game_data):
    """Get game release date."""
    if isinstance(game_data, dict):
        release_date = (
            game_data["original_release_date"]
            if game_data["original_release_date"] is not None
            else game_data["expected_release_year"]
        )
        return release_date
    else:
        return None


def get_developers(game_data):
    """Get game devs."""
    if not isinstance(game_data, dict):
        return None
    if "developers" not in game_data or not isinstance(game_data["developers"], list):
        return None
    developer_names = [developer["name"] for developer in game_data["developers"]]
    return ", ".join(developer_names) if developer_names else None


def fetch_user_reviews(game_id):
    """Fetch all user reviews for a game."""
    game_id = game_id.split("3030-")[-1]
    url = f"{BASE_URL}user_reviews/?api_key={API_KEY}&game={game_id}&format=json"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if "results" in data and data["number_of_total_results"] < 100:
            return data
    return None


def extract_description_text(html_description):
    """Extract description text from review."""
    soup = BeautifulSoup(html_description, "html.parser")
    text = soup.get_text()
    return text


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


def create_games_data_db(game_ids):
    """Inserts game data and reviews data into the database using the provided game IDs."""
    with sqlite3.connect("games_data.db") as db_connection:
        cursor = db_connection.cursor()
        cursor.execute(create_table_sql)
        cursor.execute(create_reviews_table)
        db_connection.commit()

        for game_id in game_ids:
            (
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
            ) = parse_game_data(game_id)

            game_values = (
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
            )
            cursor.execute(inserting_sql, game_values)

            game_id = cursor.lastrowid

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


class FetchDataException(Exception):
    """Custom data exception."""

    pass
