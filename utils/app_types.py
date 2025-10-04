from typing import Any, Callable, Literal

CLIFunction = Callable[..., Any]
CLIDescription = str
CLICommand = tuple[CLIFunction, CLIDescription]

MovieCollection = dict[str, dict[str, float | int]]
SearchResults = MovieCollection
NumRange = tuple[int, int]
NumType = Callable[[str], int] | Callable[[str], float]
YearType = Literal["start", "end"]
