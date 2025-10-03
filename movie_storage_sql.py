from typing import Any
from sqlalchemy import create_engine, text

# Define the database URL
DB_URL = "sqlite:///movies.db"

# Create the engine
engine = create_engine(DB_URL, echo=True)

# Create the movies table if it does not exist
with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL
        )
    """))
    connection.commit()


def list_movies() -> dict[Any, dict[str, Any]]:
    """Retrieve all movies from the database."""
    with engine.connect() as connection:
        query = "SELECT title, year, rating FROM movies"
        results = connection.execute(text(query))
        movies = results.fetchall()

    return {row[0]: {
        "year": row[1],
        "rating": row[2]
    } for row in movies}
