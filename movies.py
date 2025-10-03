from datetime import datetime
import random
import sys

import Levenshtein
import matplotlib.pyplot as plt

import movie_storage_sql as storage
from utils import colored_input, colored_print, COLORS, get_valid_number
from app_types import CLICommand, SearchResults, YearType

APP_TITLE = "My Movies Database"
APP_DATABASE = "data.json"
MIN_YEAR = 1888
SEARCH_THRESHOLD = 0.6


def display_app_title(app_title: str) -> None:
    """
    Display the application title centered and styled.

    Centers the given title within 40 characters using asterisks and
    prints it with the "TITLE" color, followed by a blank line.

    Args:
        app_title (str): The application's title to display.

    Returns:
        None
    """
    colored_print(f" {app_title} ".center(40, '*'), "TITLE", True)


def display_menu(
    menu: dict[str, CLICommand] | list[str],
    prompt: str = "Menu"
) -> None:
    """
    Display a menu and its indexed options.

    Prints each entry of the provided ``menu`` (a list of labels or the keys of a
    command dictionary) with its numeric index under the given ``prompt`` header.

    Args:
        menu (dict[str, CLICommand] | list[str]): The items to display.
        prompt (str, optional): Heading shown above the list. Defaults to "Menu".

    Returns:
        None
    """
    colored_print(f"{prompt}:", "MENU")
    for idx, option in enumerate(menu):
        colored_print(f"{idx}. {COLORS['MENU_ITEM']}{option}", "MENU")
    print()


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
    colored_print(
        f"{len(movies)} movies {COLORS['INFO']}in total", "HIGHLIGHT")

    for movie_name, movie_data in movies.items():
        rating, year = movie_data['rating'], movie_data['year']
        colored_print(f"- {COLORS['MOVIE_TITLE']}{movie_name} ({year}):"
                      f" {COLORS['RATING']}{rating:.2f}")
    print()


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

    current_year = datetime.now().year
    new_movie_rating = get_valid_number(
        "Enter new movie rating:",
        num_type=float,
        with_range=True
    )
    new_movie_year = get_valid_number(
        "Enter the year of release:",
        with_range=True,
        display_range=False,
        num_range=(MIN_YEAR, current_year)
    )

    storage.add_movie(
        title=movie_name,
        year=new_movie_year,
        rating=round(new_movie_rating, 2)
    )


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

    if movie_name in movies:
        new_movie_rating = get_valid_number("Enter new rating:", float, True)
        storage.update_movie(movie_name, new_movie_rating)
    else:
        colored_print(f"Movie {movie_name} doesn't exist!", "ERROR", True)


def is_even(collection: list) -> bool:
    """
    Return True if the length of the collection is even.

    Args:
        collection (list): The sequence to check.

    Returns:
        bool: True if ``len(collection)`` is even, False otherwise.
    """
    return len(collection) % 2 == 0


def calc_median_rating(ratings: list[float]) -> float:
    """
    Compute the median of a list of ratings.

    Sorts the ratings; for an even count returns the mean of the two
    middle values, otherwise returns the middle value.

    Args:
        ratings (list[float]): List of movie ratings.

    Returns:
        float: The median rating.
    """
    sorted_rankings = sorted(ratings)

    if is_even(sorted_rankings):
        rating_index = len(sorted_rankings) // 2 - 1
        mid_values = (sorted_rankings[rating_index]
                      + sorted_rankings[rating_index + 1])
        return mid_values / 2

    rating_index = len(sorted_rankings) // 2
    return sorted_rankings[rating_index]


def display_movie_stats() -> None:
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
    delimiter = f"{COLORS['RESET']}, {COLORS['RATING']}"

    colored_print(
        f"Average rating: {COLORS['RATING']}{average_rating:.1f}",
        "STAT_TITLE"
    )
    colored_print(
        f"Median rating: {COLORS['RATING']}{median_rating:.1f}",
        "STAT_TITLE"
    )
    colored_print(
        f"Best movie(s): {COLORS['RATING']}{delimiter.join(best_movies)}",
        "STAT_TITLE"
    )
    colored_print(
        f"Worst movie(s): {COLORS['RATING']}{delimiter.join(worst_movies)}",
        "STAT_TITLE",
        True
    )


def display_random_movie() -> None:
    """
    Display a random movie suggestion.

    Randomly selects a stored movie and prints its title and rating.

    Returns:
        None
    """
    movies = storage.list_movies()
    movie_names = list(map(lambda movie: movie, movies))
    rnd_movie = random.choice(movie_names)

    movie_str = f"{COLORS['MOVIE_TITLE']}{rnd_movie}{COLORS['INFO']}"
    movie_rating = f"{COLORS['RATING']}{movies[rnd_movie]['rating']:.2f}"

    colored_print(
        f"Your movie for tonight: {movie_str}, "
        f"it's rated with {movie_rating}", "INFO", True)


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
    search_results: SearchResults = {}
    search_term = colored_input("Enter part of movie name:", True)
    for name, data in movies.items():
        if search_term.lower() in name.lower():
            search_results[name] = data

    if search_results:
        display_search_results(search_results)
    else:
        suggestions = compute_suggestions(search_term)

        if suggestions:
            highlighted_search_term = f"{COLORS['MOVIE_TITLE']}"\
                                      f"{search_term}{COLORS['INFO']}"
            colored_print(
                f"The movie {highlighted_search_term} doesn't exist. "
                "Did you mean:", "INFO"
            )
            display_search_results(suggestions)
        else:
            highlighted_search_term = f"{COLORS['MOVIE_TITLE']}"\
                                      f"{search_term}{COLORS['ERROR']}"
            colored_print(
                f"The movie {highlighted_search_term} doesn't exist.", "ERROR")
    print()


def filter_by_rating(movie, min_rating: float) -> bool:
    """
    Return True if the movie's rating meets the minimum threshold.

    Expects a ``(title, data)`` pair as yielded by ``dict.items()``,
    where ``data`` contains a ``'rating'`` key.

    Args:
        movie (tuple[str, dict]): A (title, data) pair from the movies mapping.
        min_rating (float): Inclusive lower bound for the rating.

    Returns:
        bool: True if ``data['rating'] >= min_rating``, otherwise False.
    """
    title, data = movie
    if data['rating'] >= min_rating:
        return True

    return False


def filter_by_year(movie, year: int, year_type: YearType = 'start') -> bool:
    """
    Return True if the movie's year satisfies the given bound.

    When ``year_type`` is ``'start'``, the movie passes if its year is
    greater than or equal to ``year`` (lower bound). When ``year_type``
    is ``'end'``, the movie passes if its year is less than or equal to
    ``year`` (upper bound).

    Args:
        movie (tuple[str, dict]): A (title, data) pair from
            the movies mapping.
        year (int): The boundary year to compare against.
        year_type (YearType, optional): ``'start'`` for a lower bound
            (``>= year``) or ``'end'`` for an upper bound (``<= year``).
            Defaults to ``'start'``.

    Returns:
        bool: True if the movie satisfies the specified bound,
            otherwise False.
    """
    title, data = movie
    if year_type == 'start':
        if data['year'] >= year:
            return True
    else:
        if data['year'] <= year:
            return True

    return False


def get_filtered_movies():
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
        movies = dict(filter(
            lambda movie_data: filter_by_rating(movie_data, min_rating),
            movies.items()
        ))

    if start_year:
        movies = dict(filter(
            lambda movie_data: filter_by_year(movie_data, start_year),
            movies.items()
        ))

    if end_year:
        movies = dict(filter(
            lambda movie_data: filter_by_year(movie_data, end_year, 'end'),
            movies.items()
        ))

    return movies


def display_filtered_movies() -> None:
    """
    Display movies that match the current filter criteria.

    Obtains the filtered collection via ``get_filtered_movies()``,
    prints the total count, and lists each entry as
    ``"Title (Year): Rating"`` with formatting.

    Returns:
        None
    """
    filtered_movies = get_filtered_movies()
    colored_print(
        f"{len(filtered_movies)} movies {COLORS['INFO']}in total", "HIGHLIGHT")

    for title, movie_data in filtered_movies.items():
        rating, year = movie_data['rating'], movie_data['year']
        colored_print(f"- {COLORS['MOVIE_TITLE']}{title} ({year}):"
                      f" {COLORS['RATING']}{rating:.2f}")
    print()


def compute_suggestions(
    search_term: str
) -> SearchResults:
    """
    Compute fuzzy movie title suggestions for a search term.

    Splits each stored title into lowercase tokens and uses
    ``Levenshtein.ratio`` with ``score_cutoff=SEARCH_THRESHOLD`` to test
    similarity against the search term. If any token meets the threshold,
    the movie is included.

    Args:
        search_term (str): The user's search term.

    Returns:
        SearchResults: A dictionary of suggested movies keyed by title.
    """
    movies = storage.list_movies()
    computed_suggestions: SearchResults = {}
    for name, data in movies.items():
        tokens = name.lower().split()
        for word in tokens:
            ratio = Levenshtein.ratio(
                search_term, word.strip(':'), score_cutoff=SEARCH_THRESHOLD
            )
            if ratio > 0:
                computed_suggestions[name] = data
                break

    return computed_suggestions


def display_search_results(search_results: SearchResults) -> None:
    """
    Display a list of search results.

    Args:
        search_results (SearchResults): Mapping of movie titles to their data.

    Returns:
        None
    """
    for name, data in search_results.items():
        colored_print(
            f"- {COLORS['MOVIE_TITLE']}{name}{COLORS['RESET']}, "
            f"{COLORS['RATING']}{data['rating']:.2f}"
        )


def display_movies_by_rating() -> None:
    """
    Display all movies sorted by rating (descending).

    Returns:
        None
    """
    movies = storage.list_movies()
    sorted_movies = sorted(
        movies.keys(),
        key=lambda movie: movies[movie]['rating'],
        reverse=True
    )

    for movie in sorted_movies:
        colored_print(
            f"- {COLORS['MOVIE_TITLE']}{movie}{COLORS['RESET']}, "
            f"{COLORS['RATING']}{movies[movie]['rating']:.2f}"
        )
    print()


def display_movies_by_year() -> None:
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
    display_menu(user_choices, "Choose order of latest movies")
    user_choice = get_valid_number(
        "Enter choice:",
        with_range=True,
        num_range=(0, len(user_choices) - 1)
    )

    sorted_movies = sorted(
        movies.keys(),
        key=lambda movie: movies[movie]['year'],
        reverse=True if user_choice == 0 else False
    )

    for movie_name in sorted_movies:
        rating, year = movies[movie_name]['rating'], movies[movie_name]['year']
        colored_print(f"- {COLORS['MOVIE_TITLE']}{movie_name} ({year}):"
                      f" {COLORS['RATING']}{rating:.2f}")
    print()


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
        ratings = [data['rating'] for name, data in movies.items()]
        plt.hist(ratings)
        plt.savefig(f"{file_name}")
    else:
        colored_print("File name can't be empty!", "ERROR")
    print()


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
    display_app_title(APP_TITLE)
    while True:
        display_menu(COMMANDS)
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
        display_movie_stats,
        "Displays average stats for each movie stored in applications "
        "database."
    ),
    "Random Movie": (
        display_random_movie,
        "Displays a random movie stored in applications database."
    ),
    "Search Movie": (
        search_movie,
        "Searches for movies in applications database by search term "
        "that is given by user input."
    ),
    "Filter Movies": (
        display_filtered_movies,
        "Let users filter movies based on specific criteria such as "
        "minimum rating, start year, and end year."
    ),
    "Movies sorted by rating": (
        display_movies_by_rating,
        "Displays movies by their corresponding rating."
    ),
    "Movies sorted by release year": (
        display_movies_by_year,
        "Displays each movie in a chronological order chosen by user."
    ),
    "Create rating histogram": (
        create_rating_histogram,
        "Create a movie rating histogram and store it as file."
    ),
}


def main() -> None:
    """
    Entry point of the movie application.

    Delegates to ``start_movie_app()`` to run the interactive loop.
    This function does not load data or perform I/O beyond invoking the
    application start.

    Returns:
        None
    """
    start_movie_app()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n")
        exit_movie_app()
