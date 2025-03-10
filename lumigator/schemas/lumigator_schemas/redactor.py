import re
from typing import Any


class Redactor:
    def __init__(self, sensitive_patterns: list[re.Pattern], redaction_value: str = "<REDACTED>"):
        """Initializes the redactor with a list of sensitive key patterns and an optional redaction value.

        :param sensitive_patterns: List of compiled regex patterns for sensitive keys.
        :param redaction_value: The value to replace sensitive fields with, defaults to <REDACTED>.
        """
        self.sensitive_patterns = sensitive_patterns
        self.redaction_value = redaction_value

    def redact(self, data: dict[str, Any]) -> dict[str, Any]:
        """Recursively traverses the supplied dictionary redacting sensitive
        string values based on matching patterns with the key.

        :param data: Dictionary data to redact
        :return dict: The input data with sensitive values redacted
        """

        def redact_value(key: str, value: Any) -> Any:
            if isinstance(value, dict):
                return {k: redact_value(k, v) for k, v in value.items()}
            elif isinstance(value, list):
                return [redact_value(key, v) for v in value]  # Use parent key for lists
            elif hasattr(value, "__dict__"):
                return {k: redact_value(k, v) for k, v in value.__dict__.items()}  # Treat objects like dicts
            elif any(pattern.search(key) for pattern in self.sensitive_patterns):
                return self.redaction_value
            return value

        return {k: redact_value(k, v) for k, v in data.items()}
