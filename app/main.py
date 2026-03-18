from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import settings
from app.schemas.common import ErrorResponse, ErrorDetail


def create_application() -> FastAPI:
    """Application factory used by Uvicorn and tests."""

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="0.1.0",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    )

    # CORS
    app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"] if settings.BACKEND_CORS_ORIGINS == "*" else settings.BACKEND_CORS_ORIGINS.split(","),
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
    )

    # Root: point users to API docs and health
    @app.get("/")
    async def root():
        return {
            "message": "Book Metadata, Review & Insight API",
            "docs": f"{settings.API_V1_PREFIX}/docs",
            "redoc": f"{settings.API_V1_PREFIX}/redoc",
            "health": f"{settings.API_V1_PREFIX}/health/ping",
        }

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

