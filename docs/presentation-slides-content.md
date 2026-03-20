# Presentation Slides Content

This file contains the final short text that can be copied directly into the PPTX.

Recommended slide count: `8`

---

## Slide 1

### Title

**Book Metadata, Review & Insight API**

### Text

COMP3011 Web Services and Web Data  
FastAPI + SQLAlchemy + JWT + PostgreSQL + Open Library

- CRUD for books, authors, reviews, and reading lists
- Analytics and personalised recommendations
- Public dataset integration and live deployment

### Visual

`[Screenshot: live Swagger UI homepage]`

---

## Slide 2

### Title

**Problem, Scope, and Data Model**

### Text

- Book APIs suit both CRUD and analytics
- Public metadata is combined with user review data
- The system supports browsing, reviewing, tracking, and recommendation

**Core entities**
- User, Author, Book, Review, ReadingListEntry

### Visual

`[Diagram: simple ER-style diagram with 5 entities]`

---

## Slide 3

### Title

**Architecture and Technical Choices**

### Text

- FastAPI application layer
- SQLAlchemy ORM + Alembic migrations
- SQLite locally, PostgreSQL in deployment
- JWT authentication and role-based access control

### Visual

`[Diagram: Client -> FastAPI -> SQLAlchemy -> Database]`

---

## Slide 4

### Title

**API Documentation Overview**

### Text

- Swagger UI for testing and live demonstration
- ReDoc for cleaner reference reading
- Markdown and PDF documentation in the repository
- Auth, CRUD, analytics, and error format are all documented

### Visual

`[Screenshot: Swagger UI with endpoint groups visible]`

---

## Slide 5

### Title

**Advanced Features and Demo Highlights**

### Text

- Role-based admin endpoints
- Automatic rating recalculation
- Genre and author analytics
- Personalised recommendations
- Unified error-response structure

### Visual

`[Screenshot: analytics endpoint response in Swagger UI]`

---

## Slide 6

### Title

**Version Control Practices and Commit History**

### Text

- Project developed incrementally through Git
- Implementation, fixes, and documentation tracked separately
- Commit history shows API validation, dataset refinement, and report updates

### Visual

`[Screenshot: GitHub commit history or terminal git log]`

---

## Slide 7

### Title

**Testing, Deployment, and Technical Report**

### Text

- `pytest` + `pytest-asyncio` + `httpx`
- Coverage includes auth, CRUD, permissions, and analytics
- Render deployment with PostgreSQL
- Technical report explains architecture, data, testing, and GenAI use

### Visual

`[Split visual: pytest passing output + live deployment screenshot]`

---

## Slide 8

### Title

**Deliverables and Closing Summary**

### Text

**Deliverables**
- GitHub repository
- API documentation
- Technical report
- Live deployed API
- PPTX presentation

**Summary**
- Real public dataset integration
- Analytics and recommendation features
- Tested, documented, and deployed API

### Visual

`[Visual: clean deliverables icons row or collage]`

---

## Screenshot Checklist

1. Swagger UI homepage
2. ER/data model diagram
3. architecture diagram
4. analytics endpoint response
5. Git commit history
6. pytest passing output
7. live deployed API docs
8. deliverables icon row
