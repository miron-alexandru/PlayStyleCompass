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
    reviewers TEXT,
    review_deck TEXT,
    review_description TEXT,
    score TEXT
);
"""

remove_duplicates_sql = """
DELETE FROM Games
    WHERE rowid NOT IN (
    SELECT MIN(rowid)
    FROM Games
    GROUP BY title
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
(title, description, overview, genres, platforms, themes, image, release_date, developers, game_images, similar_games, reviewers, review_deck, review_description, score) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""
