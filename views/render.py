"""
Console rendering helpers for the Movies Database CLI.

Functions in this module are pure view concerns: they print formatted text
to the terminal based on domain data passed in from commands.
"""
import os
from typing import Any
from dotenv import load_dotenv
from sqlalchemy import Row

import utils
from utils import CLICommand, COLORS, colored_print, MoviesCollection, get_user_menu
load_dotenv()


def display_welcome_message() -> None:
    """Print a generic welcome banner for the application."""
    colored_print("Welcome to the Movie App! 🎬", "TITLE", True)


def display_menu(
    items: dict[str, CLICommand] | list[str] | list[Row[Any]],
    label: str = "Menu"
) -> None:
    """
    Display a labeled, indexed list of menu items.

    Args:
        items: Either a mapping of command labels to command tuples, or a list
            of plain strings/rows to render.
        label: Heading shown above the list.

    Notes:
        This function writes directly to stdout.
    """
    colored_print(f"{label}:", "MENU")
    for item_num, item_text in enumerate(items):
        colored_print(f"{item_num}. {COLORS['MENU_ITEM']}{item_text}")
    print()


def display_movie_stats(movie_stats) -> None:
    """
    Print aggregate statistics for the current movie collection.

    Args:
        movie_stats: A 4-tuple ``(average, median, best_titles, worst_titles)``.
    """
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
    """Print a one-line suggestion for a randomly chosen movie."""
    movie_str = f"{COLORS['MOVIE_TITLE']}{title}{COLORS['INFO']}"
    movie_rating = f"{COLORS['RATING']}{rating:.2f}"

    colored_print(f"Your movie for tonight: {movie_str}, "
                  f"it's rated with {movie_rating}", "INFO", True)


def display_movie_list(
    movies: MoviesCollection,
    show_total: bool = True,
    show_release_years: bool = False
) -> None:
    """
    Print a list of movies with rating (and optionally the release year).

    Args:
        movies: Sequence of ``(title, data)`` pairs.
        show_total: If True, prints a header with the number of movies.
        show_release_years: If True, includes the year after the title.

    Notes:
        Purely presentational; no return value.
    """
    *_, username = utils.get_current_user()
    if show_total:
        if movies:
            colored_print(f"{username}, you've {COLORS['HIGHLIGHT']}"
                          f"{len(movies)} movies {COLORS['INFO']}in your "
                          "collection:", "INFO", True)
        else:
            colored_print(f"{username}, your {COLORS['HIGHLIGHT']}movie collection"
                          f" is empty{COLORS['INFO']}. Add some movies!", "INFO")

    for title, data in movies.items():
        rating, year = data['rating'], data['year']
        release_year = f" ({year})" if show_release_years else ""
        movie_note = "Empty" if data['note'] is None else data['note']

        colored_print(f"- {COLORS['MOVIE_TITLE']}{title}{release_year}:"
                      f" {COLORS['RATING']}{rating:.2f}\n"
                      f"  {COLORS['NOTE']}Note: {movie_note}\n")

    print()


def display_select_user(users) -> None:
    """Render the user selection screen and its menu."""
    menu_items, *_ = get_user_menu(users)
    display_welcome_message()
    display_menu(menu_items, "Select a user")
