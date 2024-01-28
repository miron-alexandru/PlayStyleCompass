"""Defines sql queries."""

create_table_sql = """
CREATE TABLE IF NOT EXISTS Games (
    id INTEGER PRIMARY KEY,
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
    franchises TEXT
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
    game_id INTEGER,
    likes INTEGER default 0,
    dislikes INTEGER default 0,
    liked_by TEXT default '',
    disliked_by TEXT default ''
);
"""

insert_reviews_sql = """
INSERT INTO Reviews (reviewers, review_deck, review_description, score, user_id, game_id)
VALUES (?, ?, ?, ?, ?, ?);
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


inserting_sql = """
INSERT INTO Games 
(title, description, overview, genres, platforms, themes, image, release_date, developers, game_images, similar_games, dlcs, franchises) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

create_franchises_table = """
CREATE TABLE IF NOT EXISTS Franchises (
    id INTEGER PRIMARY KEY,
    title TEXT,
    overview TEXT,
    description TEXT,
    games TEXT,
    image TEXT
);
"""

insert_franchise_sql = """
INSERT INTO Franchises
(title, overview, description, games, image)
VALUES (?, ?, ?, ?, ?);
"""

remove_duplicate_franchises = """
DELETE FROM Franchises
    WHERE rowid NOT IN (
    SELECT MIN(rowid)
    FROM Franchises
    GROUP BY title
);
"""
