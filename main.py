"""Entry point for the Movies Database CLI application."""

import movies


def main() -> None:
    """
    Run the interactive CLI application.

    Delegates to `movies.start_app` to enter the main command loop.
    """
    movies.start_app()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Graceful exit on Ctrl+C
        print("\n")
        movies.exit_app()
