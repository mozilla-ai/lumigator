# Platform Backend

## Setup

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
