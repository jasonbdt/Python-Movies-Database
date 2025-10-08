from typing import Any
import os

from sqlalchemy import create_engine, text, Row
from dotenv import load_dotenv

import utils
from utils import colored_print
load_dotenv()

# Define the database URL
DB_URL = "sqlite:///data/movies.db"

# Create the engine
engine = create_engine(DB_URL, echo=bool(os.getenv("DEBUG_SQL")))

# Create the `movies` and `users` table if they does not exist
with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            'id' INTEGER NOT NULL,
            'name' TEXT NOT NULL,
            PRIMARY KEY('id' AUTOINCREMENT)
        );
    """))

    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            'id' INTEGER NOT NULL,
            'user_id' INTEGER NOT NULL,
            'title' TEXT NOT NULL,
            'year' INTEGER NOT NULL,
            'rating' REAL NOT NULL,
            'poster' TEXT NOT NULL,
            PRIMARY KEY('id' AUTOINCREMENT),
            FOREIGN KEY('user_id') REFERENCES 'users'('id')
        );
    """))
    connection.commit()


def list_movies() -> list[tuple[str, dict[str, Any]]]:
    """Retrieve all movies from the database."""
    with engine.connect() as connection:
        query = "SELECT title, year, rating, poster FROM movies WHERE user_id = :user_id"
        results = connection.execute(text(query), {
            "user_id": utils.get_current_user()[0]
        })
        movies = results.fetchall()

    return [(title, {
        "year": year,
        "rating": rating,
        "poster": poster
    }) for title, year, rating, poster in movies]


def add_movie(title: str, year: int, rating: float, poster: str) -> None:
    """Add a new movie to the database."""
    user_id, username = utils.get_current_user()
    with engine.connect() as connection:
        query = """
                INSERT INTO movies (user_id, title, year, rating, poster)
                VALUES (:user_id, :title, :year, :rating, :poster)
                """
        try:
            connection.execute(text(query), {
                "user_id": user_id,
                "title": title,
                "year": year,
                "rating": rating,
                "poster": poster
            })
            connection.commit()
            colored_print(f"Movie {title} successfully added "
                          f"to {username}'s collection!", "SUCCESS", True)
        except Exception as err:
            colored_print(f"Error: {err}", "ERROR", True)


def delete_movie(title: str) -> None:
    """Delete an existing movie from the database."""
    user_id, username = utils.get_current_user()
    with engine.connect() as connection:
        query = ("DELETE FROM movies WHERE LOWER(title) = :title "
                 "AND user_id = :user_id")
        try:
            connection.execute(text(query), {
                "user_id": user_id,
                "title": title.lower()
            })
            connection.commit()
            colored_print(f"Movie '{title}' successfully deleted from "
                          f"{username}'s collection!", "SUCCESS", True)
        except Exception as err:
            colored_print(f"Error: {err}", "ERROR", True)


def update_movie(title: str, rating: float) -> None:
    """Update an existing movie rating from the database."""
    user_id, username = utils.get_current_user()
    with engine.connect() as connection:
        query = ("UPDATE movies SET rating = :rating "
                 "WHERE LOWER(title) = :title AND user_id = :user_id")
        try:
            connection.execute(text(query), {
                "user_id": user_id,
                "title": title.lower(),
                "rating": rating
            })
            connection.commit()
            colored_print(f"Movie '{title}' successfully updated in "
                          f"{username}'s collection!", "SUCCESS", True)
        except Exception as err:
            colored_print(f"Error: {err}", "ERROR", True)


def get_movie(title: str):
    """Retrieve a single movie item from the database."""
    user_id, *_ = utils.get_current_user()
    with engine.connect() as connection:
        query = """SELECT * FROM movies WHERE LOWER(title) = :title
                AND user_id = :user_id"""
        results = connection.execute(text(query), {
            "title": title.lower(),
            "user_id": user_id
        })
        movie = results.fetchone()

    return movie


def get_users() -> list[tuple[int, str]]:
    """Retrieve all users from the database."""
    with engine.connect() as connection:
        query = "SELECT id, name FROM users"
        results = connection.execute(text(query))
        users = results.fetchall()

    return [(id, name) for id, name in users]


def add_user(name: str) -> None:
    with engine.connect() as connection:
        query = "INSERT INTO users (name) VALUES (:name)"
        try:
            connection.execute(text(query), {
                "name": name
            })
            connection.commit()
            colored_print(
                f"User '{name}' successfully created.", "SUCCESS", True)
        except Exception as err:
            colored_print(f"Error: {err}", "ERROR", True)
