from typing import Any

from sqlalchemy import JSON
from sqlalchemy.orm import DeclarativeBase

from app.records.mixins import PrimaryKeyMixin


class BaseRecord(DeclarativeBase, PrimaryKeyMixin):
    """Base class for declarative SQLAlchemy mappings.

    Commonly, these mappings are referred to as "models".
    However, "model" is an incredibly overloaded term on the platform,
    so we're using the term "record" instead to indicate that instances of these classes
    generally correspond to single records (i.e., rows) in a DB table.
    """

    # Additional mappings from Python type to SQLAlchemy type
    type_annotation_map = {dict[str, Any]: JSON}
