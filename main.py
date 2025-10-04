from movies import start_movie_app, exit_movie_app


def main() -> None:
    start_movie_app()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n")
        exit_movie_app()
