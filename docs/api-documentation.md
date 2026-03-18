# Book Metadata, Review & Insight API – Documentation

## 1. Overview

- **Base URL (local)**: `http://127.0.0.1:8000`
- **API prefix**: `/api/v1`
- **Authentication**: JWT Bearer token in header: `Authorization: Bearer <access_token>`
- **Interactive docs**: `http://127.0.0.1:8000/api/v1/docs` (Swagger UI), `http://127.0.0.1:8000/api/v1/redoc` (ReDoc)

### 1.1 Error response format

All error responses use this structure:

```json
{
  "error": {
    "code": "BOOK_NOT_FOUND",
    "message": "Book not found",
    "details": {
      "book_id": 1
    }
  }
}
```

Common error codes: `USER_EXISTS`, `INVALID_CREDENTIALS`, `AUTHOR_NOT_FOUND`, `BOOK_NOT_FOUND`, `REVIEW_NOT_FOUND`, `REVIEW_FORBIDDEN`, `READING_LIST_ENTRY_NOT_FOUND`, `READING_LIST_FORBIDDEN`, `INTERNAL_SERVER_ERROR`.

---

## 2. Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health/ping` | Health check. Returns `{"status": "ok"}`. |

---

## 3. Authentication (`/auth`)

### 3.1 Register – `POST /api/v1/auth/register`

Creates a new user.

**Request (JSON):**

- `username` (string, required, 3–50 chars)
- `email` (string, optional, valid email)
- `password` (string, required, 6–128 chars)

**Response 201:** User object (`id`, `username`, `email`, `is_active`, `is_admin`, `created_at`).

**Errors:**

- `400 USER_EXISTS` – Username or email already registered.

**Example:**

```json
// Request
{"username": "alice", "email": "alice@example.com", "password": "password123"}

// Response 201
{"id": 1, "username": "alice", "email": "alice@example.com", "is_active": true, "is_admin": false, "created_at": "2026-03-18T12:00:00"}
```

### 3.2 Login – `POST /api/v1/auth/login`

Returns a JWT access token. Use **form-url-encoded** body (not JSON).

**Request (application/x-www-form-urlencoded):**

- `username` (string)
- `password` (string)

**Response 200:**

```json
{"access_token": "<JWT>", "token_type": "bearer"}
```

**Errors:**

- `401 INVALID_CREDENTIALS` – Incorrect username or password.

### 3.3 Current user – `GET /api/v1/auth/me`

Returns the authenticated user. **Requires:** `Authorization: Bearer <token>`.

**Response 200:** User object (same shape as register response).

**Errors:**

- `401` – Missing or invalid token.

---

## 4. Authors (`/authors`)

All author resources. Create/Update/Delete require **admin** (JWT of a user with `is_admin=true`).

### 4.1 List authors – `GET /api/v1/authors`

**Query parameters:**

- `skip` (int, default 0) – Pagination offset
- `limit` (int, default 20, max 100) – Page size
- `search` (string, optional) – Filter by name (substring, case-insensitive)

**Response 200:** Array of author objects: `id`, `name`, `country`, `biography`.

### 4.2 Create author – `POST /api/v1/authors`

**Auth:** Admin only.

**Request (JSON):**

- `name` (string, required, max 100)
- `country` (string, optional, max 100)
- `biography` (string, optional)

**Response 201:** Author object.

**Errors:**

- `403` – Not admin.

### 4.3 Get author – `GET /api/v1/authors/{author_id}`

**Response 200:** Author object.

**Errors:**

- `404 AUTHOR_NOT_FOUND` – `details.author_id` given.

### 4.4 Update author – `PUT /api/v1/authors/{author_id}`

**Auth:** Admin only. Body: partial author fields (`name`, `country`, `biography`).

**Response 200:** Updated author object.

**Errors:**

- `404 AUTHOR_NOT_FOUND`, `403` if not admin.

### 4.5 Delete author – `DELETE /api/v1/authors/{author_id}`

**Auth:** Admin only.

**Response 204:** No content.

**Errors:**

- `404 AUTHOR_NOT_FOUND`, `403` if not admin.

---

## 5. Books (`/books`)

### 5.1 List books – `GET /api/v1/books`

**Query parameters:**

- `skip`, `limit` – Pagination
- `search` (string) – Substring search on title
- `author_id` (int) – Filter by author
- `genre` (string) – Filter by `main_genre`
- `order_by` (string) – One of: `title`, `rating`, `ratings_count` (default `title`)

**Response 200:** Array of book objects: `id`, `title`, `isbn`, `publication_date`, `description`, `cover_image_url`, `main_genre`, `author_id`, `average_rating`, `ratings_count`.

### 5.2 Create book – `POST /api/v1/books`

**Auth:** Admin only.

**Request (JSON):** `title` (required), `isbn`, `publication_date`, `description`, `cover_image_url`, `main_genre`, `author_id`, etc.

**Response 201:** Book object.

**Errors:**

- `403` – Not admin.

### 5.3 Get book – `GET /api/v1/books/{book_id}`

**Response 200:** Book object.

**Errors:**

- `404 BOOK_NOT_FOUND` – `details.book_id` given.

### 5.4 Update book – `PUT /api/v1/books/{book_id}`

**Auth:** Admin only. Body: partial book fields.

**Response 200:** Updated book object.

**Errors:**

- `404 BOOK_NOT_FOUND`, `403` if not admin.

### 5.5 Delete book – `DELETE /api/v1/books/{book_id}`

**Auth:** Admin only.

**Response 204:** No content.

**Errors:**

- `404 BOOK_NOT_FOUND`, `403` if not admin.

### 5.6 Recalculate book rating – `POST /api/v1/books/{book_id}/recalculate-rating`

**Auth:** Admin only. Recomputes `average_rating` and `ratings_count` from all reviews for this book.

**Response 200:** Updated book object.

**Errors:**

- `404 BOOK_NOT_FOUND`, `403` if not admin.

---

## 6. Reviews (`/reviews`)

### 6.1 List reviews – `GET /api/v1/reviews`

**Query parameters:**

- `skip`, `limit` – Pagination
- `book_id` (int) – Filter by book
- `user_id` (int) – Filter by user

**Response 200:** Array of review objects: `id`, `rating`, `review_text`, `book_id`, `user_id`, `created_at`.

### 6.2 Create review – `POST /api/v1/reviews`

**Auth:** Any authenticated user. The review is tied to the current user.

**Request (JSON):**

- `book_id` (int, required)
- `rating` (int, required, 1–5)
- `review_text` (string, optional)

**Response 201:** Review object. Book’s `average_rating` and `ratings_count` are updated automatically.

**Errors:**

- `404 BOOK_NOT_FOUND` – Book does not exist.
- `401` – Not authenticated.

### 6.3 Update review – `PUT /api/v1/reviews/{review_id}`

**Auth:** Review owner or admin. Body: `rating` (1–5), `review_text`. Book stats are recalculated after update.

**Response 200:** Updated review object.

**Errors:**

- `404 REVIEW_NOT_FOUND`, `403 REVIEW_FORBIDDEN` if not owner/admin.

### 6.4 Delete review – `DELETE /api/v1/reviews/{review_id}`

**Auth:** Review owner or admin. Book stats are recalculated after delete.

**Response 204:** No content.

**Errors:**

- `404 REVIEW_NOT_FOUND`, `403 REVIEW_FORBIDDEN` if not owner/admin.

---

## 7. Reading list (`/reading-list`)

All endpoints require authentication. Operations apply to the current user’s list.

### 7.1 List my reading list – `GET /api/v1/reading-list`

**Auth:** Required.

**Query parameters:** `skip`, `limit`.

**Response 200:** Array of reading list entries: `id`, `user_id`, `book_id`, `added_at`.

### 7.2 Add to reading list – `POST /api/v1/reading-list`

**Auth:** Required.

**Request (JSON):** `book_id` (int, required). If the book is already in the list, the existing entry is returned.

**Response 201:** Reading list entry object.

**Errors:**

- `404 BOOK_NOT_FOUND` – Book does not exist.
- `401` – Not authenticated.

### 7.3 Remove from reading list – `DELETE /api/v1/reading-list/{entry_id}`

**Auth:** Required. Only the entry owner or admin can delete.

**Response 204:** No content.

**Errors:**

- `404 READING_LIST_ENTRY_NOT_FOUND`, `403 READING_LIST_FORBIDDEN` if not owner/admin.

---

## 8. Analytics & recommendations (`/analytics`)

### 8.1 Book rating distribution – `GET /api/v1/analytics/books/{book_id}/rating-distribution`

Returns the count of 1–5 star ratings for the book.

**Response 200:**

```json
{
  "book_id": 1,
  "distribution": {
    "1": 0,
    "2": 1,
    "3": 2,
    "4": 5,
    "5": 3
  }
}
```

**Errors:**

- `404 BOOK_NOT_FOUND` – `details.book_id` given.

### 8.2 Top rated genres – `GET /api/v1/analytics/genres/top-rated`

**Query parameters:**

- `min_ratings` (int, default 10) – Minimum number of ratings for a genre to be included
- `limit` (int, default 10, max 50)

**Response 200:** Array of objects: `genre`, `ratings_count`, `average_rating`, sorted by average rating descending.

### 8.3 Trending authors – `GET /api/v1/analytics/authors/trending`

Compares recent average rating vs overall average per author (trend score).

**Query parameters:**

- `days` (int, default 180, 1–365) – Look-back window in days
- `limit` (int, default 10, max 50)

**Response 200:** Array of objects: `author_id`, `ratings_count`, `overall_avg`, `recent_avg`, `trend_score`.

### 8.4 User recommendations – `GET /api/v1/analytics/users/me/recommendations`

**Auth:** Required. Returns book recommendations for the current user (content-based: preferred genres from high-rated books, or global top-rated if no reviews).

**Query parameters:**

- `limit` (int, default 10, max 50)

**Response 200:** Array of objects: `book_id`, `title`, `average_rating`, `ratings_count`, `main_genre`.

---

## 9. HTTP status codes summary

- `200` – Success (GET, PUT, many POST responses)
- `201` – Created (POST register, create author/book/review/reading-list entry)
- `204` – No content (DELETE)
- `400` – Bad request (e.g. validation, USER_EXISTS)
- `401` – Unauthorized (missing/invalid token or credentials)
- `403` – Forbidden (insufficient permissions)
- `404` – Not found (resource or BOOK_NOT_FOUND, etc.)
- `500` – Internal server error (unified error shape with code `INTERNAL_SERVER_ERROR`)

---

*Export this file to PDF (e.g. via VS Code Markdown PDF or Pandoc) and place in the repository or link from the technical report as required.*
