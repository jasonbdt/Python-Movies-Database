"""
SQLite-backed persistence layer for users and movies.

Creates tables on module import (idempotent) and exposes CRUD operations used
by the CLI commands. Uses SQLAlchemy Core and a file-based SQLite database.
"""
from typing import Any

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

import utils
from utils import colored_print
from setup import create_tables
load_dotenv()

# Define the database URL
DB_URL = "sqlite:///data/movies.db"

# Create the engine
engine = create_engine(DB_URL, echo=False)

# create_tables()


def list_movies() -> list[tuple[str, dict[str, Any]]]:
    """
    Return all movies of the current user as ``(title, data)`` pairs.

    The ``data`` dict contains: ``year``, ``rating``, ``poster``, ``note``,
    ``imdb_id``, ``country_iso2``.
    """
    with engine.connect() as connection:
        query = """SELECT title, year, rating, poster, note, imdb_id, country_iso2
                   FROM movies WHERE user_id = :user_id"""
        results = connection.execute(text(query), {
            "user_id": utils.get_current_user()[0]
        })
        movies = results.fetchall()

    return [(title, {
        "year": year,
        "rating": rating,
        "poster": poster,
        "note": note,
        "imdb_id": imdb_id,
        "country_iso2": country_iso2
    }) for title, year, rating, poster, note, imdb_id, country_iso2 in movies]


def add_movie(
    title: str,
    year: int,
    rating: float,
    poster: str,
    note: str,
    imdb_id: str,
    country: str
) -> None:
    """
    Insert a new movie for the current user.

    Args:
        title: Movie title.
        year: Release year.
        rating: Normalized rating (e.g. IMDb 0–10).
        poster: Poster URL.
        note: Optional note (empty string stored as NULL).
        imdb_id: IMDb identifier.
        country: ISO-3166-1 alpha-2 country code.

    Side Effects:
        Writes to the database and prints a success or error message.
    """
    user_id, username = utils.get_current_user()
    with engine.connect() as connection:
        query = """
                INSERT INTO movies (user_id, title, year, rating, poster, note, imdb_id, country_iso2)
                VALUES (:user_id, :title, :year, :rating, :poster, :note, :imdb_id, :country_iso2)
                """
        try:
            connection.execute(text(query), {
                "user_id": user_id,
                "title": title,
                "year": year,
                "rating": rating,
                "poster": poster,
                "note": None if note == "" else note,
                "imdb_id": imdb_id,
                "country_iso2": country
            })
            connection.commit()
            colored_print(f"Movie {title} successfully added "
                          f"to {username}'s collection!", "SUCCESS", True)
        except Exception as err:
            colored_print(f"Error: {err}", "ERROR", True)


def delete_movie(title: str) -> None:
    """
    Delete a movie with the given title for the current user.

    Matching is case-insensitive on the ``title`` column.
    """
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


def update_movie(title: str, note: str) -> None:
    """
    Update the note of an existing movie for the current user.

    Empty strings are persisted as NULL.
    """
    user_id, username = utils.get_current_user()
    with engine.connect() as connection:
        query = ("UPDATE movies SET note = :note "
                 "WHERE LOWER(title) = :title AND user_id = :user_id")
        try:
            connection.execute(text(query), {
                "user_id": user_id,
                "title": title.lower(),
                "note": None if note == "" else note
            })
            connection.commit()
            colored_print(f"Movie '{title}' successfully updated in "
                          f"{username}'s collection!", "SUCCESS", True)
        except Exception as err:
            colored_print(f"Error: {err}", "ERROR", True)


def get_movie(title: str):
    """
    Return a single movie row for the current user by case-insensitive title.

    Returns:
        sqlalchemy.engine.Row | None: The matching row, if any.
    """
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
    """Return all users as ``(id, name)`` tuples."""
    with engine.connect() as connection:
        query = "SELECT id, name FROM users"
        results = connection.execute(text(query))
        users = results.fetchall()

    return [(id, name) for id, name in users]


def add_user(name: str) -> None:
    """Create a new user with the given name and print a confirmation."""
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
