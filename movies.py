"""
High-level CLI commands (use cases) for the Movies Database app.

This module wires user input/output (via `utils` and `views`) with the
persistence layer (`movie_storage`). Each function represents a user-facing
command that can be bound to the main menu.
"""

from datetime import datetime
import random

import requests
import sys
import os

import matplotlib.pyplot as plt
from dotenv import load_dotenv

import movie_storage as storage
import utils
import views
load_dotenv()

API_BASE = "http://www.omdbapi.com"
API_KEY = os.getenv("API_KEY")
MIN_YEAR = 1888


def get_user_choice() -> utils.CLICommand:
    """
    Return the selected CLI command from the main menu.

    Prompts the user for an integer between 0 and ``len(COMMANDS) - 1`` and
    returns the corresponding (callable, description) tuple.

    Returns:
        CLICommand: The command tuple selected by the user.
    """
    max_choice = len(COMMANDS) - 1
    result = utils.get_valid_number(
        "Enter choice:",
        with_range=True,
        num_range=(0, max_choice)
    )

    chosen_cmd = list(COMMANDS)[result]
    return COMMANDS[chosen_cmd]


def list_movies() -> None:
    """
    List all movies with their year and rating.

    Loads movies from storage and displays them in a formatted list. Prints the
    total count first and then each entry as "Title (Year): Rating".
    """
    movies = storage.list_movies()
    views.display_movie_list(movies)


def add_movie() -> None:
    """
    Add a new movie to the collection.

    Prompts the user for a title and a note. Attempts to fetch metadata from
    OMDb (title, year, rating, poster, IMDb ID, country). If successful, the
    movie is stored for the current user.

    Side Effects:
        - Performs HTTP requests to OMDb and API Ninjas (country ISO2).
        - Writes a new record to the database on success.
        - Prints user feedback to the console.

    Raises:
        None. Errors are reported as user-facing messages.
    """
    movie_name = utils.colored_input("Enter new movie name:")
    if movie_name == "":
        utils.colored_print("\nPlease type in a movie name!", "ERROR", True)
        return

    if storage.get_movie(movie_name):
        *_, username = utils.get_current_user()
        utils.colored_print(
            f"Movie '{movie_name}' already exist in {username}'s collection!",
            color="ERROR", extra_break=True)
    else:
        movie_data = fetch_movie_data(movie_name)
        note = utils.colored_input("Enter movie note:", extra_whitespace=True)
        if movie_data:
            country_iso2 = requests.get(
                "https://api.api-ninjas.com/v1/country",
                params={"name": movie_data["Country"].split(',')[0].strip()},
                headers={"X-Api-Key": os.getenv("API_NINJA_KEY")}
            )

            if country_iso2.ok:
                storage.add_movie(
                    movie_data["Title"],
                    movie_data["Year"],
                    movie_data["imdbRating"],
                    movie_data["Poster"],
                    note,
                    movie_data["imdbID"],
                    country_iso2.json()[0]['iso2']
                )
            else:
                utils.colored_print(
                    "Unable to fetch movies origin country", "ERROR", True)


def fetch_movie_data(title: str):
    """
    Fetch movie metadata from OMDb by exact title.

    Args:
        title: Exact movie title to query.

    Returns:
        dict | None: The OMDb response payload when found, otherwise ``None``.

    Notes:
        Connection errors and "not found" cases are handled with user-facing
        console messages and return ``None``.
    """
    try:
        response = requests.get(f"{API_BASE}", params={
            "apikey": API_KEY,
            "t": title
        })
    except requests.exceptions.ConnectionError:
        utils.colored_print(
            f"Error fetching data, please try again later!", "ERROR", True)
    else:
        if response.ok:
            data = response.json()
            if data["Response"] == "True":
                return data
            else:
                utils.colored_print(
                    f"No movie with title '{title}' found.", "ERROR", True)

    return None


def delete_movie() -> None:
    """
    Delete a movie owned by the current user.

    Prompts for the title and removes it from storage if present; otherwise
    prints an error message.
    """
    *_, username = utils.get_current_user()
    movie_name = utils.colored_input("Enter movie name to delete:", True)
    if storage.get_movie(movie_name):
        storage.delete_movie(movie_name)
    else:
        utils.colored_print(
            f"No movie called '{movie_name}' in {username}'s collection!",
            color="ERROR", extra_break=True)


def update_movie() -> None:
    """
    Update the note of an existing movie.

    Prompts for a title and the new note value. If the movie exists, updates
    its note; otherwise prints an error.
    """
    *_, username = utils.get_current_user()
    movie_name = utils.colored_input("Enter movie name:", True)
    if storage.get_movie(movie_name):
        new_movie_note = utils.colored_input("Enter movie note:", True)
        storage.update_movie(movie_name, new_movie_note)
    else:
        utils.colored_print(f"No movie called '{movie_name}' in "
                            f"{username}'s collection!", "ERROR", True)


def compute_movie_stats() -> None:
    """
    Compute and display summary statistics over stored movies.

    Shows average rating, median rating, and the list of best/worst rated
    titles among the current user's collection.
    """
    movies = storage.list_movies()
    sorted_movies = sorted(movies, key=lambda movie: movie[1]['rating'])
    ratings = list(map(lambda movie: movie[1]['rating'], sorted_movies))
    ratings.sort(reverse=True)

    average_rating = round(sum(ratings) / len(ratings), 2)
    median_rating = utils.calc_median_rating(ratings)
    best_movies = list(map(lambda movie: movie[0], filter(
        lambda movie: movie[1]['rating'] == ratings[0], sorted_movies)))

    worst_movies = list(map(lambda movie: movie[0], filter(
        lambda movie: movie[1]['rating'] == ratings[-1], sorted_movies)))

    views.display_movie_stats(
        (average_rating, median_rating, best_movies, worst_movies)
    )


def random_movie() -> None:
    """Pick and display a random movie from the current collection."""
    movies = storage.list_movies()
    rnd_movie = random.choice(movies)
    title, movie_data = rnd_movie
    views.display_random_movie(title, movie_data['rating'])


def search_movie() -> None:
    """
    Search stored movies by substring with fuzzy fallbacks.

    If literal substring search yields no results, computes fuzzy suggestions
    via Levenshtein ratio using the configured threshold and displays those.
    """
    movies = storage.list_movies()
    search_results = []
    search_term = utils.colored_input("Enter part of movie name:", True)
    for title, data in movies:
        if search_term.lower() in title.lower():
            search_results.append((title, data))

    if search_results:
        views.display_movie_list(search_results, show_total=False)
    else:
        suggestions = utils.compute_suggestions(search_term, movies)
        highlighted_search_term = f"{utils.COLORS['MOVIE_TITLE']}" \
                                  f"{search_term}"
        if suggestions:
            utils.colored_print(
                f"The movie {highlighted_search_term}{utils.COLORS['INFO']} "
                "doesn't exist. Did you mean:", "INFO"
            )
            views.display_movie_list(suggestions, show_total=False)
        else:
            utils.colored_print(
                f"The movie {highlighted_search_term}{utils.COLORS['ERROR']} "
                "doesn't exist.", "ERROR")
    print()


def filter_movies() -> None:
    """
    Filter stored movies by optional rating and year bounds.

    Interactively collects:
      * minimum rating,
      * start year (inclusive),
      * end year (inclusive).

    Blank input is treated as "no constraint". Matching movies are displayed.
    """
    movies = storage.list_movies()
    current_year = datetime.now().year
    min_rating = utils.get_valid_number(
        "Enter minimum rating (leave blank for no minimum rating):",
        num_type=float,
        with_range=True,
        display_range=False,
        allow_empty=True
    )

    start_year = utils.get_valid_number(
        "Enter start year (leave blank for no start year):",
        with_range=True,
        display_range=False,
        num_range=(MIN_YEAR, current_year),
        allow_empty=True
    )

    end_year = utils.get_valid_number(
        "Enter end year (leave blank for no end year):",
        with_range=True,
        display_range=False,
        num_range=(MIN_YEAR, current_year),
        allow_empty=True
    )

    if min_rating:
        movies = filter(
            lambda movie: utils.filter_by_rating(movie, min_rating),
            movies
        )

    if start_year:
        movies = filter(
            lambda movie: utils.filter_by_year(movie, start_year),
            movies
        )

    if end_year:
        movies = filter(
            lambda movie: utils.filter_by_year(movie, end_year, 'end'),
            movies
        )

    views.display_movie_list(movies)


def movies_by_rating() -> None:
    """Display all movies sorted by rating (descending)."""
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

    Asks the user whether to show newest first or oldest first, then prints
    the list accordingly.
    """
    user_choices = ["First", "Last"]
    movies = storage.list_movies()
    views.display_menu(user_choices, "Choose order of latest movies")
    user_choice = utils.get_valid_number(
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
    Create and save a histogram of all movie ratings.

    Prompts for an output filename, builds a Matplotlib histogram from the
    current user's ratings and saves it with ``plt.savefig(<filename>)``.

    Notes:
        The function prints a validation error if the filename is empty.
    """
    file_name = utils.colored_input(
        "In which file do you want to save the histogram?:"
        f"{utils.COLORS['RESET']}\n", extra_whitespace=False)

    if file_name != "":
        movies = storage.list_movies()
        ratings = [data['rating'] for name, data in movies]
        plt.hist(ratings)
        plt.savefig(f"{file_name}")
    else:
        utils.colored_print("File name can't be empty!", "ERROR")
    print()


def generate_website() -> None:
    """
    Generate a static HTML page listing all movies.

    Reads the template at ``static/index_template.html``, replaces placeholders
    with the configured title and a generated movie grid, and writes the file
    as ``static/<username>.html``.

    Side Effects:
        Reads and writes files under the ``static`` directory and prints
        user-facing status messages.
    """
    try:
        with open("static/index_template.html", "r") as file_obj:
            template = file_obj.read()
    except FileNotFoundError:
        utils.colored_print(
            "Template file 'static/index_template.html' not found!",
            "ERROR", True)
    else:
        app_title = os.getenv("APP_TITLE")
        movies_grid = utils.create_movies_grid()
        template = template.replace("__TEMPLATE_TITLE__", app_title)
        template = template.replace("__TEMPLATE_MOVIE_GRID__", movies_grid)

        *_, username = utils.get_current_user()
        with open(f"static/{username}.html", "w") as file_obj:
            file_obj.write(template)
            utils.colored_print(
                "Website was generated successfully.", "SUCCESS", True)


def start_app() -> None:
    """
    Enter the main application loop.

    Displays the menu, processes commands for the current user, or shows the
    user selection screen if no user is logged in.
    """
    while True:
        if utils.get_current_user():
            views.display_menu(COMMANDS)
            user_cmd, *_ = get_user_choice()

            user_cmd()
            utils.colored_input("Press enter to continue")
            print()
        else:
            users = storage.get_users()
            views.display_select_user(users)
            utils.select_user(users)


def exit_app() -> None:
    """
    Exit the application after printing a goodbye message.

    This function terminates the process with ``sys.exit(0)``.
    """
    utils.colored_print("Good bye!", "HIGHLIGHT")
    sys.exit(0)


# COMMANDS maps menu labels to (callable, description) tuples consumed by the UI.
COMMANDS: dict[str, utils.CLICommand] = {
    "Exit App": (
        exit_app,
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
    ),
    "Switch user": (
        utils.logout_user,
        "Logout of the current user and turn back to user profiles view "
        "to allow profile switching."
    )
}
