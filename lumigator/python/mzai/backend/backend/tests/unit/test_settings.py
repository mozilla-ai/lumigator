import pytest


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("", []),
        ("   ", []),
        ("http://localhost:3000", ["http://localhost:3000"]),
        (
            "http://localhost:3000,http://localhost:8080",
            ["http://localhost:3000", "http://localhost:8080"],
        ),
        (
            " http://localhost:3000 , http://localhost:8080 ",
            ["http://localhost:3000", "http://localhost:8080"],
        ),
        ("*", ["*"]),
        (
            "http://localhost:3000,*",
            ["*"],
        ),
        (
            " http://localhost:3000,http://localhost:8080,",
            ["http://localhost:3000", "http://localhost:8080"],
        ),
        (
            ",,,",
            [],
        ),
    ],
)
def test_api_allowed_origins(backend_settings, test_input, expected):
    """Ensure that our backend setting for getting CORS allowed origins
    handles being empty, whitespace and when containing one or more entries.
    """
    # Temporarily override the config value that was loaded from env.
    backend_settings._api_cors_allowed_origins = test_input

    result = backend_settings.API_CORS_ALLOWED_ORIGINS
    assert result == expected
