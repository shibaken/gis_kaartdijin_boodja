"""Kaartdijin Boodja Catalogue Django Application Validators."""


# Third-Party
from django.core import exceptions
from lxml import etree  # noqa: S410

# Local
from govapp import gis


def validate_xml(value: str) -> None:
    """Validates XML String.

    Args:
        value (str): Value to be validated.

    Raises:
        ValidationError: Raised if the value is deemed invalid.
    """
    # Handle Errors
    try:
        # Validate
        etree.XML(value.encode("UTF-8"))

    except Exception as exc:
        # Re-Raise as ValidationError
        raise exceptions.ValidationError(str(exc))


def validate_sld(value: str) -> None:
    """Validates SLD XML String.

    Args:
        value (str): Value to be validated.

    Raises:
        ValidationError: Raised if the value is deemed invalid.
    """
    # Validate SLD with GeoServer
    result = gis.geoserver.GeoServer().validate_style(value)

    # Check
    if result:
        # Raise Validation Error
        raise exceptions.ValidationError(result["title"])
