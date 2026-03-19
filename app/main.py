from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
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

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:  # type: ignore[override]
        detail = exc.detail

        if isinstance(detail, dict) and "error" in detail:
            payload = detail
        elif isinstance(detail, dict) and {"code", "message"}.issubset(detail):
            payload = ErrorResponse(error=ErrorDetail(**detail)).model_dump()
        else:
            payload = ErrorResponse(
                error=ErrorDetail(
                    code=f"HTTP_{exc.status_code}",
                    message=str(detail),
                    details=None,
                )
            ).model_dump()

        return JSONResponse(status_code=exc.status_code, content=payload, headers=exc.headers)

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:  # type: ignore[override]
        error = ErrorResponse(
            error=ErrorDetail(
                code="VALIDATION_ERROR",
                message="Request validation failed",
                details={"errors": exc.errors()},
            )
        )
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content=error.model_dump())

    # Global exception handler for unexpected errors to return unified error shape
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:  # type: ignore[override]
        error = ErrorResponse(
            error=ErrorDetail(code="INTERNAL_SERVER_ERROR", message="An unexpected error occurred", details=None)
        )
        return JSONResponse(status_code=500, content=error.model_dump())

    return app


app = create_application()

