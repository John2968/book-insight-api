# Book Metadata, Review & Insight API

This project is a FastAPI-based REST API for managing books, authors, reviews, reading lists, and analytical insight endpoints such as rating distributions, top-rated genres, trending authors, and personalised recommendations.

## Links

- **GitHub repository**: [https://github.com/John2968/book-insight-api](https://github.com/John2968/book-insight-api)
- **Live deployment**: [https://book-insight-api.onrender.com](https://book-insight-api.onrender.com)
- **Live Swagger UI**: [https://book-insight-api.onrender.com/api/v1/docs](https://book-insight-api.onrender.com/api/v1/docs)
- **Live ReDoc**: [https://book-insight-api.onrender.com/api/v1/redoc](https://book-insight-api.onrender.com/api/v1/redoc)

## Tech Stack

- **Backend**: Python 3.12+, FastAPI
- **Database**: SQLite for local development, PostgreSQL for deployment
- **ORM and migrations**: SQLAlchemy 2.x, Alembic
- **Authentication**: JWT with `python-jose`, password hashing with `passlib` and `bcrypt`
- **Testing**: `pytest`, `pytest-asyncio`, `httpx`
- **Documentation**: OpenAPI / Swagger UI plus written documentation in `docs/`

## Local Development

### 1. Clone and set up the environment

```bash
git clone https://github.com/John2968/book-insight-api.git
cd book-insight-api
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a local `.env` file from the example:

```bash
copy .env.example .env
```

By default, local development uses SQLite:

```text
DATABASE_URL=sqlite+aiosqlite:///./book_insight.db
```

For deployment, set a PostgreSQL connection string and a strong `JWT_SECRET_KEY`.

### 4. Run migrations

```bash
alembic upgrade head
```

### 5. Load data

Import the bundled public dataset:

```bash
python scripts/import_books_from_csv.py
```

Optionally seed demo users and reviews on top of the imported public books:

```bash
python scripts/seed_demo_users_and_reviews.py
```

Demo accounts created by the seed script:

- `admin` / `admin123`
- `alice` / `password123`

To regenerate the bundled dataset from Open Library:

```bash
python scripts/fetch_open_library_dataset.py
```

To import a different CSV file:

```bash
python scripts/import_books_from_csv.py data/raw/books.csv
```

Supported import fields include `title`, `authors`, `average_rating`, `isbn`, `ratings_count`, `publication_date`, and `genre`.

### 6. Run the API

```bash
uvicorn app.main:app --reload
```

Local URLs:

- API base: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/api/v1/docs`
- ReDoc: `http://127.0.0.1:8000/api/v1/redoc`
- Health check: `http://127.0.0.1:8000/api/v1/health/ping`

## Testing

Run the automated tests from the project root:

```powershell
.\.venv\Scripts\python -m pytest
```

The tests cover authentication, CRUD behaviour, review workflows, permission checks, error handling, and analytics endpoints using an isolated in-memory SQLite database.

## API Documentation

- **Interactive local docs**: `http://127.0.0.1:8000/api/v1/docs`
- **Interactive live docs**: `https://book-insight-api.onrender.com/api/v1/docs`
- **Markdown source**: `docs/api-documentation.md`
- **Submission artifact**: export `docs/api-documentation.md` to PDF for submission

## Data Source

The bundled dataset is `data/raw/open_library_books.csv`, a curated 20-book subset generated from the [Open Library Search API](https://openlibrary.org/dev/docs/api/search) by `scripts/fetch_open_library_dataset.py`.

This dataset contains real public bibliographic metadata mapped to the API import format, including title, author, ISBN, publication date, rating average, rating count, and genre. Open Library states that it does not assert copyright over the underlying database material; the source is cited in the report and supporting documentation.

## Deployment Notes

The application is deployed on Render at [https://book-insight-api.onrender.com](https://book-insight-api.onrender.com).

For a fresh deployment on Render:

1. Connect the GitHub repository.
2. Create a PostgreSQL database.
3. Set environment variables:
   - `DATABASE_URL=postgresql+asyncpg://...`
   - `JWT_SECRET_KEY=<strong-secret>`
   - `ENV=prod`
   - `BACKEND_CORS_ORIGINS=*` or a specific frontend origin if required
4. Use the build command:
   - `pip install -r requirements.txt && alembic upgrade head`
5. Use the start command:
   - `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Optionally import the bundled dataset into the production database with `python scripts/import_books_from_csv.py`.

## Submission Files

The main report-style files for submission are:

- `docs/technical-report.md` -> export to `docs/technical-report.pdf`
- `docs/api-documentation.md` -> export to `docs/api-documentation.pdf`
- `docs/genai-declaration.md` -> include as an appendix or separate PDF if required
- presentation slides in PPTX format

## Project Structure

```text
book-insight-api/
├── app/
│   ├── api/v1/           # Route handlers
│   ├── core/             # Config, security, exceptions
│   ├── db/               # Database session management
│   ├── models/           # SQLAlchemy ORM models
│   ├── schemas/          # Pydantic request and response schemas
│   └── main.py           # FastAPI entry point
├── alembic/              # Database migrations
├── data/raw/             # Bundled and user-supplied CSV datasets
├── docs/                 # Report, API documentation, submission notes
├── scripts/              # Import, export, and seed utilities
├── tests/                # Automated test suite
├── requirements.txt
├── .env.example
└── README.md
```

## Licence

See `LICENSE`.
