# Technical Report – Outline (max 5 pages)

Use this outline to write your **Technical Report** PDF. Fill in each section in your own words; the report must reflect your design decisions and understanding.

---

## 1. Introduction (≈0.5 page)

- Project title: **Book Metadata, Review & Insight API**
- Brief aim: data-driven REST API for books, authors, reviews, reading lists, and analytics/recommendations
- Target users: general users (browse, review, reading list, recommendations) and administrators (manage content, import/enrich data)
- Mention that the report covers data sources, architecture, technology choices, API design, testing, deployment, and use of Generative AI

---

## 2. Data Sources and Data Modelling (≈0.75 page)

- **Internal data**: PostgreSQL (or SQLite for dev); main entities: **users**, **authors**, **books**, **reviews**, **reading_list_entries**
- **Data model**: Describe relationships (e.g. Book → Author; Review → User, Book; ReadingListEntry → User, Book). You can refer to the ER diagram in the repo or draw one
- **External data** (if used): e.g. Google Books / Open Library for enrichment; cite licence and how you use it. If not yet integrated, state “planned” and keep focus on internal model
- **Sample/seed data**: Mention `scripts/load_sample_data.py` and how it populates authors, books, users, and reviews for demonstration

---

## 3. Architecture and Technology Choices (≈1 page)

- **Why FastAPI**: performance, automatic OpenAPI docs, type hints, async support; contrast briefly with Django REST Framework if helpful
- **Why SQL (PostgreSQL/SQLite)**: relational data, joins, transactions; explain why NoSQL was not chosen (or justify if you did use it)
- **Layered structure**: API routes → services/repositories (if any) → ORM models; mention `app/api`, `app/models`, `app/schemas`, `app/core`
- **Authentication**: JWT (python-jose), password hashing (passlib/bcrypt), role-based access (e.g. `is_admin` for authors/books/recalculate-rating)
- **Migrations**: Alembic for schema versioning and repeatable deployments

---

## 4. API Design and Implementation (≈0.75 page)

- **REST conventions**: resource-based URLs (`/api/v1/authors`, `/api/v1/books`, etc.), HTTP methods (GET/POST/PUT/DELETE), status codes (200, 201, 204, 400, 401, 403, 404, 500)
- **Key endpoints**: list a few (e.g. CRUD for books, reviews; analytics such as rating distribution, top-rated genres, trending authors, user recommendations)
- **Error format**: unified `{"error": {"code", "message", "details"}}` and how it helps clients
- **Pagination/filtering**: e.g. `skip`, `limit`, `search`, `author_id`, `genre`, `order_by` on books
- **Advanced features**: e.g. recalculate book rating from reviews; content-based recommendations; optional rate limiting or API key if implemented

---

## 5. Testing, Deployment, and Version Control (≈0.5 page)

- **Testing**: pytest + pytest-asyncio + httpx; in-memory SQLite for isolation; tests for auth (register/login/me), CRUD (authors, books), reviews and analytics
- **Deployment**: e.g. Render or Railway; environment variables (`DATABASE_URL`, `JWT_SECRET_KEY`); run migrations and `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Version control**: Git with meaningful commit messages; link to public GitHub repo

---

## 6. Use of Generative AI (≈0.5 page) – **Required**

- **Declaration**: List tools used (e.g. Cursor, ChatGPT, Copilot) and for what (design, code, debugging, documentation, report drafting)
- **How you used GenAI**: e.g. exploring API design, drafting schemas, writing tests, improving error handling, generating documentation or report structure
- **Your contribution**: What you wrote or decided yourself; what you reviewed and adapted from AI output
- **Limitations**: Where AI was not used or was wrong; how you verified and corrected
- **Appendix**: Attach sample conversation logs or exports as required by the module

---

## 7. Limitations and Future Work (≈0.25 page)

- **Limitations**: e.g. single-region deployment, no caching, recommendation logic is heuristic/content-based rather than full ML, optional external APIs not yet integrated
- **Future work**: e.g. integrate Google Books/Open Library, add rate limiting, improve recommendation algorithm, add more analytics, CI/CD pipeline

---

*Keep the report to the maximum page limit (e.g. 5 pages). Export as PDF and submit with your repository link, API documentation link, and presentation slides link as specified in the coursework brief.*
