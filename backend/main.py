import uvicorn

from core.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "core.server:app",
        reload=settings.ENVIRONMENT != "production",
    )
