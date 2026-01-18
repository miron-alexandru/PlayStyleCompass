import sqlite3
import json
import os

DB_PATH = "playstyle_db.sqlite3"

TABLES = [
    {
        "name": "Games",
        "json": "db_data/games_data.json",
        "schema": """
        CREATE TABLE IF NOT EXISTS Games (
        id INTEGER PRIMARY KEY,
        guid INTEGER,
        title TEXT,
        description TEXT,
        overview TEXT,
        genres TEXT,
        platforms TEXT,
        themes TEXT,
        image TEXT,
        release_date TEXT,
        developers TEXT,
        game_images TEXT,
        similar_games TEXT,
        dlcs TEXT,
        franchises TEXT,
        videos TEXT,
        concepts TEXT,
        pc_req_min TEXT default '',
        pc_req_rec TEXT default '',
        mac_req_min TEXT default '',
        mac_req_rec TEXT default '',
        linux_req_min TEXT default '',
        linux_req_rec TEXT default '',
        average_score REAL DEFAULT 0,
        total_reviews DEFAULT 0,
        translated_description_ro TEXT,
        translated_overview_ro TEXT,
        is_casual INTEGER DEFAULT 0,
        is_popular INTEGER DEFAULT 0,
        playtime TEXT
    )
    """,
        "unique_check": "guid"
    },
    {
        "name": "Characters",
        "json": "db_data/characters_data.json",
        "schema": """
        CREATE TABLE IF NOT EXISTS Characters (
            id INTEGER PRIMARY KEY,
            name TEXT,
            deck TEXT,
            description TEXT default '',
            birthday TEXT,
            friends TEXT,
            enemies TEXT,
            games TEXT,
            first_game TEXT,
            franchises TEXT,
            image TEXT,
            images TEXT,
            character_id INTEGER DEFAULT 0
        )
        """,
        "unique_check": "character_id"
    },
    {
        "name": "Franchises",
        "json": "db_data/franchises_data.json",
        "schema": """
        CREATE TABLE IF NOT EXISTS Franchises (
            id INTEGER PRIMARY KEY,
            title TEXT,
            overview TEXT,
            description TEXT,
            games TEXT,
            image TEXT,
            images TEXT,
            games_count INTEGER DEFAULT 0
        )
        """,
        "unique_check": "title"
    },
    {
        "name": "GameModes",
        "json": "db_data/game_modes_data.json",
        "schema": """
        CREATE TABLE IF NOT EXISTS GameModes (
            id INTEGER PRIMARY KEY,
            game_id TEXT,
            game_name TEXT,
            game_mode TEXT
        )
        """,
        "unique_check": ("game_id", "game_mode")
    },
    {
        "name": "Reviews",
        "json": "db_data/reviews_data.json",
        "schema": """
        CREATE TABLE IF NOT EXISTS Reviews (
            id INTEGER PRIMARY KEY,
            reviewers TEXT,
            review_deck TEXT,
            review_description TEXT,
            score TEXT,
            user_id INTEGER,
            game_id TEXT,
            likes INTEGER default 0,
            dislikes INTEGER default 0,
            liked_by TEXT default '',
            disliked_by TEXT default '',
            date_added TEXT default ''
        )
        """,
        "unique_check": ("user_id", "game_id", "date_added")
    }
]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

total_inserted = 0

for t in TABLES:
    print("Processing", t["name"])

    if not os.path.exists(t["json"]):
        print("  File not found", t["json"])
        continue

    c.execute(t["schema"])

    with open(t["json"], "r", encoding="utf-8") as f:
        rows = json.load(f)

    inserted = 0

    for row in rows:
        uc = t["unique_check"]

        if isinstance(uc, tuple):
            where = " AND ".join(f"{k}=?" for k in uc)
            params = [row.get(k) for k in uc]
        else:
            where = f"{uc}=?"
            params = [row.get(uc)]

        c.execute(
            f"SELECT 1 FROM {t['name']} WHERE {where}",
            params
        )

        if c.fetchone():
            continue

        keys = row.keys()
        values = [row.get(k) if row.get(k) is not None else "" for k in keys]
        placeholders = ", ".join("?" for _ in keys)
        columns = ", ".join(keys)

        c.execute(
            f"INSERT INTO {t['name']} ({columns}) VALUES ({placeholders})",
            values
        )

        inserted += 1

    print("  Inserted", inserted, t["name"])
    total_inserted += inserted

conn.commit()
conn.close()

print("Done")
print("Total rows inserted", total_inserted)
