"""Models for extracted GIS Metadata."""


# Standard
import dataclasses
import datetime


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


@dataclasses.dataclass
class Symbology:
    """GIS Symbology."""
    name: str
    sld: str
