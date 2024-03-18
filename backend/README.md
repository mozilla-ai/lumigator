# Platform Backend

## Setup

(1) Create a virtual environment

(2) Install all requirements

```
pip install -r requirements.txt -r dev.txt
```

(3) Launch the application (with reloading enabled)

```
uvicorn app.main:app --reload
```

(4) Navigate to `http://127.0.0.1:8000/docs` to view the API docs
