from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import settings
from app.schemas.common import ErrorResponse, ErrorDetail

# Tags for clearer Swagger/ReDoc grouping and descriptions
OPENAPI_TAGS = [
    {"name": "health", "description": "Service health check."},
    {"name": "auth", "description": "Register, login, and current user (JWT)."},
    {"name": "authors", "description": "Author CRUD. Create/update/delete require admin."},
    {"name": "books", "description": "Book CRUD and rating recalculation. Create/update/delete require admin."},
    {"name": "reviews", "description": "Review CRUD. Users can create and manage their own reviews."},
    {"name": "reading-list", "description": "Current user's reading list (add/remove books)."},
    {"name": "analytics", "description": "Rating distribution, top genres, trending authors, recommendations."},
]


def custom_openapi(app: FastAPI):
    """Build OpenAPI schema and rename auto-generated schema names for a cleaner docs UI."""
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description="REST API for book metadata, reviews, reading lists, and analytics. "
        "Use **Authorize** to log in (username/password); then locked endpoints will use your token.",
        routes=app.routes,
        tags=OPENAPI_TAGS,
    )
    # Rename ugly auto-generated request body schema (e.g. Body_login_for_access_token_api_v1_auth_login_post)
    schemas = openapi_schema.get("components", {}).get("schemas", {})
    refs_to_fix = []
    for key in list(schemas.keys()):
        if "Body_login" in key and "auth_login" in key:
            new_key = "LoginRequest"
            schemas[new_key] = schemas.pop(key)
            refs_to_fix.append((key, new_key))
            break
    for old_key, new_key in refs_to_fix:
        old_ref = f"#/components/schemas/{old_key}"
        new_ref = f"#/components/schemas/{new_key}"
        for path_item in openapi_schema.get("paths", {}).values():
            for op in path_item.values():
                if not isinstance(op, dict):
                    continue
                for content in op.get("requestBody", {}).get("content", {}).values():
                    if content.get("schema", {}).get("$ref") == old_ref:
                        content["schema"]["$ref"] = new_ref
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def create_application() -> FastAPI:
    """Application factory used by Uvicorn and tests."""

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="0.1.0",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    )
    app.openapi = lambda: custom_openapi(app)

    # CORS
    app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"] if settings.BACKEND_CORS_ORIGINS == "*" else settings.BACKEND_CORS_ORIGINS.split(","),
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
    )

    # Routers
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # Global exception handler for unexpected errors to return unified error shape
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:  # type: ignore[override]
        error = ErrorResponse(
            error=ErrorDetail(code="INTERNAL_SERVER_ERROR", message="An unexpected error occurred", details=None)
        )
        return JSONResponse(status_code=500, content=error.model_dump())

    return app


app = create_application()

