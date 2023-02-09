"""Kaartdijin Boodja Logs Django Application Views."""


# Third-Party
from drf_spectacular import utils as drf_utils
from rest_framework import viewsets

# Local
from govapp.common import mixins
from govapp.apps.logs import models
from govapp.apps.logs import serializers


@drf_utils.extend_schema(tags=["Logs - Communications Logs"])
class CommunicationsLogEntryViewSet(
    mixins.ChoicesMixin,
    viewsets.GenericViewSet,
):
    """Communications Log Entry View Set."""
    queryset = models.CommunicationsLogEntry.objects.all()
    serializer_class = serializers.CommunicationsLogEntrySerializer
