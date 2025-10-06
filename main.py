import movies

def main() -> None:
    movies.start_app()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n")
        movies.exit_app()
