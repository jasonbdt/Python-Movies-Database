import os
from typing import Any
from dotenv import load_dotenv
from utils import (CLICommand, COLORS, colored_print, MovieCollection,
                   SearchResults)
load_dotenv()

def display_app_title() -> None:
    title = os.getenv("APP_TITLE")
    colored_print(f" {title} ".center(40, "*"), "TITLE", True)


def display_menu(
    items: dict[str, CLICommand] | list[str],
    label: str = "Menu"
) -> None:
    """
    Display a menu and its indexed options.

    Prints each entry of the provided ``menu`` (a list of labels or the keys of a
    command dictionary) with its numeric index under the given ``prompt`` header.

    Args:
        items (dict[str, CLICommand] | list[str]): The items to display.
        label (str, optional): Heading shown above the list. Defaults to "Menu".

    Returns:
        None
    """
    colored_print(f"{label}:", "MENU")
    for item_num, item_text in enumerate(items):
        colored_print(f"{item_num}. {COLORS['MENU_ITEM']}{item_text}")
    print()


def display_movie_stats(movie_stats) -> None:
    avg_rating, median_rating, best_movies, worst_movies = movie_stats
    delimiter = f"{COLORS['RESET']}, {COLORS['RATING']}"

    colored_print(
        f"Average rating: {COLORS['RATING']}{avg_rating:.1f}",
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


def display_random_movie(title: str, rating: float) -> None:
    movie_str = f"{COLORS['MOVIE_TITLE']}{title}{COLORS['INFO']}"
    movie_rating = f"{COLORS['RATING']}{rating:.2f}"

    colored_print(f"Your movie for tonight: {movie_str}, "
                  f"it's rated with {movie_rating}", "INFO", True)


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


def display_filtered_movies(movies: MovieCollection) -> None:
    """
    Display movies that match the current filter criteria.

    Obtains the filtered collection via ``get_filtered_movies()``,
    prints the total count, and lists each entry as
    ``"Title (Year): Rating"`` with formatting.

    Returns:
        None
    """
    colored_print(
        f"{len(movies)} movies {COLORS['INFO']}in total", "HIGHLIGHT")

    for title, movie_data in movies.items():
        rating, year = movie_data['rating'], movie_data['year']
        colored_print(f"- {COLORS['MOVIE_TITLE']}{title} ({year}):"
                      f" {COLORS['RATING']}{rating:.2f}")
    print()


def display_movies_by_rating(movies: list[tuple[str, dict[str, Any]]]) -> None:
    for title, data in movies:
        colored_print(
            f"- {COLORS['MOVIE_TITLE']}{title}{COLORS['RESET']}, "
            f"{COLORS['RATING']}{data['rating']:.2f}"
        )
    print()


def display_movies_by_year(movies: list[tuple[str, dict[str, Any]]]) -> None:
    for title, data in movies:
        colored_print(
            f"- {COLORS['MOVIE_TITLE']}{title} ({data['year']}): "
            f"{COLORS['RATING']}{data['rating']:.2f}")
    print()
