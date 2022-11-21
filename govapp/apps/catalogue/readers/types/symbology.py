"""Models for extracted GIS Symbology."""


# Standard
import dataclasses


@dataclasses.dataclass
class Symbology:
    """GIS Symbology."""
    name: str
    sld: str
