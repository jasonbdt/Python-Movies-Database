import json

from app_types import MovieCollection
from movies import APP_DATABASE
from utils import colored_print


def get_movies() -> MovieCollection:
    """
    Returns a dictionary of dictionaries that
    contains the movies information in the database.

    The function loads the information from the JSON
    file and returns the data.

    For example, the function may return:
    {
      "Titanic": {
        "rating": 9,
        "year": 1999
      },
      "..." {
        ...
      },
    }
    """
    try:
        with open(APP_DATABASE, "r") as file_obj:
            return json.load(file_obj)
    except FileNotFoundError:
        colored_print(f"File database ({APP_DATABASE}) not found!", "ERROR")
        with open(APP_DATABASE, "w") as file_obj:
            file_obj.write(json.dumps({}))
            print(f"Created empty database ({APP_DATABASE})")
        return {}


def save_movies(movies: MovieCollection) -> None:
    """
    Gets all your movies as an argument and saves them to the JSON file.

    Returns:
        None
    """
    with open(APP_DATABASE, "w") as file_obj:
        file_obj.write(json.dumps(movies))


def add_movie(title: str, year: int, rating: float) -> None:
    """
    Adds a movie to the movies database.
    Loads the information from the JSON file, add the movie,
    and saves it. The function doesn't need to validate the input.
    """
    movies = get_movies()
    movies[title] = {
        "rating": rating,
        "year": year
    }

    save_movies(movies)


def delete_movie(title: str) -> None:
    """
    Deletes a movie from the movies database.
    Loads the information from the JSON file, deletes the movie,
    and saves it. The function doesn't need to validate the input.
    """
    movies = get_movies()
    if title in movies:
        del movies[title]
        colored_print(f"Movie {title} successfully deleted", "SUCCESS", True)
    else:
        colored_print(f"Movie {title} doesn't exist!", "ERROR", True)

    save_movies(movies)


def update_movie(title: str, rating: float) -> None:
    """
    Updates a movie from the movies database.
    Loads the information from the JSON file, updates the movie,
    and saves it. The function doesn't need to validate the input.
    """
    movies = get_movies()
    movies[title]['rating'] = rating
    save_movies(movies)
