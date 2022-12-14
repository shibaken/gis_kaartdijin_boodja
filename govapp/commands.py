"""Kaartdijin Boodja Catalogue Django Application Command Views."""


# Standard
import logging

# Third-Party
from django import conf
from django.core import management
from drf_spectacular import utils as drf_utils
from rest_framework import decorators
from rest_framework import request
from rest_framework import response
from rest_framework import routers
from rest_framework import status
from rest_framework import viewsets

# Local
from .apps.accounts import permissions

# Logging
log = logging.getLogger(__name__)


@drf_utils.extend_schema(tags=["Management Commands"])
class ManagementCommands(viewsets.ViewSet):
    """Management Commands View Set."""
    permission_classes = [permissions.IsInAdministratorsGroup]

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
            # Here, instead of directly running the `scan` management command
            # we run it via the `runcrons` command. This allows us to take
            # advantage of the builtin locking functionality - i.e., we won't
            # be able to run the scanner if its already running. The `--force`
            # option is used to allow us to call the scanner whenever we want,
            # but it does not bypass the concurrency locking.
            management.call_command("runcrons", conf.settings.CRON_SCANNER_CLASS, "--force")

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
