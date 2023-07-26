"""Kaartdijin Boodja Catalogue Django Serializers."""


# Third-Party
from rest_framework import serializers

# Local
from govapp.apps.catalogue import models
from govapp.apps.catalogue.models.layer_subscriptions import LayerSubscriptionType


class LayerSubscriptionSerializer(serializers.ModelSerializer):
    """Layer Subscription Model Serializer."""
    class Meta:
        """Layer Subscription Model Serializer Metadata."""
        model = models.layer_subscriptions.LayerSubscription
        fields = ("id", "name", "description", "type", "enabled", 
                  "url", "connection_timeout", "max_connections", "min_connections", 
                  "read_timeout", "created_at", "updated_at", "workspace", 
                  "host", "port", "database", "schema", "fetch_size")
        read_only_fields = fields
        
class LayerSubscriptionCreateSerializer(serializers.ModelSerializer):
    """Layer Subscription Model Serializer."""
    url = serializers.URLField(required=False) # required if type is WMS or WFS
    max_connections = serializers.IntegerField(required=False) # required if type is WMS or POST GIS
    read_timeout = serializers.IntegerField(required=False) # required if type is WMS
    min_connections = serializers.IntegerField(required=False) # required if type is POST GIS
    host = serializers.CharField(required=False) # required if type is POST GIS
    port = serializers.IntegerField(required=False) # required if type is POST GIS
    database = serializers.CharField(required=False) # required if type is POST GIS
    schema = serializers.CharField(required=False) # required if type is POST GIS
    fetch_size = serializers.IntegerField(required=False) # required if type is POST GIS
    
    required_map = {LayerSubscriptionType.WFS:('url',),
                LayerSubscriptionType.WMS:('url', 'max_connections', 'read_timeout'),
                LayerSubscriptionType.POST_GIS:('max_connections', 'min_connections', 'host', 'port', 'database', 'schema', 'fetch_size')}    
    
    def validate_url(self, url):
        return self.validate_conditional_optionals(url, 'url')
    
    def validate_max_connections(self, max_connections):
        return self.validate_conditional_optionals(max_connections, 'max_connections')
    
    def validate_min_connections(self, min_connections):
        return self.validate_conditional_optionals(min_connections, 'min_connections')
    
    def validate_read_timeout(self, read_timeout):
        return self.validate_conditional_optionals(read_timeout, 'read_timeout')
    
    def validate_host(self, host):
        return self.validate_conditional_optionals(host, 'host')
    
    def validate_port(self, port):
        return self.validate_conditional_optionals(port, 'port')
    
    def validate_database(self, database):
        return self.validate_conditional_optionals(database, 'database')
    
    def validate_schema(self, schema):
        return self.validate_conditional_optionals(schema, 'schema')
    
    def validate_fetch_size(self, fetch_size):
        return self.validate_conditional_optionals(fetch_size, 'fetch_size')
     
    def validate_conditional_optionals(self, param, param_name):
        type = self.get_type_by_value(self.initial_data.get('type'))
        if param_name in self.required_map[type] and not param:
            raise serializers.ValidationError(f"Value of '{param_name}' is required when the type is {type}.")
        return param
        
    def get_type_by_value(self, value):
        for type in LayerSubscriptionType:
            if type.value == int(value):
                return type
        raise serializers.ValidationError(f"A member has value '{value}' does not exist in LayerSubscriptionType.")
        
        
    class Meta:
        """Layer Subscription Model Serializer Metadata."""
        model = LayerSubscriptionSerializer.Meta.model
        fields = ("name", "description", "type", "enabled", 
                  "url", "username", "userpassword", "connection_timeout", "max_connections", "min_connections",
                  "read_timeout", "created_at", "updated_at", "workspace",
                  "host", "port", "database", "schema", "fetch_size")