"""The "API_functions" module provides functions for making API calls and fetching data."""

import os
import re
from roman import fromRoman, toRoman, InvalidRomanNumeralError
import datetime
import difflib
from datetime import datetime, timedelta
import requests
from youtubesearchpython import VideosSearch

from constants import BASE_URL, headers, API_KEY, GAMESPOT_API_KEY, RAWG_API_KEY
from data_extraction import get_requirements

steam_app_list = None
steam_app_dict = None


def fetch_game_ids_by_platforms(
    platform_ids, api_key, offset=0, limit=10, game_ids_to_add=None
):
    """
    Fetches game IDs for multiple platform IDs and returns a set of all fetched game IDs.
    """
    all_game_ids = set()

    if game_ids_to_add:
        all_game_ids.update(game_ids_to_add)

    current_date = datetime.now().date()
    # current_date = datetime(2023, 1, 1).date()

    for platform_id in platform_ids:
        url = (
            f"{BASE_URL}games/"
            f"?api_key={api_key}&format=json&platforms={platform_id}"
            f"&filter=original_release_date:|{current_date}&sort=original_release_date:desc"
            f"&limit={limit}&offset={offset}"
        )
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                game_ids = [result["guid"] for result in response.json()["results"]]
                all_game_ids.update(game_ids)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching game IDs for platform {platform_id}: {e}")

    return all_game_ids


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


def fetch_object_images(object_id):
    """Fetch images for an object using Giant Bomb's API."""
    url = f"{BASE_URL}images/{object_id}/?api_key={API_KEY}&format=json&limit=15"

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
        print(f"Error fetching images for ID {object_id}: {e}")

    return None


def fetch_user_reviews(game_id):
    """Fetch all user reviews for a game."""
    game_id = game_id.split("3030-")[-1]
    url = f"{BASE_URL}user_reviews/?api_key={API_KEY}&game={game_id}&format=json"
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json()
        if "results" in data and data["number_of_total_results"] < 100:
            return data
    return None


def fetch_data(
    api_key, resource_type, offset=0, format="json", field_list=None, limit=1
):
    """Fetch data using the Giant Bomb's API."""
    base_url = f"https://www.giantbomb.com/api/{resource_type}/"
    api_url = f"{base_url}?api_key={api_key}&format={format}&offset={offset}"

    if field_list:
        api_url += f'&field_list={",".join(field_list)}'
    api_url += f"&limit={limit}"

    response = requests.get(api_url, headers=headers, timeout=10)

    if response.status_code == 200:
        data = response.json()
        return data.get("results", [])
    else:
        print(f"Error: {response.status_code}")
        return None


def fetch_data_by_guid(guid, api_key, resource_type, format="json", field_list=None):
    """Fetch data for an individual resource (character or franchise)."""
    base_url = f"https://www.giantbomb.com/api/{resource_type}"
    api_url = f"{base_url}/{guid}?api_key={api_key}&format={format}"

    if field_list:
        api_url += f'&field_list={",".join(field_list)}'

    response = requests.get(api_url, headers=headers, timeout=10)

    if response.status_code == 200:
        data = response.json()
        return data.get("results", [])
    else:
        print(f"Error: {response.status_code}")
        return None


def search_gameplay_videos(game_name):
    """Function used to search gameplay videos and return their specific ids."""
    videosSearch = VideosSearch(game_name + " gameplay", limit=2)
    results = videosSearch.result()
    video_ids = [video["id"] for video in results["result"]]

    return video_ids


def fetch_steam_app_list():
    """Fetch the app list from the Steam API and store it globally."""
    global steam_app_dict
    search_url = "https://api.steampowered.com/ISteamApps/GetAppList/v0002/"
    response = requests.get(search_url)

    if response.status_code == 200:
        steam_app_list = response.json()["applist"]["apps"]
        steam_app_dict = {app["name"].lower(): app["appid"] for app in steam_app_list}


def get_steam_app_id(game_name):
    """Get the app id from the Steam API based on the game name using string similarity matching."""
    global steam_app_dict

    if steam_app_dict is None:
        fetch_steam_app_list()

    if steam_app_dict:
        game_names = list(steam_app_dict.keys())
        closest_matches = difflib.get_close_matches(
            game_name.lower(), game_names, n=1, cutoff=0.95
        )
        if closest_matches:
            closest_match = closest_matches[0]
            return steam_app_dict.get(closest_match)

    return None


def get_steam_game_requirements(app_id):
    """Get the sys requirements for a game from the steam api using the app id."""
    url = f"https://store.steampowered.com/api/appdetails/?appids={app_id}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if str(app_id) in data and "data" in data[str(app_id)]:
            app_data = data[str(app_id)]["data"]

            pc_requirements = get_requirements(app_data.get("pc_requirements"))
            mac_requirements = get_requirements(app_data.get("mac_requirements"))
            linux_requirements = get_requirements(app_data.get("linux_requirements"))

            return pc_requirements, mac_requirements, linux_requirements
        else:
            return None, None, None
    else:
        return None, None, None


def get_latest_gaming_news(api_key, num_articles, offset, start_date, end_date):
    """Use the GameSpot API to retrieve articles related to gaming between specific dates."""
    url = "http://www.gamespot.com/api/articles/"
    headers = {"User-Agent": "Khada-Ake", "Accept": "application/json"}

    params = {
        "api_key": api_key,
        "format": "json",
        "limit": num_articles,
        "sort": "publish_date:desc",
        "filter": f"categories:18,publish_date:{start_date}|{end_date}",
        "offset": offset,
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        articles = response.json()
        return articles["results"]
    else:
        return None


def get_all_articles_from_year(api_key, year, num_articles=100):
    """Retrieve all articles related to gaming from a specific year using the GameSpot API."""
    all_articles = []
    offset = 0
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"

    while True:
        articles = get_latest_gaming_news(
            api_key, num_articles, offset, start_date, end_date
        )
        if not articles:
            break
        all_articles.extend(articles)
        offset += num_articles

    return all_articles


def get_all_articles_from_last_7_days(api_key, num_articles=100):
    """Retrieve all articles related to gaming from the last 7 days using the GameSpot API."""
    all_articles = []
    offset = 0
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    while True:
        articles = get_latest_gaming_news(
            api_key, num_articles, offset, start_date, end_date
        )
        if not articles:
            break
        all_articles.extend(articles)
        offset += num_articles

    return all_articles


def fetch_games_by_genre(genre_id, page_size=10, page=1):
    url = "https://api.rawg.io/api/games"
    params = {
        "key": RAWG_API_KEY,
        "genres": genre_id,
        "page_size": page_size,
        "page": page,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        games = response.json().get("results", [])
        return [game["name"] for game in games]
    else:
        return None


def find_game_on_giantbomb(game_name):
    """Searches for a game on GiantBomb using the GiantBomb API based on the provided game name."""
    url = "https://www.giantbomb.com/api/search/"
    params = {
        "api_key": API_KEY,
        "format": "json",
        "query": game_name,
        "resources": "game",
        "field_list": "name,id",
        "limit": 1,
    }
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        results = response.json().get("results", [])
        if results:
            return f"3030-{results[0]['id']}"
        else:
            return None
    else:
        return f"Failed to search for {game_name}, status code: {response.status_code}"


def fetch_game_ids_by_genre(genre_id, page_size=10, page=1):
    """
    Fetches a list of game IDs from the RAWG API based on the specified genre,
    then searches for those games on GiantBomb and returns a list of game IDs.
    """
    game_names = fetch_games_by_genre(genre_id, page_size, page)
    if game_names:
        game_ids = []
        for game_name in game_names:
            game_id = find_game_on_giantbomb(game_name)
            if game_id:
                game_ids.append(game_id)
        return game_ids
    else:
        return []


def get_popular_game_names(page_size=10, page=1):
    """Fetches popular game names from the RAWG API."""
    url = "https://api.rawg.io/api/games"
    params = {
        "key": RAWG_API_KEY,
        "ordering": "-rating",
        "page_size": page_size,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        games = response.json().get("results", [])
        return [game["name"] for game in games]
    else:
        return None


def fetch_popular_game_ids(page_size=10, page=1):
    """
    Fetches popular game names from the RAWG API,
    then searches for those games on GiantBomb and returns a list of game IDs.
    """
    # Get popular game names from RAWG
    game_names = get_popular_game_names(page_size, page)

    if game_names:
        game_ids = []

        for game_name in game_names:
            game_id = find_game_on_giantbomb(game_name)
            if game_id:
                game_ids.append(game_id)

        return game_ids
    else:
        return []


def search_game(game_name, page=1, page_size=10):
    """Searches for a game by name using the RAWG API and retrieves store information for the game."""
    url = "https://api.rawg.io/api/games"
    params = {
        "key": RAWG_API_KEY,
        "search": game_name,
        "page": page,
        "page_size": page_size,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        games_data = response.json()
        if games_data["results"]:
            first_game = games_data["results"][0]
            game_id = first_game["id"]

            stores = []
            if "stores" in first_game and first_game["stores"]:
                for store_entry in first_game["stores"]:
                    store_id = store_entry["store"]["id"]
                    store_name = store_entry["store"]["name"]
                    stores.append({"store_id": store_id, "store_name": store_name})

            return {"game_id": game_id, "stores": stores}
        else:
            return None
    else:
        print(f"Error: {response.status_code}")
        return None


def fetch_game_stores(game_id):
    """Fetches the store information for a specific game by game ID using the RAWG API."""
    url = f"https://api.rawg.io/api/games/{game_id}/stores"
    params = {
        "key": RAWG_API_KEY,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None


def get_game_store_info(game_name):
    """Retrieves detailed store information for a game based on its name."""
    game_data = search_game(game_name)

    if game_data:
        game_id = game_data["game_id"]
        store_data = fetch_game_stores(game_id)

        store_details = []

        if store_data and "results" in store_data:
            for store_entry in store_data["results"]:
                store_id = store_entry["store_id"]
                url = store_entry["url"]

                store_name = next(
                    (
                        s["store_name"]
                        for s in game_data["stores"]
                        if s["store_id"] == store_id
                    ),
                    None,
                )

                if store_name:
                    store_details.append({"store_name": store_name, "url": url})

            return store_details
        else:
            return None
    else:
        return None


def convert_roman_to_arabic(roman_str):
    """Convert a Roman numeral string to an Arabic number (integer)."""
    try:
        return str(fromRoman(roman_str))
    except (InvalidRomanNumeralError, ValueError):
        return roman_str


def convert_arabic_to_roman(arabic_str):
    """Convert an Arabic number (integer) to a Roman numeral string."""
    try:
        num = int(arabic_str)
        return toRoman(num)
    except (ValueError, InvalidRomanNumeralError):
        return arabic_str


def generate_title_variations(game_name):
    """Generate variations of a game title by converting numbers to Roman numerals and vice versa."""
    words = game_name.split()
    variations = {game_name}

    # Replace numbers with Roman numerals and vice versa
    for i, word in enumerate(words):
        if word.isdigit():
            roman = convert_arabic_to_roman(word)
            if roman != word:
                new_variation = " ".join(words[:i] + [roman] + words[i + 1 :])
                variations.add(new_variation)
        else:
            arabic = convert_roman_to_arabic(word.upper())
            if arabic != word:
                new_variation = " ".join(words[:i] + [arabic] + words[i + 1 :])
                variations.add(new_variation)

    return variations


def fetch_from_api(url, params):
    """Perform an HTTP GET request to the specified URL with provided parameters."""
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None


def search_game_playtime(game_name, page=1, page_size=10):
    """Search for games on the RAWG API by game title."""
    url = "https://api.rawg.io/api/games"
    params = {
        "key": RAWG_API_KEY,
        "search": game_name,
        "page": page,
        "page_size": page_size,
    }
    data = fetch_from_api(url, params)
    return data.get("results", []) if data else []


def fetch_game_playtime(game_id):
    """Retrieve the average playtime for a specific game by its ID."""
    url = f"https://api.rawg.io/api/games/{game_id}"
    params = {"key": RAWG_API_KEY}
    data = fetch_from_api(url, params)
    return data.get("playtime", "N/A") if data else None


def get_game_playtime(game_name):
    """Get the playtime for a specified game by matching its title or variations."""
    variations = generate_title_variations(game_name)
    results = search_game_playtime(game_name)

    for game in results:
        game_title = game["name"].lower()
        if any(variation.lower() == game_title for variation in variations):
            game_id = game["id"]
            return fetch_game_playtime(game_id)

    return None


class FetchDataException(Exception):
    """Custom data exception."""

    pass
