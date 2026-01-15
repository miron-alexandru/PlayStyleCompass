import sqlite3
import json
import os

DB_PATH = "playstyle_db.sqlite3"
JSON_PATH = "games_data.json"

if not os.path.exists(JSON_PATH):
    print(f"Cannot find {JSON_PATH}")
    exit(1)

with open(JSON_PATH, "r", encoding="utf-8") as f:
    games = json.load(f)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute("""
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
""")

# Insert games
for g in games:
    # Skip if guid already exists
    c.execute("SELECT 1 FROM Games WHERE guid=?", (g["guid"],))
    if c.fetchone():
        continue

    values = [g.get(col) if g.get(col) is not None else "" for col in g.keys()]
    placeholders = ", ".join("?" for _ in values)
    columns = ", ".join(g.keys())
    sql = f"INSERT INTO Games ({columns}) VALUES ({placeholders})"
    c.execute(sql, values)

conn.commit()
conn.close()
