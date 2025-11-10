from movie_storage import engine
from sqlalchemy import text

def create_tables() -> None:
    with engine.connect() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                'id' INTEGER NOT NULL,
                'name' TEXT NOT NULL,
                PRIMARY KEY ('id' AUTOINCREMENT)
            );
        """))

        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS movies (
                'id' INTEGER NOT NULL,
                'user_id' INTEGER NOT NULL,
                'imdb_id' TEXT NOT NULL,
                'title' TEXT NOT NULL,
                'year' INTEGER NOT NULL,
                'rating' REAL NOT NULL,
                'poster' TEXT NOT NULL,
                'note' TEXT,
                'country_iso2' TEXT NOT NULL,
                PRIMARY KEY ('id' AUTOINCREMENT),
                FOREIGN KEY ('user_id') REFERENCES 'users' ('id')
            );
        """))
        connection.commit()
