python_sources(
    name = "schemas",
    dependencies = [
        "backend/3rdparty/python:3rdparty#ray",
        "backend/3rdparty/python:3rdparty#pydantic",
        "backend/3rdparty/python:3rdparty#pydantic-settings",
    ],
)

python_distribution(
    name = "pydantic_schemas",
    dependencies = [
        ":schemas",
    ],
    provides = python_artifact(
        name = "mzai_pydantic_schemas",
        version = "0.0.1",
    ),
)
