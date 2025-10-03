import colorama
from app_types import NumType, NumRange

COLORS = {
    "ERROR": colorama.Fore.RED,
    "TITLE": colorama.Fore.LIGHTMAGENTA_EX,
    "HIGHLIGHT": colorama.Fore.LIGHTBLUE_EX,
    "MOVIE_TITLE": colorama.Fore.LIGHTCYAN_EX,
    "STAT_TITLE": colorama.Fore.LIGHTCYAN_EX,
    "INFO": colorama.Fore.LIGHTGREEN_EX,
    "MENU": colorama.Fore.LIGHTYELLOW_EX,
    "RATING": colorama.Fore.LIGHTYELLOW_EX,
    "MENU_ITEM": colorama.Fore.LIGHTCYAN_EX,
    "SUCCESS": colorama.Back.GREEN + colorama.Fore.LIGHTWHITE_EX,
    "USER_INPUT": colorama.Back.YELLOW + colorama.Fore.BLACK,
    "RESET": colorama.Style.RESET_ALL,
    "DEFAULT": colorama.Fore.WHITE
}

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
