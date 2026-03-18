# Raw data directory

Place your books CSV file here for import.

## Recommended public dataset: Goodreads (Kaggle)

- **Kaggle – Goodreads-books (various versions)**  
  Example: [Goodreads Books Dataset](https://www.kaggle.com/datasets/ayushiiisahu/goodreads-books-dataset) or search Kaggle for "goodreads books".
- After downloading, save the CSV as `books.csv` in this folder (or use the path when running the import script).
- Supported columns (names are flexible): `title`, `authors`, `average_rating`, `isbn`, `ratings_count`, `language_code`, `num_pages`, `publication_date`, `genre` (or `main_genre`). The importer maps the first author in `authors` to the Author table.

## Quick start (no download)

The repo includes `sample_books.csv` with a small set of books. Run:

```bash
python scripts/import_books_from_csv.py
```

That uses `data/raw/sample_books.csv` by default. To use your own file:

```bash
python scripts/import_books_from_csv.py data/raw/books.csv
```

## Licence

If you use a Kaggle or other third-party dataset, ensure it is used in line with its licence and cite the source in your technical report.
