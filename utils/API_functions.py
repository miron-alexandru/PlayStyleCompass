"""The "API_functions" module provides functions for making API calls and fetching data."""

import datetime
import difflib
from datetime import datetime
import requests
from youtubesearchpython import VideosSearch

from constants import BASE_URL, headers, API_KEY
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
        closest_matches = difflib.get_close_matches(game_name.lower(), game_names, n=1, cutoff=0.95)
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


class FetchDataException(Exception):
    """Custom data exception."""

    pass
