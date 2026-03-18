from fastapi import APIRouter

router = APIRouter()


@router.get("/ping", summary="Health check", tags=["health"])
async def ping() -> dict:
    """Simple health check endpoint to verify that the API is running."""

    return {"status": "ok"}

