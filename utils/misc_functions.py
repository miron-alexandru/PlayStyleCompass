"""
The misc_functions module contains misc functions used in different parts
of the application.
"""

from constants import BASE_URL, headers, API_KEY
from sql_queries import create_table_sql, remove_duplicates_sql

import requests
import json
import sqlite3
from datetime import datetime
from bs4 import BeautifulSoup


def fetch_game_ids_by_platforms(platform_ids, api_key):
    """
    Fetches game IDs for multiple platform IDs and returns a set of all fetched game IDs.
    """
    all_game_ids = set()

    current_date = datetime.now().date()

    for platform_id in platform_ids:
        url = f'{BASE_URL}games/?api_key={api_key}&format=json&platforms={platform_id}&filter=original_release_date:|{current_date}&sort=original_release_date:desc&limit=5'
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            game_ids = [result['guid'] for result in response.json()['results']]
            all_game_ids.update(game_ids)

    return all_game_ids


def fetch_game_data(game_id):
    """Fetch game data from Giant Bomb's API."""
    url = f'{BASE_URL}game/{game_id}/?api_key={API_KEY}&format=json'
    response = requests.get(url, headers=headers)
    return response.json()

def fetch_game_images(game_id):
    """Fetch images for a game using Giant Bomb's API."""
    url = f'{BASE_URL}images/{game_id}/?api_key={API_KEY}&format=json&limit=15'

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        images = data.get("results", [])

        medium_urls = [image["medium_url"] for image in images if "medium_url" in image]
        
        return ", ".join(medium_urls) if medium_urls else None

    return None

def extract_overview_content(data):
    """Extract overview content from game data."""
    if 'description' in data and data['description']:
        soup = BeautifulSoup(data['description'], 'html.parser')

        overview_tag = soup.find('h2', string='Overview')
        
        if overview_tag:
            overview_content = []

            current_element = overview_tag.find_next_sibling()
            while current_element and current_element.name != 'h2':
                if current_element.name == 'p':
                    overview_content.append(current_element.get_text())
                current_element = current_element.find_next_sibling()

            overview_text = '\n'.join(overview_content)

            return overview_text
    
    return None

def parse_game_data(game_id):
    game_data = fetch_game_data(game_id)['results']
    game_images = fetch_game_images(game_id)

    title = get_title(game_data)
    description = get_description(game_data)
    overview = extract_overview_content(game_data)
    genres = get_genres(game_data)
    platforms = get_platforms(game_data)
    themes = get_themes(game_data)
    image = get_image(game_data)
    release_date = get_release_date(game_data)
    developers = get_developers(game_data)

    return title, description, overview, genres, platforms, themes, image, release_date, developers, game_images

def get_title(game_data):
    return game_data.get('name', None)

def get_description(game_data):
    return game_data.get('deck', None)

def get_genres(game_data):
    genre_names = [genre['name'] for genre in game_data.get('genres', [])]
    return ", ".join(genre_names) if genre_names else None

def get_platforms(game_data):
    platform_names = [platform['name'] for platform in game_data['platforms']]
    return ", ".join(platform_names) if platform_names else None

def get_themes(game_data):
    theme_names = [theme['name'] for theme in game_data.get('themes', [])]
    return ", ".join(theme_names) if theme_names else None

def get_image(game_data):
    image_url = game_data['image'].get('small_url', None)
    return 'https://i.ibb.co/HnJFgmy/default-psc.jpg' if image_url and 'default' in image_url else image_url

def get_release_date(game_data):
    release_date = game_data['original_release_date'] if game_data['original_release_date'] is not None else game_data['expected_release_year']
    return release_date

def get_developers(game_data):
    if 'developers' in game_data and isinstance(game_data['developers'], list):
        developer_names = [developer['name'] for developer in game_data['developers']]
        return ", ".join(developer_names) if developer_names else None
    else:
        return None

def create_games_data_db(game_ids):
    """Inserts game data into a SQLite database using the provided game IDs."""
    with sqlite3.connect('games_data.db') as db_connection:
        cursor = db_connection.cursor()
        cursor.execute(create_table_sql)
        db_connection.commit()

        for game_id in game_ids:
            title, description, overview, genres, platforms, themes, image, release_date, developers, game_images = parse_game_data(game_id)
            
            sql = "INSERT INTO Games (title, description, overview, genres, platforms, themes, image, release_date, developers, game_images) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            values = (title, description, overview, genres, platforms, themes, image, release_date, developers, game_images)
            cursor.execute(sql, values)
            db_connection.commit()

        cursor.execute(remove_duplicates_sql)
        db_connection.commit()
