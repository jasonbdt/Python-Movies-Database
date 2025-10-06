from datetime import datetime
import random

import requests
import sys
import os

import matplotlib.pyplot as plt
from dotenv import load_dotenv

import movie_storage as storage
from utils import (CLICommand, SearchResults, calc_median_rating,
                   colored_input, colored_print, COLORS, get_valid_number,
                   filter_by_rating, filter_by_year, compute_suggestions,
                   create_movies_grid)
import views

load_dotenv()

API_BASE = "http://www.omdbapi.com"
API_KEY = os.getenv("API_KEY")
MIN_YEAR = 1888


def get_user_choice() -> CLICommand:
    """
    Prompt the user to select a menu option.

    Prompts for an integer between 0 and ``len(COMMANDS) - 1`` and
    returns the corresponding CLI command from ``COMMANDS``.

    Returns:
        CLICommand: The selected command (callable and its description).
    """
    max_choice = len(COMMANDS) - 1
    result = get_valid_number(
        "Enter choice:",
        with_range=True,
        num_range=(0, max_choice)
    )

    chosen_cmd = list(COMMANDS)[result]
    return COMMANDS[chosen_cmd]


def list_movies() -> None:
    """
    List all movies with their year and rating.

    Loads movies from the JSON-backed storage and prints the total count
    and each movie in the format "Title (Year): Rating".

    Returns:
        None
    """
    movies = storage.list_movies()
    views.display_movie_list(movies)


def add_movie() -> None:
    """
    Add a new movie to the collection.

    Prompts for the movie title, a rating (0–10), and a release year
    between ``MIN_YEAR`` and the current year. Persists the movie to the
    JSON-backed storage.

    Returns:
        None
    """
    movie_name = colored_input("Enter new movie name:")
    if movie_name == "":
        colored_print("\nPlease type in a movie name!", "ERROR", True)
        return

    movies = storage.list_movies()
    if movie_name in movies:
        colored_print("\nMovie already exist!", "ERROR", True)
        return

    movie_data = fetch_movie_data(movie_name)
    if movie_data:
        storage.add_movie(
            movie_data["Title"],
            movie_data["Year"],
            movie_data["imdbRating"],
            movie_data["Poster"]
        )


def fetch_movie_data(title: str):
    try:
        response = requests.get(f"{API_BASE}", params={
            "apikey": API_KEY,
            "t": title
        })
    except requests.exceptions.ConnectionError:
        colored_print(
            f"Error fetching data, please try again later!", "ERROR", True)
    else:
        if response.ok:
            data = response.json()
            if data["Response"] == "True":
                return data
            else:
                colored_print(
                    f"No movie with title '{title}' found.", "ERROR", True)

    return None


def delete_movie() -> None:
    """
    Delete a movie from the collection.

    Prompts for the movie title and removes it from the JSON-backed
    storage.

    Returns:
        None
    """
    movie_name = colored_input("Enter movie name to delete:", True)
    storage.delete_movie(movie_name)


def update_movie() -> None:
    """
    Update a movie's rating.

    Prompts for the movie title and a new rating (0–10). If the movie
    exists, updates its rating in the JSON-backed storage; otherwise
    prints an error.

    Returns:
        None
    """
    movies = storage.list_movies()
    movie_name = colored_input("Enter movie name:", True)

    if movie_name.title() in movies:
        new_movie_rating = get_valid_number("Enter new rating:", float, True)
        storage.update_movie(movie_name, new_movie_rating)
    else:
        colored_print(f"Movie {movie_name} doesn't exist!", "ERROR", True)


def compute_movie_stats() -> None:
    """
    Display summary statistics for the stored movies.

    Loads movies from storage and prints the average and median rating,
    as well as the best and worst rated movie titles.

    Returns:
        None
    """
    movies = storage.list_movies()
    ratings = [movie_data['rating'] for movie_data in movies.values()]
    average_rating = round(sum(ratings) / len(ratings), 2)
    median_rating = calc_median_rating(ratings)
    best_movies = [
        f"{name} ({data['rating']:.1f})" for name, data in movies.items()
        if data['rating'] == max(ratings)
    ]
    worst_movies = [
        f"{name} ({data['rating']:.1f})" for name, data in movies.items()
        if data['rating'] == min(ratings)
    ]

    views.display_movie_stats(
        (average_rating, median_rating, best_movies, worst_movies)
    )


def random_movie() -> None:
    movies = storage.list_movies()
    movie_names = list(map(lambda movie: movie, movies))
    rnd_movie = random.choice(movie_names)
    views.display_random_movie(rnd_movie, movies[rnd_movie]['rating'])


def search_movie() -> None:
    """
    Search for movies by substring and show fuzzy suggestions if needed.

    Prompts the user for a substring and displays direct matches against stored
    titles (simple substring check). If no matches are found, computes fuzzy
    suggestions using ``Levenshtein.ratio`` with ``SEARCH_THRESHOLD`` and displays
    them.

    Returns:
        None
    """
    movies = storage.list_movies()
    search_results: SearchResults = []
    search_term = colored_input("Enter part of movie name:", True)
    for title, data in movies:
        if search_term.lower() in title.lower():
            search_results.append((title, data))

    if search_results:
        views.display_movie_list(search_results, show_total=False)
    else:
        suggestions = compute_suggestions(search_term, movies)
        highlighted_search_term = f"{COLORS['MOVIE_TITLE']}" \
                                  f"{search_term}"
        if suggestions:
            colored_print(
                f"The movie {highlighted_search_term}{COLORS['INFO']} doesn't "
                "exist. Did you mean:", "INFO"
            )
            views.display_movie_list(suggestions, show_total=False)
        else:
            colored_print(
                f"The movie {highlighted_search_term}{COLORS['ERROR']} doesn't"
                " exist.", "ERROR")
    print()


def filter_movies() -> None:
    """
    Retrieve movies from storage and apply optional rating/year filters.

    Prompts the user for an optional minimum rating and optional start/end
    years. Blank inputs are allowed and interpreted as "no filter"
    (internally a sentinel value is used). Each provided criterion is
    applied in sequence to narrow the results.

    Returns:
        dict[str, dict]: Mapping of movie titles to their data that match the
            provided criteria.
    """
    movies = storage.list_movies()
    current_year = datetime.now().year
    min_rating = get_valid_number(
        "Enter minimum rating (leave blank for no minimum rating):",
        num_type=float,
        with_range=True,
        display_range=False,
        allow_empty=True
    )

    start_year = get_valid_number(
        "Enter start year (leave blank for no start year):",
        with_range=True,
        display_range=False,
        num_range=(MIN_YEAR, current_year),
        allow_empty=True
    )

    end_year = get_valid_number(
        "Enter end year (leave blank for no end year):",
        with_range=True,
        display_range=False,
        num_range=(MIN_YEAR, current_year),
        allow_empty=True
    )

    if min_rating:
        movies = filter(
            lambda movie: filter_by_rating(movie, min_rating),
            movies
        )

    if start_year:
        movies = filter(
            lambda movie: filter_by_year(movie, start_year),
            movies
        )

    if end_year:
        movies = filter(
            lambda movie: filter_by_year(movie, end_year, 'end'),
            movies
        )

    views.display_movie_list(movies)


def movies_by_rating() -> None:
    """
    Display all movies sorted by rating (descending).

    Returns:
        None
    """
    movies = storage.list_movies()
    sorted_movies = sorted(
        movies,
        key=lambda movie: movie[1]['rating'],
        reverse=True
    )
    views.display_movie_list(sorted_movies)


def movies_by_year() -> None:
    """
    Display all movies sorted by release year.

    Prompts the user to choose the ordering ("First" => newest first,
    "Last" => oldest first). Loads movies via ``movie_storage``, sorts by
    the ``year`` field, and prints each entry as "Title (Year): Rating".

    Returns:
        None
    """
    user_choices = ["First", "Last"]
    movies = storage.list_movies()
    views.display_menu(user_choices, "Choose order of latest movies")
    user_choice = get_valid_number(
        "Enter choice:",
        with_range=True,
        num_range=(0, len(user_choices) - 1)
    )

    sorted_movies = sorted(
        movies,
        key=lambda movie: movie[1]['year'],
        reverse=True if user_choice == 0 else False
    )

    views.display_movie_list(
        sorted_movies, show_total=False, show_release_years=True)


def create_rating_histogram() -> None:
    """
    Create and save a histogram of movie ratings.

    Prompts for an output filename, builds a histogram of all stored
    movie ratings using Matplotlib, and saves it with ``plt.savefig``.
    Prints an error if no filename is provided.

    Returns:
        None
    """
    file_name = colored_input(
        "In which file do you want to save the histogram?:"
        f"{COLORS['RESET']}\n", extra_whitespace=False)

    if file_name != "":
        movies = storage.list_movies()
        ratings = [data['rating'] for name, data in movies]
        plt.hist(ratings)
        plt.savefig(f"{file_name}")
    else:
        colored_print("File name can't be empty!", "ERROR")
    print()


def generate_website() -> None:
    try:
        with open("static/index_template.html", "r") as file_obj:
            template = file_obj.read()
    except FileNotFoundError:
        colored_print(
            "Template file 'static/index_template.html' not found!",
            "ERROR", True)
    else:
        app_title = os.getenv("APP_TITLE")
        movies_grid = create_movies_grid()
        template = template.replace("__TEMPLATE_TITLE__", app_title)
        template = template.replace("__TEMPLATE_MOVIE_GRID__", movies_grid)

        with open("static/index.html", "w") as file_obj:
            file_obj.write(template)
            colored_print(
                "Website was generated successfully.", "SUCCESS", True)


def start_movie_app() -> None:
    """
    Start the interactive movie application loop.

    Displays the title, then repeatedly shows the menu, reads the user's
    choice, and executes the selected command. Movie data is read from
    and written to a JSON file via ``movie_storage`` during
    these operations.

    Returns:
        None
    """
    views.display_app_title()
    while True:
        views.display_menu(COMMANDS)
        user_cmd, *_ = get_user_choice()

        user_cmd()
        colored_input("Press enter to continue")
        print()


def exit_movie_app() -> None:
    """
    Exit the application with a goodbye message.

    Returns:
        None
    """
    colored_print("Good bye!", "HIGHLIGHT")
    sys.exit(0)


COMMANDS: dict[str, CLICommand] = {
    "Exit": (
        exit_movie_app,
        "Exits the Movies Database application."
    ),
    "List Movies": (
        list_movies,
        "Lists each Movie stored in applications database."
    ),
    "Add Movie": (
        add_movie,
        "Stores a new movie in applications database."
    ),
    "Delete Movie": (
        delete_movie,
        "Delete a stored movie from applications database."
    ),
    "Update Movie": (
        update_movie,
        "Update a stored movie in applications database."
    ),
    "Stats": (
        compute_movie_stats,
        "Displays average stats for each movie stored in applications "
        "database."
    ),
    "Random Movie": (
        random_movie,
        "Displays a random movie stored in applications database."
    ),
    "Search Movie": (
        search_movie,
        "Searches for movies in applications database by search term "
        "that is given by user input."
    ),
    "Filter Movies": (
        filter_movies,
        "Let users filter movies based on specific criteria such as "
        "minimum rating, start year, and end year."
    ),
    "Movies sorted by rating": (
        movies_by_rating,
        "Displays movies by their corresponding rating."
    ),
    "Movies sorted by release year": (
        movies_by_year,
        "Displays each movie in a chronological order chosen by user."
    ),
    "Create rating histogram": (
        create_rating_histogram,
        "Create a movie rating histogram and store it as file."
    ),
    "Generate website": (
        generate_website,
        "Generates a website with all movies that are stored in database"
    )
}
