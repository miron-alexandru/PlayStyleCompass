"""
The misc_functions module contains misc functions used in different parts
of the application.
"""

from constants import BASE_URL, headers, API_KEY

import requests
import json
import sqlite3
from datetime import datetime


def fetch_game_ids_by_platforms(platform_ids, api_key):
    """
    Fetches game IDs for multiple platform IDs and returns a set of all fetched game IDs.
    """
    all_game_ids = set()

    current_date = datetime.now().date()

    for platform_id in platform_ids:
        url = f'{BASE_URL}games/?api_key={api_key}&format=json&platforms={platform_id}&sort=original_release_date:desc&limit=100'
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            results = response.json()['results']
            game_ids = [result['id'] for result in results if not result.get('original_release_date') or datetime.strptime(result['original_release_date'], '%Y-%m-%d').date() <= current_date]
            all_game_ids.update(game_ids)

    return all_game_ids

def fetch_game_data(game_id):
    """Fetch game data from Giant Bomb API"""
    url = f'{BASE_URL}game/{game_id}/?api_key={API_KEY}&format=json'
    response = requests.get(url, headers=headers)
    return response.json()

def parse_game_data(game_id):
    """Parses the game data fetched using the provided game ID and extracts relevant information."""
    game_data = fetch_game_data(game_id)['results']
    
    title = game_data['name']
    description = game_data['deck']
    
    genre_names = [genre['name'] for genre in game_data.get('genres', [])]
    genres = ", ".join(genre_names) if genre_names else None
    
    platform_names = [platform['name'] for platform in game_data['platforms']]
    platforms = ", ".join(platform_names)
    
    theme_names = [theme['name'] for theme in game_data.get('themes', [])]
    themes = ", ".join(theme_names) if theme_names else None
    
    image_url = game_data['image'].get('small_url', None)
    image = 'https://i.ibb.co/HnJFgmy/default-psc.jpg' if image_url and 'default' in image_url else image_url
    
    release_date = game_data['original_release_date']

    return title, description, genres, platforms, themes, image, release_date


def create_games_data_db(game_ids):
    """Inserts game data into a SQLite database using the provided game IDs."""
    with sqlite3.connect('games_data.db') as db_connection:
        cursor = db_connection.cursor()

        create_table_sql = '''
        CREATE TABLE IF NOT EXISTS Games (
            id INTEGER PRIMARY KEY,
            title TEXT,
            description TEXT,
            genres TEXT,  
            platforms TEXT,
            themes TEXT,
            image TEXT,
            release_date TEXT
        );
        '''
        cursor.execute(create_table_sql)
        db_connection.commit()

        for game_id in game_ids:
            title, description, genres, platforms, themes, image, release_date = parse_game_data(game_id)
            
            sql = "INSERT INTO Games (title, description, genres, platforms, themes, image, release_date) VALUES (?, ?, ?, ?, ?, ?, ?)"
            values = (title, description, genres, platforms, themes, image, release_date)
            cursor.execute(sql, values)
            db_connection.commit()

        # Remove duplicates based on the title
        remove_duplicates_sql = '''
        DELETE FROM Games
        WHERE rowid NOT IN (
            SELECT MIN(rowid)
            FROM Games
            GROUP BY title
        );
        '''
        cursor.execute(remove_duplicates_sql)
        db_connection.commit()
