from typing import Any
import os

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from utils import colored_print
load_dotenv()

# Define the database URL
DB_URL = "sqlite:///data/movies.db"

# Create the engine
engine = create_engine(DB_URL, echo=bool(os.getenv("DEBUG_SQL")))

# Create the movies table if it does not exist
with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            poster TEXT NOT NULL
        )
    """))
    connection.commit()


def list_movies() -> list[tuple[str, dict[str, Any]]]:
    """Retrieve all movies from the database."""
    with engine.connect() as connection:
        query = "SELECT title, year, rating, poster FROM movies"
        results = connection.execute(text(query))
        movies = results.fetchall()

    return [(title, {
        "year": year,
        "rating": rating,
        "poster": poster
    }) for title, year, rating, poster in movies]


def add_movie(title: str, year: int, rating: float, poster: str) -> None:
    """Add a new movie to the database."""
    with engine.connect() as connection:
        query = ("INSERT INTO movies (title, year, rating, poster) "
                 "VALUES (:title, :year, :rating, :poster)")
        try:
            connection.execute(text(query), {
                "title": title,
                "year": year,
                "rating": rating,
                "poster": poster
            })
            connection.commit()
            colored_print(
                f"Movie {title} successfully added.", "SUCCESS", True)
        except Exception as err:
            print(f"Error: {err}")


def delete_movie(title: str) -> None:
    """Delete an existing movie from the database."""
    with engine.connect() as connection:
        query = "DELETE FROM movies WHERE LOWER(title) = :title"
        try:
            connection.execute(text(query), {
                "title": title.lower()
            })
            connection.commit()
            colored_print(
                f"Movie '{title}' successfully deleted.", "SUCCESS", True)
        except Exception as err:
            print(f"Error: {err}")


def update_movie(title: str, rating: float) -> None:
    """Update an existing movie rating from the database."""
    with engine.connect() as connection:
        query = "UPDATE movies SET rating = :rating WHERE LOWER(title) = :title"
        try:
            connection.execute(text(query), {
                "title": title.lower(),
                "rating": rating
            })
            connection.commit()
            colored_print(
                f"Movie '{title}' successfully updated", "SUCCESS", True)
        except Exception as err:
            print(f"Error: {err}")
