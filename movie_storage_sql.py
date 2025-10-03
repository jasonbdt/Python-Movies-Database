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


def add_movie(title: str, year: int, rating: float) -> None:
    """Add a new movie to the database."""
    with engine.connect() as connection:
        query = ("INSERT INTO movies (title, year, rating) "
                 "VALUES (:title, :year, :rating)")
        try:
            connection.execute(text(query, {
                "title": title,
                "year": year,
                "rating": rating
            }))
            connection.commit()
            print(f"Movie '{title} added successfully.'")
        except Exception as err:
            print(f"Error: {err}")


def delete_movie(title: str) -> None:
    """Delete an existing movie from the database."""
    with engine.connect() as connection:
        query = "DELETE FROM movies WHERE title = :title"
        try:
            connection.execute(text(query, {
                "title": title
            }))
            connection.commit()
            print(f"Movie '{title}' successfully deleted.")
        except Exception as err:
            print(f"Error: {err}")


def update_movie(title: str, rating: float) -> None:
    """Update an existing movie rating from the database."""
    with engine.connect() as connection:
        query = "UPDATE movies SET rating = :rating WHERE title = :title"
        try:
            connection.execute(text(query, {
                "title": title,
                "rating": rating
            }))
            connection.commit()
            print(f"Movie '{title}' successfully updated.")
        except Exception as err:
            print(f"Error: {err}")
