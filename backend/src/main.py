import uvicorn

from src.core.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "src.core.server:app",
        reload=settings.ENVIRONMENT != "production",
    )
