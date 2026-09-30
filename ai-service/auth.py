import os

from fastapi import Header, HTTPException
from dotenv import load_dotenv


load_dotenv()


AI_SERVICE_API_KEY = os.getenv(
    "AI_SERVICE_API_KEY"
)


def verify_ai_service_key(
    x_ai_service_key: str | None = Header(
        default=None
    ),
):
    if not AI_SERVICE_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="AI service authentication is not configured",
        )

    if not x_ai_service_key:
        raise HTTPException(
            status_code=401,
            detail="Missing AI service authentication",
        )

    if x_ai_service_key != AI_SERVICE_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid AI service authentication",
        )

    return True