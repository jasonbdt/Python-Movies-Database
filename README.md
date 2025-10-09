# 🎬 Python Movies Database

A command-line application for managing personal movie collections —  
add, delete, search, and analyze your favorite movies directly from the terminal.

This project was built to practice Python fundamentals (functions, types, exceptions, I/O, modules, SQLAlchemy, etc.)  
and demonstrates clean architecture separation between **UI**, **logic**, and **storage** layers.

---

## 📁 Project Structure

```
Python-Movies-Database/
│
├── main.py                         # Entry point for the CLI app
├── movies.py                       # Core command logic (add, delete, search, etc.)
│
├── utils/                          # Helper utilities and shared logic
│   ├── app_utils.py                # I/O, validation, fuzzy search, user handling
│   ├── app_types.py                # Type aliases and enums
│   └── init.py
│
├── views/                          # Rendering functions for the console
│   ├── render.py
│   └── init.py
│
├── movie_storage/                  # Data persistence layer
│   ├── movie_storage_sql.py        # SQLite CRUD operations using SQLAlchemy
│   └── init.py
│
├── static/                         # Contains generated HTML pages and templates
│   ├── index_template.html
│   └── .html
│
└── requirements.txt                # Project dependencies
```

---

## ⚙️ Features

- 🆕 Add new movies (auto-fetches metadata from **OMDb API**)
- 🗑️ Delete and update existing entries  
- 🔍 Search by title or fuzzy match (Levenshtein distance)
- 📊 View statistics (average, median, best/worst ratings)
- 🧮 Filter movies by year or rating range
- 🎲 Random movie picker
- 🌐 Generate static HTML movie page
- 🖼️ Plot a rating histogram using Matplotlib
- 👤 Multi-user support (stored in SQLite)

---

## 🧰 Tech Stack

| Component       | Technology                               |
|-----------------|------------------------------------------|
| Language        | Python 3.10+                             |
| Database        | SQLite (via SQLAlchemy Core)             |
| CLI             | Standard I/O + ANSI colors               |
| Visualization   | Matplotlib                               |
| APIs            | OMDb API, API Ninjas (for country codes) |
| Data Processing | Levenshtein (fuzzy matching)             |

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/jasonbdt/Python-Movies-Database.git
cd Python-Movies-Database
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate    # on macOS/Linux
# or
.venv\Scripts\activate       # on Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

Run the app via:

```bash
python main.py
```

You'll be greeted by the Movies Database CLI, where you can:

- Add, delete, or edit movies
- View ratings, statistics, and random picks
- Generate a static HTML page of your collection

All movies are stored per user inside a local SQLite database file.

---

### 📊 Example Output

```bash
---------------------------------------
     🎬  Movies Database CLI
---------------------------------------
1. List movies
2. Add movie
3. Delete movie
4. Statistics
5. Generate website
0. Exit
---------------------------------------
Enter your choice: 1

3 movies in total
- Inception (2010): 8.8
- Interstellar (2014): 8.6
- The Dark Knight (2008): 9.0
```

---

## 🧪 Testing

Currently, this project focuses on CLI functionality rather than automated tests.
Unit tests may be added later using **pytest**.

---

## 🌍 Environment Variables

The following environment variables are required for API access:


| Variable       | Description                            |
|----------------|----------------------------------------|
| OMDB_API_KEY   | Your OMDb API key                      |
| NINJAS_API_KEY | Your API Ninjas key for country lookup |
| APP_TITLE      | (Optional) Custom CLI header title     |

You can place them in a .env file or export them in your shell.

---

## 📦 Dependencies

Main dependencies listed in `requirements.txt`:

- SQLAlchemy
- requests
- matplotlib
- python-Levenshtein
- python-dotenv

---

## 💡 Development Notes

- Follows **PEP 8** and **PEP 257** style conventions  
- Each function includes a **Google-style docstring**  
- The codebase is modularized to separate:
  - `movies.py` → command logic  
  - `utils/` → generic helpers  
  - `views/` → console rendering  
  - `movie_storage/` → persistence layer

---

## 🧠 Future Improvements

- Add automated tests (pytest)
- Add user authentication
- Add export/import functionality (CSV / JSON)
- Create a GUI or web version (Flask / FastAPI)
- Add Dockerfile for simplified setup

---

## 👤 Author

**Jason Bladt**  
Software Developer & Tech Enthusiast  
[LinkedIn Profile](https://www.linkedin.com/in/jason-bladt-07313b11b)

---

## 📜 License

This project is licensed under the **Apache License 2.0** – see the [LICENSE](./LICENSE) file for details.

---

> _"Code as if the next person maintaining it knows where you live."_  
> — Unknown Developer