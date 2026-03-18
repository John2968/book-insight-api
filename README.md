# Book Metadata, Review & Insight API

A FastAPI-based REST API for managing books, authors, reviews, reading lists, and analytical insights (rating distributions, top genres, trending authors, personalised recommendations).

## Tech stack

- **Backend**: Python 3.12+, FastAPI
- **Database**: SQLite (local dev) / PostgreSQL (recommended for production)
- **ORM & migrations**: SQLAlchemy 2.x, Alembic
- **Auth**: JWT (python-jose, passlib with bcrypt)
- **Testing**: pytest, pytest-asyncio, httpx
- **Docs**: OpenAPI (Swagger UI at `/api/v1/docs`), plus Markdown API doc in `docs/api-documentation.md`

## Local development

### 1. Clone and setup

```bash
git clone <your-repo-url>
cd book-insight-api
python -m venv .venv
```

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment

Copy the example env and adjust if needed:

```bash
copy .env.example .env
```

Default `.env` uses SQLite: `DATABASE_URL=sqlite+aiosqlite:///./book_insight.db`. For production, set a PostgreSQL URL and a strong `JWT_SECRET_KEY`.

### 4. Database migrations

```bash
alembic upgrade head
```

### 5. Load data (optional)

**Option A – Demo users and a few books/reviews (for testing auth and reviews):**

```bash
python scripts/load_sample_data.py
```

Sample users: **admin** / `admin123`, **alice** / `password123`.

**Option B – Import books from a CSV (public-dataset style):**

The repo includes a small `data/raw/sample_books.csv` (15 books). To import it:

```bash
python scripts/import_books_from_csv.py
```

To use your own CSV (e.g. from [Kaggle Goodreads datasets](https://www.kaggle.com/datasets)), place the file in `data/raw/` and run:

```bash
python scripts/import_books_from_csv.py data/raw/books.csv
```

Supported columns: `title`, `authors`, `average_rating`, `isbn`, `ratings_count`, `publication_date`, `genre`. See `data/raw/README.md` for details and licence/citation.

### 6. Run the API

```bash
uvicorn app.main:app --reload
```

- API base: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/api/v1/docs`
- ReDoc: `http://127.0.0.1:8000/api/v1/redoc`
- Health: `GET http://127.0.0.1:8000/api/v1/health/ping`

## Testing

```bash
pytest
```

Runs tests for auth (register/login/me), authors/books CRUD, and reviews/analytics. Uses an in-memory SQLite database.

## API documentation

- **Interactive**: Open `http://127.0.0.1:8000/api/v1/docs` when the server is running.
- **Markdown (for PDF)**: See `docs/api-documentation.md`. Export to PDF (e.g. VS Code “Markdown PDF” or Pandoc) and submit/link as required.

## Deployment (e.g. Render / Railway)

1. Push the repo to GitHub (public or connected to the platform).
2. Create a new **Web Service**; connect the repository.
3. Set environment variables:
   - `DATABASE_URL` – PostgreSQL connection string (Render/Railway provide one).
   - `JWT_SECRET_KEY` – Strong random secret.
   - `ENV=prod`
   - Optionally `BACKEND_CORS_ORIGINS` if you need specific origins.
4. **Build command** (if needed): `pip install -r requirements.txt`
5. **Start command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. For PostgreSQL, run migrations in the build or a release phase, e.g. `alembic upgrade head` (ensure `DATABASE_URL` uses a sync driver for Alembic, or run migrations locally against the production DB).

## Project structure

```
book-insight-api/
├── app/
│   ├── api/v1/          # Route handlers (auth, authors, books, reviews, reading-list, analytics)
│   ├── core/            # Config, security, exceptions
│   ├── db/              # Database session
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic request/response models
│   └── main.py          # FastAPI application
├── alembic/             # Database migrations
├── scripts/              # e.g. load_sample_data.py
├── tests/                # Pytest tests
├── docs/                 # API documentation (Markdown), technical report
├── requirements.txt
├── .env.example
└── README.md
```

## Licence

See `LICENSE` in the repository.
