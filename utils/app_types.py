from typing import Any, Callable, Literal

CLIFunction = Callable[..., Any]
CLIDescription = str
CLICommand = tuple[CLIFunction, CLIDescription]

MoviesCollection = list[tuple[str, dict[str, Any]]]
SearchResults = MoviesCollection
NumRange = tuple[int, int]
NumType = Callable[[str], int] | Callable[[str], float]
YearType = Literal["start", "end"]
