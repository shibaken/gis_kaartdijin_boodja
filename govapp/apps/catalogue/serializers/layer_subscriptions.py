"""Kaartdijin Boodja Catalogue Django Serializers."""


# Third-Party
from rest_framework import serializers

# Local
from govapp.apps.catalogue import models
from govapp.apps.catalogue import utils
from govapp.apps.catalogue.models.layer_subscriptions import LayerSubscriptionType

required_map = {
            LayerSubscriptionType.WMS:{'url', 'max_connections', 'read_timeout'},
            LayerSubscriptionType.WFS:{'url',},
            LayerSubscriptionType.POST_GIS:{'max_connections', 'min_connections', 'host', 'port', 'database', 'schema', 'fetch_size'}}

all_fields = set()
for key in required_map:
    for field in required_map[key]:
        all_fields.add(field)

# fields that must not be included by each types
forbidden_map = {
            LayerSubscriptionType.WMS:
                {field for field in all_fields if field not in required_map[LayerSubscriptionType.WMS]},
            LayerSubscriptionType.WFS:
                {field for field in all_fields if field not in required_map[LayerSubscriptionType.WFS]},
            LayerSubscriptionType.POST_GIS:
                {field for field in all_fields if field not in required_map[LayerSubscriptionType.POST_GIS]}}

class LayerSubscriptionSerializer(serializers.ModelSerializer):
    """Layer Subscription Model Serializer."""
    assigned_to_first_name = serializers.ReadOnlyField(source='assigned_to.first_name',)
    assigned_to_last_name = serializers.ReadOnlyField(source='assigned_to.last_name',)
    updated_at = serializers.SerializerMethodField()

    class Meta:
        """Layer Subscription Model Serializer Metadata."""
        model = models.layer_subscriptions.LayerSubscription
        fields = ("id", "name", "description", "type", "enabled",
                  "url", "connection_timeout", "max_connections", "min_connections", 
                  "read_timeout", "created_at", "updated_at", "workspace", 
                  "host", "port", "database", "schema", "fetch_size", "status", 
                  "assigned_to_first_name", "assigned_to_last_name")
        read_only_fields = ("id", "assigned_to", "status", "created_at", "updated_at")

    def get_updated_at(self, obj):
        return obj.updated_at.strftime("%d-%m-%Y %H:%M:%S")

        
class LayerSubscriptionCreateSerializer(serializers.ModelSerializer):
    """Layer Subscription Model Serializer."""
    description = serializers.CharField(required=False)
    # connection_timeout = serializers.IntegerField() 
    
    def validate(self, data):
        # check property values
        type_key = data['type']
        type_name = utils.find_enum_by_value(LayerSubscriptionType, type_key).name.replace('_', ' ')
        # check required
        for key in required_map[type_key]:
            if key not in data or data[key] == None or (type(data[key]) == 'str' and data[key] == ""):
                raise serializers.ValidationError(f"A member value '{key}' is required when type is '{type_name}'.")
            
        # check forbidden or should they be removed?
        for key in forbidden_map[type_key]:
            if key in data:
                raise serializers.ValidationError(f"A member value '{key}' must not be included in the request when type is '{type_name}'.")
        
        return data
        
    class Meta:
        """Layer Subscription Model Serializer Metadata."""
        model = LayerSubscriptionSerializer.Meta.model
        fields = ("name", "description", "type", "enabled", 
                  "url", "username", "userpassword", "connection_timeout", "max_connections", "min_connections",
                  "read_timeout", "created_at", "updated_at", "workspace",
                  "host", "port", "database", "schema", "fetch_size", "status", "assigned_to")
        
class LayerSubscriptionUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    workspace = serializers.IntegerField(required=False)
    username = serializers.CharField(required=False, allow_blank=True)
    userpassword = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        """Layer Subscription Model Serializer Metadata."""
        model = models.layer_subscriptions.LayerSubscription
        fields = ("__all__")
        read_only_fields = ('id', 'created_at', 'updated_at', 'status', 'assugned_to', 'assugned_to_id')
        
    def validate(self, data):
        type = data['type']
        type_name = utils.find_enum_by_value(LayerSubscriptionType, type).name.replace('_', ' ')
        
        forbidden_list = list(forbidden_map[type])
        
        # check forbidden or should they be removed?
        for key in forbidden_list:
            if key in data:
                raise serializers.ValidationError(f"A member value '{key}' must not be included in the request when type is '{type_name}'.")
            
        return data
