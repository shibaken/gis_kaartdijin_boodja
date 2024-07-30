import pytz
from rest_framework import serializers
from govapp.apps.publisher.models.geoserver_roles_groups import GeoServerGroup, GeoServerGroupUser, GeoServerRole
from django.utils.html import format_html


class GeoServerRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeoServerRole
        fields = [
            'id',
            'name',
            'active',
        ]


class GeoServerGroupSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    users = serializers.SerializerMethodField()
    class Meta:
        model = GeoServerGroup
        fields = [
            'id',
            'name',
            'active',
            'roles',
            'users',
            'created_at',
            'updated_at',
        ]

    def get_created_at(self, obj):
        """Convert published_at to the desired format."""
        if obj.created_at:
            # Convert to local time
            local_time = obj.created_at.astimezone(pytz.timezone('Australia/Perth'))
            # Return formatted string
            return local_time.strftime('%d %b %Y %I:%M %p')
        return None

    def get_updated_at(self, obj):
        """Convert published_at to the desired format."""
        if obj.updated_at:
            # Convert to local time
            local_time = obj.updated_at.astimezone(pytz.timezone('Australia/Perth'))
            # Return formatted string
            return local_time.strftime('%d %b %Y %I:%M %p')
        return None

    def get_roles(self, obj):
        roles = '<br>'.join([role.name for role in obj.geoserver_roles.all()])
        return format_html(roles)

    def get_users(self, obj):
        geoserver_group_users = GeoServerGroupUser.objects.filter(geoserver_group=obj)
        users = '<br>'.join([geoserver_group_user.user.email for geoserver_group_user in geoserver_group_users])
        return format_html(users)