# Technical Report: Book Metadata, Review & Insight API

**Module**: COMP3011 Web Services and Web Data  
**Coursework**: 1 - Individual Web Services API Development Project  

---

## 1. Introduction

This project implements a data-driven REST API for managing book metadata, authors, user reviews, reading lists, and analytical insight endpoints. The application was designed to satisfy the coursework requirement for a complete web service that demonstrates structured API design, persistent data storage, authentication, testing, deployment, and professional documentation.

The system supports two main user groups. General users can browse books, submit and manage reviews, maintain reading lists, and receive personalised recommendations. Administrators can create, update, and delete authors and books, as well as recalculate derived rating fields. The final implementation is available both locally and via a live Render deployment, which makes the project suitable for demonstration during the oral presentation.

This report explains the project data sources, data model, technical architecture, API design, testing strategy, deployment approach, version control practice, and use of Generative AI.

---

## 2. Data Sources and Data Modelling

The project uses a relational data model implemented with SQLAlchemy. SQLite is used for local development and test isolation, while PostgreSQL is used for deployed hosting. The core entities are `User`, `Author`, `Book`, `Review`, and `ReadingListEntry`.

The `User` entity stores identity and access-control fields such as username, email, password hash, activity status, admin role, and creation timestamp. A user can create many reviews and many reading list entries. The `Author` entity stores author-level metadata including name, country, and biography. A single author can be associated with many books. The `Book` entity stores bibliographic and analytical fields such as title, ISBN, publication date, description, cover image URL, main genre, average rating, ratings count, and a nullable foreign key to an author. The `Review` entity records the rating and review text provided by a user for a specific book, with a database constraint limiting ratings to the range 1 to 5. The `ReadingListEntry` entity links a user to a book that they wish to save, and a uniqueness constraint prevents duplicate entries for the same user-book pair.

The application uses a real public metadata source rather than a purely hand-written dataset. The bundled dataset `data/raw/open_library_books.csv` is a curated 20-book export generated from the Open Library Search API by `scripts/fetch_open_library_dataset.py`. The import utility `scripts/import_books_from_csv.py` maps this CSV into the project schema and creates authors automatically, while also preventing duplicate book insertion through ISBN checks. A second utility, `scripts/seed_demo_users_and_reviews.py`, optionally creates example users and a small amount of review activity on top of the imported public books so that authentication and analytics features can be demonstrated more easily.

Open Library is used as an offline public-data source rather than a live dependency during request handling. This choice reduces runtime complexity and external failure risk while still allowing the project to demonstrate the use of genuine public data. The imported records remain traceable to an identifiable external source, which strengthens the academic credibility of the dataset and supports the coursework requirement to reference data origins.

---

## 3. Architecture and Technology Choices

FastAPI was selected as the core web framework because it provides asynchronous request handling, automatic OpenAPI documentation, strong type-hint integration, and clear support for dependency injection. This makes it well suited to a coursework project that needs a clean, testable service layer and a professional documentation story through Swagger UI and ReDoc.

SQL was chosen over a NoSQL alternative because the project domain is strongly relational. Books, authors, users, reviews, and reading lists depend on stable foreign-key relationships, and the analytics endpoints rely on joins and aggregate queries. SQLAlchemy 2.x is used as the ORM and session-management layer, while Alembic is used for migration tracking so that schema changes can be applied consistently across local and deployed environments.

The codebase is organised into clear layers. Route handlers are defined under `app/api`, data models under `app/models`, request and response schemas under `app/schemas`, and shared services such as configuration, security, and exception helpers under `app/core`. This structure keeps endpoint logic compact and makes the application easier to test, maintain, and explain in the report and presentation.

Authentication uses JSON Web Tokens created after a successful login request. Passwords are hashed rather than stored directly, and role-based checks restrict admin-only operations such as managing authors and books. The use of dependency-based authentication in FastAPI keeps security checks reusable and consistent across endpoints.

---

## 4. API Design and Implementation

The API follows a resource-oriented structure under the `/api/v1` prefix. Core resources are exposed through predictable REST-style routes such as `/authors`, `/books`, `/reviews`, `/reading-list`, and `/analytics`. CRUD operations use conventional HTTP methods: `GET` for retrieval, `POST` for creation, `PUT` for updates, and `DELETE` for removal. A dedicated health endpoint at `/api/v1/health/ping` supports deployment verification.

The authentication flow includes registration, login, and a current-user endpoint. The login endpoint follows the OAuth2 password flow expected by Swagger UI, which improves the usability of the interactive documentation. Once authenticated, a user can manage their own reviews and reading-list items. Administrative operations are guarded through explicit role checks.

The books resource supports pagination, text search, filtering by author or genre, and ordering by title, average rating, or rating count. Reviews automatically trigger recalculation of derived book statistics so that the stored `average_rating` and `ratings_count` remain consistent with the underlying review data. This makes analytics queries cheaper and simplifies list views.

In addition to standard CRUD operations, the project includes analytical endpoints intended to demonstrate higher-value API functionality. These include rating distribution by book, top-rated genres, trending authors, and recommendation generation for the currently authenticated user. The recommendation logic is intentionally explainable rather than opaque: it uses the genres and ratings from a user’s prior activity to suggest books that match demonstrated preferences.

Error handling was standardised so that API consumers receive a unified response shape of the form `{"error": {"code": "...", "message": "...", "details": {...}}}`. This improves client-side predictability, makes the behaviour easier to document, and ensures validation and permission errors are communicated consistently.

---

## 5. Testing, Deployment, and Version Control

Automated testing is implemented with `pytest`, `pytest-asyncio`, and `httpx`. The test suite runs against an isolated in-memory SQLite database so that tests are repeatable and do not depend on local development data. Current coverage includes authentication behaviour, CRUD flows for authors and books, review creation and update behaviour, reading-list permissions, consistent error formatting, and analytics endpoints such as rating distribution and recommendations. This level of testing is especially important because the project uses asynchronous database access and role-based security checks, both of which are areas where regressions can be subtle.

The application is deployed on Render, with PostgreSQL used for the hosted database. The repository includes a `render.yaml` blueprint and environment-driven configuration through `.env` and deployment variables. The production service is available at [https://book-insight-api.onrender.com](https://book-insight-api.onrender.com), and the live interactive documentation is exposed at [https://book-insight-api.onrender.com/api/v1/docs](https://book-insight-api.onrender.com/api/v1/docs). Running Alembic migrations as part of the build process ensures that the database schema is in sync with the application code on deployment.

Version control was managed through Git, with the project stored in a public GitHub repository at [https://github.com/John2968/book-insight-api](https://github.com/John2968/book-insight-api). Using Git throughout development supported incremental implementation, testing, refactoring, documentation updates, and deployment preparation. The repository also provides transparent evidence of development progress and supports the coursework expectation that version-control practice should be part of the presentation.

---

## 6. Use of Generative AI

Generative AI was used in line with the module's Green Light policy. The detailed declaration is provided in `docs/genai-declaration.md`, but the overall pattern of use can be summarised briefly here.

AI assistance was used to explore alternative API structures, compare architectural options, draft implementation scaffolding, improve error-handling consistency, generate and refine automated tests, and improve the organisation of the written documentation. AI support was also useful when troubleshooting dependency issues and evaluating how best to present the data-ingestion approach using a real public dataset.

However, the final design decisions, implementation choices, corrections, verification steps, and all submission judgments remained the responsibility of the author. AI-generated suggestions were treated as draft material rather than authoritative answers and were checked against framework documentation, runtime behaviour, and coursework requirements before being kept.

---

## 7. Limitations and Future Work

The current deployment is intentionally lightweight. It does not include caching, background task processing, rate limiting, API-key access, or CI/CD automation. The recommendation logic is heuristic and explainable rather than machine-learning based. In addition, Open Library is used as a curated offline import source rather than as a live enrichment dependency during requests, so some metadata fields remain incomplete when the public source does not provide them directly.

There are several realistic directions for future improvement. The system could enrich records with additional live metadata sources, support cover and description backfilling, extend the analytics layer with more comparative and time-series views, and introduce stronger deployment automation. Recommendation quality could also be improved through collaborative filtering, embedding-based similarity, or hybrid ranking methods. These extensions were not necessary for the coursework deliverable but would be sensible next steps for a production-oriented version of the system.

---

## 8. References

1. FastAPI. *FastAPI Documentation*. Available at: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
2. SQLAlchemy. *SQLAlchemy Documentation*. Available at: [https://docs.sqlalchemy.org/](https://docs.sqlalchemy.org/)
3. Alembic. *Alembic Documentation*. Available at: [https://alembic.sqlalchemy.org/](https://alembic.sqlalchemy.org/)
4. Open Library. *Search API Documentation*. Available at: [https://openlibrary.org/dev/docs/api/search](https://openlibrary.org/dev/docs/api/search)
5. Render. *Render Documentation*. Available at: [https://render.com/docs](https://render.com/docs)
6. GitHub repository for this project. Available at: [https://github.com/John2968/book-insight-api](https://github.com/John2968/book-insight-api)

---

## Appendix A: Supporting Materials

- **Repository**: [https://github.com/John2968/book-insight-api](https://github.com/John2968/book-insight-api)
- **Live API**: [https://book-insight-api.onrender.com](https://book-insight-api.onrender.com)
- **Live API documentation**: [https://book-insight-api.onrender.com/api/v1/docs](https://book-insight-api.onrender.com/api/v1/docs)
- **Written API documentation**: `docs/api-documentation.md` (export to PDF for submission)
- **Generative AI declaration**: `docs/genai-declaration.md`
- **Presentation slides**: submitted separately as the accompanying PPTX deck or linked in the final submission form, as required by the module
