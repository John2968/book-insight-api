# Technical Report: Book Metadata, Review & Insight API

**Module**: COMP3011 Web Services and Web Data  
**Coursework**: 1 – Individual Web Services API Development Project  

---

## 1. Introduction

This project implements a **Book Metadata, Review & Insight API**: a data-driven REST API for managing books, authors, user reviews, reading lists, and analytical insights. The system provides standard CRUD operations, JWT-based authentication, and analytics endpoints (rating distributions, top-rated genres, trending authors, and personalised book recommendations).

**Target users** are (1) general users, who can browse books, create and manage reviews, maintain a reading list, and receive recommendations, and (2) administrators, who can create and update authors and books, recalculate book ratings, and manage content. The API is designed to be demonstrable locally or on a hosted platform and to support future integration with external metadata sources (e.g. Google Books, Open Library).

This report covers data sources and data modelling, architecture and technology choices, API design and implementation, testing and deployment, version control, use of Generative AI, and limitations and future work.

---

## 2. Data Sources and Data Modelling

**Internal data** is stored in a relational database: SQLite for local development and PostgreSQL for production. The main entities are **users**, **authors**, **books**, **reviews**, and **reading_list_entries**.

**Data model and relationships:**
- **User**: id, username, email, password_hash, is_active, is_admin, created_at. Users own reviews and reading list entries.
- **Author**: id, name, country, biography. An author has many books (one-to-many).
- **Book**: id, title, isbn, publication_date, description, cover_image_url, main_genre, author_id (FK to Author), average_rating, ratings_count. A book has many reviews and can appear in many users’ reading lists.
- **Review**: id, user_id, book_id, rating (1–5), review_text, created_at. Each review belongs to one user and one book; a constraint enforces rating between 1 and 5.
- **ReadingListEntry**: id, user_id, book_id, added_at. A unique constraint on (user_id, book_id) prevents duplicate entries per user.

**Data sources for populating the database:**
1. **Seed script** (`scripts/load_sample_data.py`): creates demo users (e.g. admin, alice), authors, books, and reviews for testing authentication and review flows.
2. **CSV import** (`scripts/import_books_from_csv.py`): imports books from a CSV file and creates authors by name (deduplicated). The repository includes `data/raw/sample_books.csv` (15 books with title, authors, average_rating, ratings_count, publication_date, genre). The same script can be used with larger public datasets (e.g. [Kaggle Goodreads books](https://www.kaggle.com/datasets)): the user downloads the CSV, places it in `data/raw/`, and runs the script. Any such dataset should be cited and used in accordance with its licence.

**External data**: Google Books and Open Library are listed in the project scope for future enrichment (e.g. descriptions, cover images, ISBNs). They are not integrated in the current implementation; the design allows additional metadata to be added to existing book records later.

---

## 3. Architecture and Technology Choices

**Framework: FastAPI.** FastAPI was chosen for its native async support, automatic OpenAPI (Swagger) documentation, type hints and Pydantic validation, and performance. Compared to Django REST Framework, FastAPI offers a lighter-weight stack and built-in async, which fits a read-heavy API with analytics queries. The decision was documented in the project scope and reflected in the use of async database sessions and non-blocking request handling.

**Database: SQL (SQLite / PostgreSQL).** A relational database was chosen because the domain is naturally relational (books–authors, users–reviews–books, reading lists). Joins and aggregates are used for analytics (e.g. rating distribution per book, top genres by average rating). Transactions ensure consistency when creating reviews and updating book statistics. NoSQL was not selected because the access patterns are structured and the assignment encourages SQL unless NoSQL is clearly justified.

**Layered structure:** The application is organised into `app/api` (route handlers), `app/models` (SQLAlchemy ORM), `app/schemas` (Pydantic request/response models), `app/core` (configuration, security, exceptions), and `app/db` (database session). Dependency injection (e.g. `get_db`, `get_current_user`) keeps routes thin and testable.

**Authentication and security:** Authentication uses JWT (python-jose) with HS256. Passwords are hashed with passlib and bcrypt. The login endpoint conforms to OAuth2 password flow for compatibility with Swagger UI. Access control is role-based: endpoints that create or update authors and books, or recalculate ratings, require the current user to have `is_admin=True`; review and reading-list endpoints require the user to be the resource owner or an admin.

**Migrations:** Alembic is used for schema versioning. Migrations are generated from the ORM models and applied with `alembic upgrade head`, supporting repeatable deployments and different environments (e.g. local SQLite, production PostgreSQL).

---

## 4. API Design and Implementation

**REST conventions:** The API uses resource-based URLs under `/api/v1/`: e.g. `/api/v1/books`, `/api/v1/authors`, `/api/v1/reviews`, `/api/v1/reading-list`, `/api/v1/analytics`. HTTP methods follow REST: GET for retrieval, POST for creation, PUT for full updates, DELETE for removal. Status codes follow industry practice: 200 (OK), 201 (Created), 204 (No Content), 400 (Bad Request), 401 (Unauthorized), 403 (Forbidden), 404 (Not Found), 500 (Internal Server Error).

**Key endpoints:** Health check: `GET /api/v1/health/ping`. Auth: `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`. Authors: list (with optional search), create, get, update, delete. Books: list (with pagination, search, filter by author/genre, sort by title/rating/ratings_count), create, get, update, delete, and `POST /api/v1/books/{id}/recalculate-rating`. Reviews: list (filter by book or user), create, update, delete; creating or updating a review triggers recalculation of the book’s average_rating and ratings_count. Reading list: list current user’s entries, add book, remove entry. Analytics: `GET /api/v1/analytics/books/{id}/rating-distribution`, `GET /api/v1/analytics/genres/top-rated`, `GET /api/v1/analytics/authors/trending`, `GET /api/v1/analytics/users/me/recommendations` (content-based from preferred genres and ratings).

**Error format:** All error responses use a unified structure: `{"error": {"code": "...", "message": "...", "details": {...}}}`. Codes include BOOK_NOT_FOUND, AUTHOR_NOT_FOUND, REVIEW_FORBIDDEN, USER_EXISTS, INVALID_CREDENTIALS, etc. This allows clients to handle errors consistently and supports documentation of error codes in the API documentation.

**Pagination and filtering:** List endpoints accept `skip` and `limit`. Books support `search` (title substring), `author_id`, `genre`, and `order_by` (title, rating, ratings_count). Reviews and authors support relevant filters (e.g. book_id, user_id, search by author name).

**Advanced features:** Recalculation of book ratings from reviews; content-based recommendations using the user’s highly rated books and preferred genres; role-based access for admin-only operations. Rate limiting and API keys are not implemented in the current version but can be added as middleware or dependencies.

---

## 5. Testing, Deployment, and Version Control

**Testing:** The test suite uses pytest with pytest-asyncio and httpx. An in-memory SQLite database is used so tests do not depend on external state. The client fixture overrides the database dependency so that the same session is used for the app and for test setup (e.g. promoting a user to admin). Tests cover: (1) auth – register, login, and get current user; (2) authors and books CRUD – create author, create book, list with search, update, delete; (3) reviews and analytics – create reviews, check rating distribution, and call the recommendations endpoint. Tests are run with `pytest` from the project root.

**Deployment:** The application can be deployed to a platform such as Render or Railway. The repository includes a `render.yaml` blueprint. Required environment variables include `DATABASE_URL` (PostgreSQL in production) and `JWT_SECRET_KEY`. The start command is `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Migrations should be run during the build or release phase (e.g. `alembic upgrade head`) against the production database. The README documents these steps and the option to use the provided CSV import for initial or demo data.

**Version control:** The project is maintained in a Git repository with a clear commit history. Meaningful commit messages are used (e.g. feat: add CRUD for books; fix: tests use shared session for admin). The repository includes a README with setup and run instructions, links to API documentation, and data-loading options. The API documentation is available as Markdown (`docs/api-documentation.md`) for export to PDF and is also exposed interactively via Swagger UI at `/api/v1/docs`.

---

## 6. Use of Generative AI

Generative AI was used in line with the module’s “Green Light” policy. The tools and purposes are documented in the **Generative AI Declaration** (see `docs/genai-declaration.md` or Appendix A). Summary:

- **Tools:** Cursor (and/or similar AI-assisted editors) and optionally other conversational AI tools were used for design discussion, code drafting, test design, documentation structure, and report drafting.
- **Purposes:** Exploring API and error-response design, drafting Pydantic schemas and route structure, generating pytest fixtures and test cases, improving error handling and documentation, and structuring the technical report and GenAI declaration.
- **Own contribution:** All design and technology decisions were made by the author. Code was reviewed for correctness, security, and consistency; tests were run and fixed (e.g. session isolation for admin role). The report and declaration were written and revised by the author; AI was used to improve clarity and structure, not to substitute for technical understanding.
- **Verification:** The application and tests were run locally. AI-suggested code was checked and corrected where necessary (e.g. async fixture scope, OpenAPI customisation reverted per preference). Sample conversation logs are attached as supplementary material where required by the module.

---

## 7. Limitations and Future Work

**Limitations:** The deployment is single-region and does not use caching. The recommendation logic is content-based (genre and rating preferences) rather than a trained machine-learning model. External APIs (Google Books, Open Library) are not yet integrated. Rate limiting and API keys are not implemented. The CSV import does not support very large files with streaming; for very large datasets, batch or chunked processing could be added.

**Future work:** Integrate Google Books or Open Library for metadata enrichment (descriptions, covers, ISBNs). Add rate limiting and optional API-key authentication for third-party clients. Improve recommendations (e.g. collaborative filtering or embedding-based similarity). Add more analytics (e.g. time-series trends, author comparison). Introduce a CI/CD pipeline for tests and deployment. Optionally support streaming or batch CSV import for large public datasets.

---

## References and Appendix

- **Repository:** [Link to your public GitHub repository]
- **API documentation:** See `docs/api-documentation.md` (export to PDF as required) and Swagger UI at `/api/v1/docs` when the server is running.
- **Presentation slides:** [Link to your slides, e.g. Google Drive or OneDrive]

**Appendix A: Generative AI Declaration** – See `docs/genai-declaration.md` (included in submission as required).
