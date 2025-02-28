from abc import ABC, abstractmethod
from typing import Any, ClassVar

from pydantic import BaseModel, model_validator

from lumigator_schemas.redactor import Redactor


class RedactableBaseModel(BaseModel, ABC):
    """Redactable base model represents a base model that can have its values redacted before model validation.

    To enable redaction a model must be assigned a ``Redactor`` before validation occurs.

    Subclasses are free to override `redact` to apply custom redaction logic. If overridden,
    it is recommended to call `super().redact(values)` to apply the base redaction functionality.
    """

    # Redactor should be assigned per model.
    redactor: ClassVar[Redactor] = None

    @abstractmethod
    @model_validator(mode="before")
    @classmethod
    def redact(cls, values: dict[str, Any]) -> dict[str, Any]:
        """When a ``Redactor`` is configured, redacts string values when keys match the specified
        sensitive patterns configured on the ``Redactor``.

        Called by the Pydantic framework before a model is created.
        Model's can create their own 'before' model validation.
        """
        if cls.redactor:
            values = cls.redactor.redact(values)

        return values
