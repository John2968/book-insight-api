from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import settings


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

    # Routers
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_application()

