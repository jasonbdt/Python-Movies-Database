from typing import Any
import sys

import colorama
import Levenshtein

import movie_storage as storage
# from views import display_welcome_message, display_menu
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


def colored_input(
    msg: str,
    extra_break: bool = False,
    extra_whitespace: bool = True
) -> str:
    """
    Prompt the user for input with colored text.

    The prompt message is wrapped in the ANSI color code for
    ``USER_INPUT`` from the global ``COLORS`` dictionary. An
    optional trailing whitespace can be added for readability,
    and an extra newline can be printed after the input.

    Args:
        msg (str): The prompt message displayed to the user.
        extra_break (bool, optional): If True, prints an extra
            newline after the input. Defaults to False.
        extra_whitespace (bool, optional): If True, appends a
            trailing space to the prompt. Defaults to True.

    Returns:
        str: The user input as a string.
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
    Print a message with the given color.

    The message is wrapped in the specified ANSI color code from the
    global ``COLORS`` dictionary. If ``color`` is set to "SUCCESS",
    the message is padded with a leading and trailing space. After
    printing, an additional line break is added if ``extra_break``
    is True.

    Args:
        msg (str): The message text to print.
        color (str, optional): The color key from ``COLORS``. Defaults
            to "DEFAULT".
        extra_break (bool, optional): If True, adds an extra newline
            after the message. Defaults to False.

    Returns:
        None
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
    computed_suggestions: SearchResults = []
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
    output = ""
    for title, data in storage.list_movies():
        output += f"""<li><div class='movie'>
          <img class='movie-poster' src='{data['poster']}' title='{data['note']}' />
          <div class='movie-title'>{title}</div>
          <div class='movie-year'>{data['year']}</div>
        </div></li>"""

    return output


def is_even(collection: list) -> bool:
    """
    Return True if the length of the collection is even.

    Args:
        collection (list): The sequence to check.

    Returns:
        bool: True if ``len(collection)`` is even, False otherwise.
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
    Prompt the user for a number until a valid input is provided.

    The input is repeatedly requested until it can be cast to
    ``num_type``. If ``with_range`` is True, the input must lie
    within the given numeric range.

    Args:
        prompt (str): The message displayed to the user.
        num_type (NumType, optional): The target type of the number
            (``int`` or ``float``). Defaults to ``int``.
        with_range (bool, optional): If True, restricts the input to
            ``num_range``. Defaults to False.
        display_range (bool, optional): If True, appends the range to
            the prompt message (e.g. "Enter a number (0-10):").
            Defaults to True.
        num_range (NumRange, optional): A tuple ``(min, max)`` defining
            the valid range. Defaults to ``(0, 10)``.
        allow_empty (bool, optional): If True, user can leave the
            input empty without getting repeatedly requested.

    Returns:
        int | float | None: The validated user input.
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
                pass
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


def get_user_menu(users):
    users_str = list(map(lambda user: user[1], users))
    users_str.append("Create new user")

    return users_str, len(users_str)-1


def select_user(users) -> None:
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
    return __current_user


def set_current_user(user: tuple[int, str] | None) -> None:
    global __current_user
    __current_user = user


def logout_user() -> None:
    set_current_user(None)
    colored_print("Logged out successfully!", "SUCCESS", True)
