import re

import pytest
from lumigator_schemas.redactor import Redactor

sensitive_patterns = [
    re.compile(r"password", re.IGNORECASE),
    re.compile(r"api_key", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
]


@pytest.mark.parametrize(
    "redaction_value, input_data, expected_output",
    [
        # Default redaction value
        ("<REDACTED>", {"password": "12345"}, {"password": "<REDACTED>"}),
        # Custom redaction value
        ("***HIDDEN***", {"api_key": "abcdef"}, {"api_key": "***HIDDEN***"}),
        # Case-insensitive match
        ("MASKED", {"PaSsWoRd": "12345"}, {"PaSsWoRd": "MASKED"}),
        # Nested dictionary
        (
            "REMOVED",
            {"user": {"password": "mypassword"}},  # pragma: allowlist secret
            {"user": {"password": "REMOVED"}},  # pragma: allowlist secret
        ),  # pragma: allowlist secret
        # List inside dictionary
        ("FILTERED", {"tokens": [{"api_key": "abcdef"}]}, {"tokens": [{"api_key": "FILTERED"}]}),
        # Mixed case and non-sensitive data should remain unchanged
        ("<REDACTED>", {"username": "john_doe", "api_key": "xyz"}, {"username": "john_doe", "api_key": "<REDACTED>"}),
        # Lists with non-sensitive data should remain unchanged
        ("<REDACTED>", {"data": ["hello", "world"]}, {"data": ["hello", "world"]}),
        # Redaction should not trigger based on values
        ("MASKED", {"key": "my password is 12345"}, {"key": "my password is 12345"}),
        # Nested structures with multiple sensitive keys
        (
            "HIDDEN",
            {"config": {"api_key": "abcdef", "nested": {"secret": "hidden"}}},
            {"config": {"api_key": "HIDDEN", "nested": {"secret": "HIDDEN"}}},  # pragma: allowlist secret
        ),
    ],
)
def test_redactor(redaction_value, input_data, expected_output):
    redactor = Redactor(sensitive_patterns, redaction_value=redaction_value)
    assert redactor.redact(input_data) == expected_output
