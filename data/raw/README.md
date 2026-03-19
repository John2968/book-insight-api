# Raw data directory

Place CSV files here for import.

## Default bundled dataset

The repository includes `open_library_books.csv`, a curated 20-book export from the **Open Library Search API**:

- API docs: [Open Library Search API](https://openlibrary.org/dev/docs/api/search)
- Licensing note: [Open Library Developers / Licensing](https://openlibrary.org/developers/licensing)
- Export script: `scripts/fetch_open_library_dataset.py`

To regenerate the bundled dataset:

```bash
python scripts/fetch_open_library_dataset.py
```

To import it into the database:

```bash
python scripts/import_books_from_csv.py
```

That uses `data/raw/open_library_books.csv` by default.

## Using your own CSV

You can also place another file here and import it explicitly:

```bash
python scripts/import_books_from_csv.py data/raw/books.csv
```

Supported columns (names are flexible): `title`, `authors`, `average_rating`, `isbn`, `ratings_count`, `language_code`, `num_pages`, `publication_date`, `genre` (or `main_genre`). The importer maps the first author in `authors` to the Author table.

## Licence and citation

Open Library states that it does not assert copyright over the database material and that many records are public-domain or contributed as open data. Cite Open Library as the source of the bundled dataset in your technical report and submission materials.
