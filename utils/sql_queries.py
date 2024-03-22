"""Defines sql queries."""

create_table_sql = """
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
    videos TEXT
);
"""

create_reviews_table = """
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
    disliked_by TEXT default ''
);
"""

create_franchises_table = """
CREATE TABLE IF NOT EXISTS Franchises (
    id INTEGER PRIMARY KEY,
    title TEXT,
    overview TEXT,
    description TEXT,
    games TEXT,
    image TEXT,
    images TEXT,
    games_count INTEGER DEFAULT 0
);
"""

create_characters_table = """
CREATE TABLE IF NOT EXISTS Characters (
    id INTEGER PRIMARY KEY,
    name TEXT,
    deck TEXT,
    description TEXT,
    birthday TEXT,
    friends TEXT,
    enemies TEXT,
    games TEXT,
    first_game TEXT,
    franchises TEXT,
    image TEXT,
    images TEXT,
    character_id INTEGER DEFAULT 0
);
"""

create_game_modes_table = """
CREATE TABLE IF NOT EXISTS GameModes (
    id INTEGER PRIMARY KEY,
    game_id TEXT,
    game_name TEXT,
    game_mode TEXT
);
"""

inserting_sql = """
INSERT INTO Games 
(guid, title, description, overview, genres, platforms, themes, image, release_date, developers, game_images, similar_games, dlcs, franchises, videos) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

insert_reviews_sql = """
INSERT INTO Reviews (reviewers, review_deck, review_description, score, user_id, game_id)
VALUES (?, ?, ?, ?, ?, ?);
"""

insert_franchise_sql = """
INSERT INTO Franchises
(title, overview, description, games, image, images, games_count)
VALUES (?, ?, ?, ?, ?, ?, ?);
"""

insert_characters_sql = """
INSERT INTO Characters 
(name, deck, description, birthday, friends, enemies, games, first_game, franchises, image, images, character_id) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

insert_game_modes_sql = """
INSERT INTO GameModes
(game_id, game_name, game_mode)
VALUES (?, ?, ?);
"""

remove_duplicates_sql = """
DELETE FROM Games
    WHERE rowid NOT IN (
    SELECT MIN(rowid)
    FROM Games
    GROUP BY title
);
"""

remove_duplicates_reviews = """
DELETE FROM Reviews 
WHERE rowid NOT IN (
    SELECT MIN(rowid)
    FROM Reviews
    GROUP BY reviewers, game_id
);
"""

remove_duplicate_franchises = """
DELETE FROM Franchises
    WHERE rowid NOT IN (
    SELECT MIN(rowid)
    FROM Franchises
    GROUP BY title
);
"""

remove_duplicate_characters = """
DELETE FROM Characters
    WHERE rowid NOT IN (
    SELECT MIN(rowid)
    FROM Characters
    GROUP BY character_id, name
);
"""

remove_duplicate_game_modes = """
DELETE FROM GameModes
    WHERE rowid NOT IN (
    SELECT MIN(rowid)
    FROM GameModes
    GROUP BY game_id, game_mode
);
"""


remove_empty = """
DELETE FROM Games
WHERE title IS NULL
  AND description IS NULL
  AND overview IS NULL
  AND genres IS NULL
  AND platforms IS NULL
  AND themes IS NULL
  AND image IS NULL
  AND release_date IS NULL
  AND developers IS NULL
  AND game_images IS NULL
  AND similar_games is NULL;
"""
