"""
Fetch a curated public book dataset from the Open Library Search API.

The output is a CSV tailored to this project's importer:
title, authors, average_rating, isbn, ratings_count, publication_date, genre

Usage:
  python scripts/fetch_open_library_dataset.py
"""
from __future__ import annotations

import csv
import json
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
import re
import unicodedata


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_CSV = REPO_ROOT / "data" / "raw" / "open_library_books.csv"
SEARCH_API = "https://openlibrary.org/search.json"


@dataclass(frozen=True)
class BookSeed:
    title: str
    author: str
    fallback_genre: str


BOOK_SEEDS: list[BookSeed] = [
    BookSeed("Neuromancer", "William Gibson", "Science Fiction"),
    BookSeed("Kindred", "Octavia E. Butler", "Science Fiction"),
    BookSeed("The Left Hand of Darkness", "Ursula K. Le Guin", "Science Fiction"),
    BookSeed("A Wizard of Earthsea", "Ursula K. Le Guin", "Fantasy"),
    BookSeed("Mistborn", "Brandon Sanderson", "Fantasy"),
    BookSeed("The Name of the Wind", "Patrick Rothfuss", "Fantasy"),
    BookSeed("Gone Girl", "Gillian Flynn", "Thriller"),
    BookSeed("Rebecca", "Daphne du Maurier", "Mystery"),
    BookSeed("The Murder of Roger Ackroyd", "Agatha Christie", "Mystery"),
    BookSeed("The Handmaid's Tale", "Margaret Atwood", "Dystopian"),
    BookSeed("Beloved", "Toni Morrison", "Historical Fiction"),
    BookSeed("Jane Eyre", "Charlotte Bronte", "Classics"),
    BookSeed("Dracula", "Bram Stoker", "Classics"),
    BookSeed("Moby-Dick", "Herman Melville", "Classics"),
    BookSeed("The Color Purple", "Alice Walker", "Fiction"),
    BookSeed("The Secret History", "Donna Tartt", "Fiction"),
    BookSeed("The Dispossessed", "Ursula K. Le Guin", "Science Fiction"),
    BookSeed("Fahrenheit 451", "Ray Bradbury", "Science Fiction"),
    BookSeed("The Martian", "Andy Weir", "Science Fiction"),
    BookSeed("The Picture of Dorian Gray", "Oscar Wilde", "Classics"),
]


def clean_text(value: str) -> str:
    ascii_text = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
    return " ".join(ascii_text.split())


def normalize_for_match(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", clean_text(value).lower())


def fetch_book(seed: BookSeed) -> dict[str, str]:
    params = {
        "title": seed.title,
        "author": seed.author,
        "limit": 5,
        "fields": "key,title,author_name,first_publish_year,isbn,subject,ratings_average,ratings_count",
    }
    url = f"{SEARCH_API}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "book-insight-api/1.0 (student project dataset fetcher)",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))

    docs = payload.get("docs", [])
    if not docs:
        raise RuntimeError(f"No result found for {seed.title} by {seed.author}")

    seed_title_norm = normalize_for_match(seed.title)
    seed_author_norm = normalize_for_match(seed.author)

    def score(doc: dict) -> int:
        title_norm = normalize_for_match(doc.get("title", ""))
        authors_norm = [normalize_for_match(name) for name in doc.get("author_name", [])]
        score_value = 0
        if title_norm == seed_title_norm:
            score_value += 100
        elif seed_title_norm in title_norm or title_norm in seed_title_norm:
            score_value += 50
        if seed_author_norm in authors_norm:
            score_value += 100
        if doc.get("ratings_count"):
            score_value += 10
        return score_value

    chosen = max(docs, key=score)

    authors = chosen.get("author_name", [])
    isbn_values = chosen.get("isbn", [])
    work_key = chosen.get("key", "")
    primary_author = clean_text(authors[0]) if authors else clean_text(seed.author)
    title = clean_text(chosen.get("title", seed.title))

    return {
        "title": title,
        "authors": primary_author,
        "average_rating": str(chosen.get("ratings_average", "") or ""),
        "isbn": str(isbn_values[0])[:20] if isbn_values else "",
        "ratings_count": str(chosen.get("ratings_count", "") or ""),
        "publication_date": str(chosen.get("first_publish_year", "") or ""),
        "genre": seed.fallback_genre,
        "open_library_work_key": work_key,
        "source_url": f"https://openlibrary.org{work_key}" if work_key else "",
    }


def main() -> None:
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    rows = [fetch_book(seed) for seed in BOOK_SEEDS]
    rows.sort(key=lambda row: row["title"].lower())

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "title",
                "authors",
                "average_rating",
                "isbn",
                "ratings_count",
                "publication_date",
                "genre",
                "open_library_work_key",
                "source_url",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover
        print(f"Failed to fetch Open Library dataset: {exc}", file=sys.stderr)
        sys.exit(1)
