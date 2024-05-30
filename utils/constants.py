# List of platform IDs
"""
Pc(94)
Mac(17)
Mobile (123, 96)
Nintendo ( 21, 52, 157)
Xbox (32)
PlayStation (22, 19)
Linux (152)
Browser (140)
Wii (36)
"""

import os
from dotenv import load_dotenv

load_dotenv()

platform_ids = [
    "94",
    "17",
    "123",
    "96",
    "21",
    "52",
    "32",
    "22",
    "152",
    "140",
    "36",
    "157",
    "19",
    "176",
    "146",
]

concept_ids = [
    "3015-2029",
    "3015-464",
    "3015-183",
    "3015-27",
    "3015-1308",
    "3015-24",
    "3015-217",
    "3015-1009",
    "3015-469",
    "3015-199",
    "3015-383",
    "3015-934",
    "3015-1297",
    "3015-250",
    "3015-2220",
    "3015-2911",
    "3015-330",
    "3015-559",
    "3015-932",
    "3015-6130",
    "3015-322",
    "3015-229",
    "3015-174",
    "3015-753",
    "3015-1427",
    "3015-2329",
    "3015-29",
    "3015-2352",
    "3015-3178",
    "3015-2287",
    "3015-765",
    "3015-192",
    "3015-18",
    "3015-755",
    "3015-79",
    "3015-253",
    "3015-207",
    "3015-155",
    "3015-2125",
    "3015-8592",
    "3015-611",
    "3015-292",
    "3015-405",
    "3015-3603",
    "3015-185",
    "3015-125",
    "3015-73",
    "3015-767",
    "3015-338",
    "3015-77",
    "3015-442",
    "3015-515",
    "3015-1118",
    "3015-376",
    "3015-740",
    "3015-161",
    "3015-6",
    "3015-340",
    "3015-1200",
    "3015-648",
    "3015-1363",
    "3015-357",
    "3015-451",
    "3015-4640",
    "3015-4801",
    "3015-346",
    "3015-1843",
    "3015-2163",
    "3015-1467",
    "3015-1018",
    "3015-133",
]

concept_names = [
    "Visual Novel",
    "Third-Person Perspective",
    "Difficulty Level",
    "Multiple Endings",
    "Free to Play",
    "Stealth",
    "Character Creation",
    "Military",
    "Hack and Slash",
    "Microtransaction",
    "Linear Gameplay",
    "Crafting",
    "Survival",
    "Grinding",
    "Skill Points",
    "Indie",
    "First-Person Perspective",
    "Online",
    "Puzzle",
    "Single-Player Only",
    "Split-Screen Multiplayer",
    "Boss",
    "Multiple Protagonists",
    "Time Limit",
    "2D",
    "Digital Distribution",
    "Achievements",
    "Male Protagonists",
    "Sequel",
    "Female Protagonists",
    "Games Based on Anime",
    "Turn-Based",
    "Combo",
    "Games Based on Movies",
    "Zombie",
    "Romance",
    "Open World",
    "Customizable Character",
    "Character Select Screen",
    "Action RPG",
    "World Map",
    "Checkpoint",
    "Character Class",
    "RPG Elements",
    "Minimap",
    "Party System",
    "Time Travel",
    "Exploration",
    "Side Quest",
    "Dialogue Tree",
    "Plot Twist",
    "Martial Arts",
    "Underwater Gameplay",
    "High Definition Graphics",
    "Instant Death",
    "Loot Gathering",
    "Quick Time Event",
    "Remake",
    "Upgradeable Vehicles",
    "Upgradeable Weapon",
    "Voice Chat",
    "Revenge",
    "Realism",
    "Deathmatch",
    "Apocalypse",
    "Survival Horror",
    "Player vs Player",
    "Blocking",
    "Ranking System",
    "Never-Ending",
    "Game Based on Literature",
]


genres = [
    "Action",
    "Adventure",
    "Role-Playing",
    "Strategy",
    "Sports",
    "Shooter",
    "Simulation",
    "Puzzle",
    "Horror",
    "MMORPG",
    "MOBA",
    "Driving/Racing",
    "Fighting",
    "Anime",
    "Platformer",
]

all_themes = [
    "Fantasy",
    "Anime",
    "Comedy",
    "Crime",
    "Cyberpunk",
    "Horror",
    "Medieval",
    "Sci-Fi",
    "Superhero",
    "Motorsports",
    "Martial Arts",
]

all_platforms = [
    "PC",
    "PlayStation",
    "PlayStation 4",
    "PlayStation 5",
    "Xbox",
    "Nintendo",
    "Android",
    "iPhone",
    "Mac",
    "Linux",
    "Wii",
    "Browser",
]

game_ids_to_add = [
    "3030-85645",
    "3030-85432",
    "3030-89473",
    "3030-82375",
    "3030-72597",
    "3030-86375",
    "3030-75881",
    "3030-88561",
    "3030-48190",
    "3030-41484",
    "3030-73982",
    "3030-24024",
    "3030-80641",
    "3030-49998",
    "3030-56725",
    "3030-36765",
    "3030-38456",
    "3030-37030",
    "3030-80643",
    "3030-74787",
    "3030-55211",
    "3030-25462",
    "3030-73727",
    "3030-89729",
    "3030-85645",
    "3030-81387",
    "3030-89239",
    "3030-83940",
    "3030-32327",
    "3030-82842",
    "3030-86145",
]

franchises_ids_to_add = [
    "3025-82",
    "3025-6",
    "3025-38",
    "3025-609",
    "3025-282",
    "3025-7",
    "3025-2",
    "3025-397",
    "3025-267",
    "3025-1495",
    "3025-244",
    "3025-174",
    "3025-194",
    "3025-51",
]

GAMING_COMMITMENT_CHOICES = [
    ("Newbie", "Newbie"),
    ("Casual", "Casual"),
    ("Enthusiast", "Enthusiast"),
    ("Hardcore", "Hardcore"),
    ("Professional", "Professional"),
]

PLATFORM_CHOICES = [
    ("PC", "PC"),
    ("PlayStation", "PlayStation"),
    ("Xbox", "Xbox"),
    ("Nintendo", "Nintendo"),
    ("Mobile", "Mobile"),
    ("VR", "VR"),
    ("Browser", "Browser"),
    ("Arcade", "Arcade"),
]

GENRE_CHOICES = [
    ("FPS", "First-Person Shooter"),
    ("RPG", "Role-Playing Game"),
    ("MMO", "Massively Multiplayer Online"),
    ("MOBA", "Multiplayer Online Battle Arena"),
    ("Strategy", "Strategy"),
    ("Sports", "Sports"),
    ("Adventure", "Adventure"),
    ("Simulation", "Simulation"),
    ("Platformer", "Platformer"),
    ("Puzzle", "Puzzle"),
    ("Horror", "Horror"),
    ("Fighting", "Fighting"),
    ("Driving/Racing", "Driving/Racing"),
]


API_KEY = str(os.getenv("GBAPI_KEY"))
GOOGLE_API_KEY = str(os.getenv("GOOGLE_API_KEY"))

BASE_URL = "https://www.giantbomb.com/api/"

headers = {
    "User-Agent": "PlayStyleCompass/1.0",
}
