"""
Typed aliases for the CLI application.

Centralizes callable signatures and common collection shapes used across the
UI and command layers.
"""
from typing import Any, Callable, Literal

CLIFunction = Callable[..., Any]
CLIDescription = str
CLICommand = tuple[CLIFunction, CLIDescription]

MoviesCollection = list[tuple[str, dict[str, Any]]]
NumRange = tuple[int, int]
NumType = Callable[[str], int] | Callable[[str], float]
YearType = Literal["start", "end"]
