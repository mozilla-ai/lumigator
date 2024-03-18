import uvicorn
from fastapi import FastAPI

app = FastAPI(title="MZAI Platform")


@app.get("/")
async def root():
    return {"message": "Welcome to the MZAI Platform!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
