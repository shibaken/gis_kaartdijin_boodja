"""Models for extracted GIS Attributes."""


# Standard
import dataclasses


@dataclasses.dataclass
class Attribute:
    """GIS Attribute."""
    name: str
    type: str  # noqa: A003
    order: int
