
from govapp.apps.publisher import models
from rest_framework import serializers


class GeoServerPoolSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.geoserver_pools.GeoServerPool
        fields = (
            "id",
            "name",
        )