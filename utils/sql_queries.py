create_table_sql = '''
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
    game_images TEXT
);
'''

remove_duplicates_sql = '''
DELETE FROM Games
    WHERE rowid NOT IN (
    SELECT MIN(rowid)
    FROM Games
    GROUP BY title
);
'''

inserting_sql = '''
INSERT INTO Games 
(title, description, overview, genres, platforms, themes, image, release_date, developers, game_images) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
'''