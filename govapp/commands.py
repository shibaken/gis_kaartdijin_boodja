"""Kaartdijin Boodja Catalogue Django Application Command Views."""


# Standard
import logging

# Third-Party
from django.core import management
from drf_spectacular import utils as drf_utils
from rest_framework import decorators
from rest_framework import permissions
from rest_framework import request
from rest_framework import response
from rest_framework import routers
from rest_framework import status
from rest_framework import viewsets


# Logging
log = logging.getLogger(__name__)


@drf_utils.extend_schema(tags=["Management Commands"])
class ManagementCommands(viewsets.ViewSet):
    """Management Commands View Set."""
    permission_classes = [permissions.IsAdminUser]

    @drf_utils.extend_schema(request=None, responses={status.HTTP_204_NO_CONTENT: None})
    @decorators.action(detail=False, methods=["POST"], url_path=r"absorb/(?P<file>[^/]+)")
    def absorb(self, request: request.Request, file: str) -> response.Response:
        """Runs the `absorb` Management Command.

        Args:
            request (request.Request): API request.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Handle Errors
        try:
            # Run Management Command
            management.call_command("absorb", file)

        except Exception as exc:
            # Log
            log.error(f"Unable to perform absorb on '{file}': {exc}")

        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @drf_utils.extend_schema(request=None, responses={status.HTTP_204_NO_CONTENT: None})
    @decorators.action(detail=False, methods=["POST"])
    def scan(self, request: request.Request) -> response.Response:
        """Runs the `scan` Management Command.

        Args:
            request (request.Request): API request.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Handle Errors
        try:
            # Run Management Command
            management.call_command("scan")

        except Exception as exc:
            # Log
            log.error(f"Unable to perform scan: {exc}")

        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)


# Router
router = routers.DefaultRouter()
router.register("commands", ManagementCommands, basename="commands")

# Commands URL Patterns
urlpatterns = router.urls
