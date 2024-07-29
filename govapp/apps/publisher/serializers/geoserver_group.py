from rest_framework import serializers
from govapp.apps.publisher.models.geoserver_roles_groups import GeoServerGroup


class GeoServerGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeoServerGroup
        fields = ['id', 'name',]