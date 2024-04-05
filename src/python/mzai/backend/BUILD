python_requirements(
    name = "backend_deps",
    overrides = {
        "ray": {"dependencies": [":backend_deps#setuptools"]},
        "sqlalchemy": {"dependencies": [":backend_deps#psycopg2-binary"]},
    },
    source = "pyproject.toml",
)

python_sources(
    name = "backend",
)

pex_binary(
    name = "backend_fastapi_app",
    args = [
        "mzai.backend.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "80",
    ],
    complete_platforms = [
        "pants_tools:ubuntu_2204_py310",
        "pants_tools:macosx_py310",
    ],
    dependencies = [
        ":backend",  # defined implicitly by `python_sources()`
        ":backend_deps",
        "src/python/mzai/backend/schemas:schemas",
    ],
    execution_mode = "venv",
    include_sources = True,
    script = "uvicorn",
)

pex_binary(
    name = "backend_pex_for_ide",
    dependencies = [
        ":backend_deps",
        ":schemas",
    ],
    execution_mode = "venv",
    include_sources = True,
    include_tools = True,
)

docker_image(
    name = "mzai_backend",
    build_platform = ["linux/amd64"],
    dependencies = [":backend_fastapi_app"],
    image_tags = [
        "dev",
        "0.1",
    ],
    repository = "{directory}/{name}",
    source = "Dockerfile",
)
