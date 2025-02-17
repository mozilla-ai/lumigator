from typing import Any, ClassVar

from pydantic import BaseModel, model_validator

from lumigator_schemas.redactor import Redactor


class RedactableBaseModel(BaseModel):
    """Redactable base model represents a base model that can have its values redacted.

    It wraps the underlying ``BaseModel``, to enable redaction a model must be assigned a
     ``Redactor`` before validation occurs.
    """

    # Redactor should be assigned per model.
    redactor: ClassVar[Redactor]

    @model_validator(mode="before")
    @classmethod
    def parse(cls, values: dict[str, Any]) -> dict[str, Any]:
        """When a ``Redactor`` is configured, redacts values if keys match the specified
        sensitive patterns configured on the ``Redactor``.

        Called by the Pydantic framework before a model is created.
        Model's can create their own 'before' model validation.
        """
        if cls.redactor:
            values = cls.redactor.redact(values)

        return values
