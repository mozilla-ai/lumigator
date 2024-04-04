python_sources()

python_distribution(
    name = "mzai_platform_schemas",
    dependencies = [
        ":schemas",
        "src/python/mzai/backend:backend_reqs",
    ],
    provides = python_artifact(
        name = "mzai_platform_schemas",
        version = "0.0.1",
    ),
)
