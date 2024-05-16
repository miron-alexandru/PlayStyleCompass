"""The "data_extraction" module provides functions for extracting specific data from API responses."""

from bs4 import BeautifulSoup


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


def get_embed_links(video_ids):
    """Return youtube embed links using the video id's."""
    if video_ids:
        embed_links = []
        for video_id in video_ids:
            embed_links.append(f"https://www.youtube.com/embed/{video_id}")

        return ", ".join(embed_links)
    return None


def extract_data(game_data, field_name):
    """Extract data from game data based on the field name."""
    return game_data.get(field_name, None) if isinstance(game_data, dict) else None


def extract_names(data, field_name):
    """Extract names from data based on the field name."""
    if not isinstance(data, dict):
        return None

    field_data = data.get(field_name)
    if field_data is None:
        return None
    names = [item["name"] for item in field_data]

    return ", ".join(names) if names else None


def get_franchises(game_data):
    """Get game franchises from data."""
    if not isinstance(game_data, dict):
        return None

    franchises_data = game_data.get("franchises")

    if not franchises_data or not isinstance(franchises_data, list):
        return None

    franchises_names = [franchise["name"] for franchise in franchises_data]

    return ", ".join(franchises_names) if franchises_names else None


def get_similar_games(game_data, max_count=7):
    """Extract similar games from data."""
    if isinstance(game_data, dict):
        similar_games = game_data.get("similar_games")

        if similar_games is not None:
            similar_games = [game["name"] for game in similar_games[:max_count]]

            return ", ".join(similar_games) if similar_games else None

    return None


def get_dlcs(game_data):
    """Extract dlc's from data."""
    if isinstance(game_data, dict):
        dlcs = set()
        for dlc in game_data.get("dlcs", []):
            dlcs.add(dlc["name"])
        return ", ".join(dlcs) if dlcs else None
    return None


def get_image(game_data):
    """Get game image from data."""
    if not isinstance(game_data, dict):
        return None
    image_url = game_data["image"].get("small_url", None)
    return (
        "https://i.ibb.co/HnJFgmy/default-psc.jpg"
        if image_url and "default" in image_url
        else image_url
    )


def get_release_date(game_data):
    """Get game release date from data."""
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
    """Get game devs from data."""
    if not isinstance(game_data, dict):
        return None
    if "developers" not in game_data or not isinstance(game_data["developers"], list):
        return None
    developer_names = [developer["name"] for developer in game_data["developers"]]

    return ", ".join(developer_names) if developer_names else None


def extract_first_game(data):
    """Return the first game a character has appeared in."""
    return (
        data["first_appeared_in_game"].get("name", None)
        if data["first_appeared_in_game"]
        else None
    )


def extract_description_text(html_description):
    """Extract description text from review."""
    soup = BeautifulSoup(html_description, "html.parser")
    text = soup.get_text()
    return text


def extract_guids(franchises, franchises_ids_to_add=None):
    """Extract "guid's" from each franchise and add specific ids if provided."""
    franchises_ids = set()

    if franchises_ids_to_add:
        franchises_ids.update(franchises_ids_to_add)

    if franchises:
        for franchise in franchises:
            franchises_ids.add(franchise["guid"])

    return franchises_ids


def extract_character_guids(characters, characters_ids_to_add=None):
    """Extract guid's from each character and add specifict character id's if provided."""
    characters_ids = set()

    if characters_ids_to_add:
        characters_ids.update(characters_ids_to_add)

    if characters:
        for character in characters:
            characters_ids.add(character["guid"])

    return characters_ids


def get_franchise_games(franchise_data):
    """Get games that are from a particular franchise."""
    if not isinstance(franchise_data, dict):
        return None
    if "games" not in franchise_data or not isinstance(franchise_data["games"], list):
        return None

    games = [game["name"] for game in franchise_data["games"]]

    return ", ".join(games) if games else None


def get_franchise_games_count(games):
    """Get the number of games for a franchise."""
    if games:
        games_list = games.split(",")
        return len(games_list)

    return 0


def extract_game_data(game, data_name):
    """Extract game data based on the data_name ."""
    return game[data_name] if isinstance(game, dict) else None


def get_game_concepts(game_data, concept_ids):
    """Extract concept names for games based on concept ids."""
    concept_ids = [id_.split("-")[1] for id_ in concept_ids]

    if isinstance(game_data, dict):
        concepts = game_data.get("concepts", [])
        if concepts is None:
            return None
        else:
            concept_names = [
                concept["name"]
                for concept in concepts
                if str(concept["id"]) in concept_ids
            ]
            return ", ".join(concept_names)
    else:
        return None


def strip_html_tags(text):
    """Remove HTML tags from a string and replace certain characters with newline."""
    replacements = [
        "Processor:",
        "OS:",
        "Memory:",
        "Graphics:",
        "DirectX:",
        "Storage:",
        "Sound Card:",
        "Additional Notes:",
    ]
    remove_strings = ["Minimum:", "Recommended:"]
    soup = BeautifulSoup(text, "html.parser")
    result = soup.get_text()

    for rs in remove_strings:
        result = result.replace(rs, "")

    for r in replacements:
        result = result.replace(r, f"\n{r}")

    return result.strip()


def get_requirements(requirements_data):
    """Get system requirements."""
    if requirements_data:
        return strip_html_tags(requirements_data.get("minimum", None)), strip_html_tags(
            requirements_data.get("recommended", "")
        )
    else:
        return None, None
