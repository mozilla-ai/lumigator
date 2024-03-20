import uvicorn

from src.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "src.server:app",
        reload=settings.ENVIRONMENT != "production",
    )
