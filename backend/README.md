# Platform Backend

## Setup

(1) Create a virtual environment and install Poetry for managing dependencies

```
pip install poetry
```

(2) Install all requirements

```
poetry lock && poetry install
```

(3) Launch the application.
Note that the main script must be executed as a Python module (via `python -m`)
to get imports to line up.

```
python -m src.main
```
