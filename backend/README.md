# Platform Backend

## Local Setup

(1) Create a virtual environment and install Poetry for managing dependencies.

```
pip install poetry
```

(2) Install requirements.

```
poetry lock && poetry install
```

(3) Launch the application (with auto-reloading).

```
uvicorn src.main:app --reload
```

## Docker

(1) Build the backend Docker image.

```
docker build . -t backend
```

(2) Launch the application (forwarded to port 80 of your local machine).

```
docker run --rm -p 80:80 backend
```

(3) View the API documentation in your browser at `http://0.0.0.0:80/docs`.
