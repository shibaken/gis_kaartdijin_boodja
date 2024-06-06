"""Models for extracted GIS Metadata."""


# Standard
import dataclasses
import datetime
from typing import Any, Dict


@dataclasses.dataclass
class Attribute:
    """GIS Attribute."""
    name: str
    type: str  # noqa: A003
    order: int


@dataclasses.dataclass
class Metadata:
    """GIS Metadata."""
    name: str
    description: str
    created_at: datetime.datetime
    additional_data: Dict[str, Any] = dataclasses.field(default_factory=dict) 


@dataclasses.dataclass
class Symbology:
    """GIS Symbology."""
    name: str
    sld: str
