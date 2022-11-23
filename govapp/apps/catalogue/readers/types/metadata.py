"""Models for extracted GIS Metadata."""


# Standard
import dataclasses
import datetime


@dataclasses.dataclass
class Metadata:
    """GIS Metadata."""
    name: str
    description: str
    created_at: datetime.datetime
