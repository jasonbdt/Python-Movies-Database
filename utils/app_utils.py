"""
Utility functions for console I/O, validation, and simple computations.

This module centralizes:
- colored console input/output,
- numeric input validation,
- basic statistics helpers,
- fuzzy search helpers,
- current-user handling for the CLI,
- small HTML grid generation used by the static site generator.
"""
from typing import Any
import sys

import colorama
import Levenshtein

import movie_storage as storage
from utils.app_types import NumType, NumRange, YearType, MoviesCollection

COLORS = {
    "ERROR": colorama.Fore.RED,
    "TITLE": colorama.Fore.LIGHTMAGENTA_EX,
    "HIGHLIGHT": colorama.Fore.LIGHTBLUE_EX,
    "MOVIE_TITLE": colorama.Fore.LIGHTCYAN_EX,
    "STAT_TITLE": colorama.Fore.LIGHTCYAN_EX,
    "INFO": colorama.Fore.LIGHTGREEN_EX,
    "MENU": colorama.Fore.LIGHTYELLOW_EX,
    "NOTE": colorama.Fore.LIGHTMAGENTA_EX,
    "RATING": colorama.Fore.LIGHTYELLOW_EX,
    "MENU_ITEM": colorama.Fore.LIGHTCYAN_EX,
    "SUCCESS": colorama.Back.GREEN + colorama.Fore.LIGHTWHITE_EX,
    "USER_INPUT": colorama.Back.YELLOW + colorama.Fore.BLACK,
    "RESET": colorama.Style.RESET_ALL,
    "DEFAULT": colorama.Fore.WHITE
}
SEARCH_THRESHOLD = 0.6


__current_user: tuple[int, str] | None = None

def calc_median_rating(ratings: list[float]) -> float:
    """
    Return the median of a non-empty list of ratings.

    For even-sized lists, returns the mean of the two middle values; for
    odd-sized lists, returns the middle value.

    Args:
        ratings: Non-empty list of numeric ratings.

    Returns:
        float: The median rating.

    Raises:
        ValueError: If ``ratings`` is empty.
    """
    sorted_rankings = sorted(ratings)

    if is_even(sorted_rankings):
        rating_index = len(sorted_rankings) // 2 - 1
        mid_values = (sorted_rankings[rating_index]
                      + sorted_rankings[rating_index + 1])
        return mid_values / 2

    rating_index = len(sorted_rankings) // 2
    return sorted_rankings[rating_index]


def colored_input(
    msg: str,
    extra_break: bool = False,
    extra_whitespace: bool = True
) -> str:
    """
    Prompt the user and return the raw input string with styled prompt.

    Args:
        msg: The message displayed to the user.
        extra_break: If True, print an extra newline after reading input.
        extra_whitespace: If True, append a trailing space to the prompt.

    Returns:
        str: The user input as typed.
    """
    whitespace = " " if extra_whitespace else ""
    result = input(
        f"{COLORS['USER_INPUT']} {msg} {COLORS['RESET']}{whitespace}"
    )
    if extra_break:
        print()

    return result


def colored_print(
    msg: str,
    color: str = "DEFAULT",
    extra_break: bool = False
) -> None:
    """
    Print a message using the configured ANSI color palette.

    Args:
        msg: The message to print.
        color: Key into the global ``COLORS`` palette.
        extra_break: If True, append an extra newline after printing.
    """
    whitespace = " " if color == "SUCCESS" else ""
    print(
        f"{COLORS[color]}{whitespace}"
        f"{msg}{whitespace}{COLORS['RESET']}"
    )
    if extra_break:
        print()


def compute_suggestions(
    search_term: str,
    movies: list[tuple[str, dict[str, Any]]]
) -> MoviesCollection:
    """
    Return fuzzy title suggestions for a search term.

    Splits each title into tokens and tests similarity with
    ``Levenshtein.ratio`` using ``score_cutoff=SEARCH_THRESHOLD``. If any token
    meets the cutoff for a given title, that title is included.

    Args:
        search_term: The user-provided query.
        movies: The (title, data) pairs to test.

    Returns:
        MoviesCollection: A list of ``(title, data)`` suggestions.
    """
    computed_suggestions = []
    for title, data in movies:
        tokens = title.lower().split()
        for word in tokens:
            ratio = Levenshtein.ratio(
                search_term, word.strip(':'), score_cutoff=SEARCH_THRESHOLD
            )
            if ratio > 0:
                computed_suggestions.append((title, data))
                break

    return computed_suggestions


def create_movies_grid() -> str:
    """
    Build the HTML snippet used to render the movies grid in the template.

    Returns:
        str: A concatenated HTML fragment (no surrounding `<html>`).
    """
    output = ""
    for title, data in storage.list_movies():
        note = "" if data['note'] is None else f"title='{data['note']}'"
        output += f"""<li><div class='movie'>
          <a href='https://www.imdb.com/title/{data['imdb_id']}/' target='_blank'>
            <img class='movie-poster' src='{data['poster']}' {note}/>
          </a>
          <div class='movie-title'>
            {title}
            <img src="https://flagsapi.com/{data['country_iso2']}/shiny/64.png" />
          </div>
          <div class='movie-year'>{data['year']}</div>
          <div class='movie-rating'>
            <span>Rated:</span> {data['rating']}
            <span class="fa fa-star checked"></span>
          </div>
        </div></li>"""

    return output


def is_even(collection: list) -> bool:
    """
    Return True if the collection length is even, False otherwise.

    Args:
        collection: Any sequence with a defined length.

    Returns:
        bool: Whether ``len(collection) % 2 == 0``.
    """
    return len(collection) % 2 == 0


def get_valid_number(
    prompt: str,
    num_type: NumType = int,
    with_range: bool = False,
    display_range: bool = True,
    num_range: NumRange = (0, 10),
    allow_empty: bool = False
) -> int | float | None:
    """
    Prompt until a valid numeric input (or empty if allowed) is provided.

    Converts the input to ``num_type`` and optionally enforces a closed
    interval constraint.

    Args:
        prompt: Message shown to the user.
        num_type: Target cast type (``int`` or ``float``).
        with_range: If True, enforce the ``num_range`` constraint.
        display_range: If True, append the range to the prompt text.
        num_range: Inclusive ``(min, max)`` bounds when ``with_range`` is True.
        allow_empty: If True, return ``None`` for a blank input.

    Returns:
        int | float | None: The parsed number, or ``None`` when blank input is
        allowed and provided.

    Notes:
        Invalid inputs are re-prompted without raising.
    """
    while True:
        if with_range:
            has_range = f"({num_range[0]}-{num_range[1]})" in prompt
            if display_range and not has_range:
                if prompt[-1] == ':':
                    prompt = f"{prompt[:-1]} ({num_range[0]}-{num_range[1]}):"
                else:
                    prompt = f"{prompt} ({num_range[0]}-{num_range[1]}):"

        try:
            user_input = colored_input(prompt, True)
            if allow_empty and user_input == "":
                return None
            else:
                user_input = num_type(user_input)
        except ValueError:
            pass
        else:
            if with_range:
                if allow_empty and user_input == "":
                    return None

                if num_range[0] <= user_input <= num_range[1]:
                    return user_input

                print(f"{COLORS['ERROR']}Invalid choice, "
                      "please enter a digit between "
                      f"{num_range[0]}-{num_range[1]}.\n")
            else:
                return user_input


def filter_by_rating(movie, min_rating: float) -> bool:
    """
    Return True if the movie's rating is at least ``min_rating``.

    Args:
        movie: A ``(title, data)`` pair where ``data['rating']`` is a float.
        min_rating: Inclusive lower bound for the rating.

    Returns:
        bool: True if the rating passes, otherwise False.
    """
    title, data = movie
    if data['rating'] >= min_rating:
        return True

    return False


def filter_by_year(movie, year: int, year_type: YearType = 'start') -> bool:
    """
    Return True if the movie's year satisfies the specified bound.

    Args:
        movie: A ``(title, data)`` pair where ``data['year']`` is an int.
        year: The comparison year.
        year_type: ``'start'`` for ``>= year`` (lower bound) or ``'end'`` for
            ``<= year`` (upper bound).

    Returns:
        bool: True if the movie passes the bound, otherwise False.
    """
    title, data = movie
    if year_type == 'start':
        if data['year'] >= year:
            return True
    else:
        if data['year'] <= year:
            return True

    return False


def get_user_menu(users):
    """
    Return the menu labels for the user selector and the index of 'create'.

    Args:
        users: Sequence of ``(id, name)`` tuples.

    Returns:
        tuple[list[str], int]: A pair of (menu labels, index of "Create new user").
    """
    users_str = list(map(lambda user: user[1], users))
    users_str.append("Create new user")

    return users_str, len(users_str)-1


def select_user(users) -> None:
    """
    Prompt the user to select an existing profile or create a new one.

    On blank input, exits the application gracefully. On "create", prompts for
    a name and persists a new user; otherwise selects the chosen existing user.
    """
    *_, last_item_idx = get_user_menu(users)
    user_id = get_valid_number("Enter choice (or leave blank to exit app)",
                                with_range=True,
                                num_range=(0, last_item_idx),
                                allow_empty=True)

    if user_id is None:
        colored_print("Good bye!", "HIGHLIGHT")
        sys.exit(0)

    if user_id == last_item_idx:
        username = colored_input("Enter your name (e.g. Max): ")
        storage.add_user(username)
    else:
        set_current_user(users[user_id])


def get_current_user() -> tuple[int, str]:
    """Return the current user as ``(id, name)`` or ``None`` if not set."""
    return __current_user


def set_current_user(user: tuple[int, str] | None) -> None:
    """
    Set the current user used by the CLI session.

    Args:
        user: ``(id, name)`` tuple or ``None`` to clear.
    """
    global __current_user
    __current_user = user


def logout_user() -> None:
    """Clear the current user and print a confirmation message."""
    set_current_user(None)
    colored_print("Logged out successfully!", "SUCCESS", True)
