# Generative AI Declaration

**Module:** COMP3011 Web Services and Web Data  
**Assignment:** Coursework 1 – Individual Web Services API Development Project  
**Project:** Book Metadata, Review & Insight API  

---

## Declaration

I declare that I have used Generative AI tools in this assessment in accordance with the module’s “Green Light” policy. I have documented below the tools, purposes, and extent of use, and I have attached (or will attach) sample conversation logs as supplementary material where required.

---

## Tools Used

| Tool / product   | Purpose |
|------------------|--------|
| Cursor (AI-assisted editor) | API structure, Pydantic schemas, route handlers, database models, test fixtures and test cases, error-handling and exception helpers, README and documentation structure, CSV import script, technical report and GenAI declaration drafting. |
| Other (e.g. ChatGPT / Copilot / Claude) | Explaining FastAPI and OpenAPI behaviour, JWT and OAuth2 flow, pytest-asyncio usage, and reviewing wording for the report. |

---

## How GenAI Was Used

- **Design and architecture:** I used AI to explore REST endpoint design, unified error response formats, and layered structure (routes, schemas, models). I chose the final endpoint set, status codes, and role-based access rules myself.
- **Implementation:** AI suggested FastAPI dependency injection, JWT creation/validation, and CRUD patterns. I adapted these to the project, wrote and adjusted the auth and CRUD routes, and implemented analytics and the CSV import script.
- **Testing:** AI helped generate pytest fixtures (in-memory DB, client, session) and example tests. I modified assertions, fixed session isolation so admin role is set in the same DB as the test client, and verified all tests pass.
- **Documentation:** The API documentation outline and README sections (setup, data loading, deployment) were drafted with AI; I revised and completed the content. The technical report outline and this declaration were drafted with AI; I filled in the technical details and ensured accuracy.
- **Report:** AI was used to improve clarity and structure of the technical report; all technical content reflects my own understanding and design decisions.

---

## My Own Contribution

- I defined the data model (users, authors, books, reviews, reading lists) and their relationships and validated them against the assignment and project scope.
- I implemented and reviewed all application code, including security (JWT, password hashing, admin checks) and error handling.
- I ran the application and tests locally and fixed issues (e.g. test DB session, dependency versions, CSV import column mapping).
- I made all final decisions on technology stack (FastAPI, SQLite/PostgreSQL, Alembic, pytest), API shape, and deployment approach.
- I wrote and revised the technical report and this declaration; I am responsible for the accuracy of the submitted materials.

---

## Limitations and Verification

- AI was not used to run the application or execute tests; I ran these myself.
- I checked AI-suggested code for correctness, security (e.g. password hashing, token handling), and consistency with the chosen design.
- Where AI output was incomplete or incorrect (e.g. fixture scope, session isolation for admin tests, OpenAPI schema customisation), I corrected it.
- I did not submit AI-generated text as my own without review; the report and declaration reflect my understanding and choices.

---

## Supplementary Material

- Sample conversation exports (e.g. PDF or markdown of relevant Cursor or other AI conversations) are attached as required by the module. *[Insert file names or “See appendix in submitted PDF” when you attach them.]*

---

*Sign and date as required by your module. Keep this document in your submission (e.g. as an appendix to the Technical Report PDF) and ensure the full declaration is included as specified in the coursework brief.*
