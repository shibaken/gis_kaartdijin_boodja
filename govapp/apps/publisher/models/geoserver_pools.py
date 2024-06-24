"""Kaartdijin Boodja Publisher Django Application GeoserverPool Models."""


# Third-Party
from django.db import models
import reversion
import logging
import httpx
import json

# Local
from govapp.common import mixins
from govapp.common.utils import handle_http_exceptions


log = logging.getLogger(__name__)

@reversion.register()
class GeoServerPool(mixins.RevisionedMixin):
    """Model for an Geoserver Pool."""
    name = models.CharField(max_length=200, null=True)
    url = models.URLField()
    username = models.TextField()
    password = models.TextField()
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        """Geoserver Pool Model Metadata."""
        verbose_name = "Geoserver Pool"
        verbose_name_plural = "Geoserver Pools"

    def __str__(self) -> str:
        """Provides a string representation of the object.

        Returns:
            str: Human readable string representation of the object.
        """
        # Generate String and Return
        return f"{self.id}: {self.name}" if self.name else f'{self.id}'
    
    @property
    def base_url(self):
        return f"{self.url}/rest/security",
    
    @property
    def auth(self):
        return (self.username, self.password)

    @property
    def total_active_layers(self):
        return self.geoserverpublishchannel_set.filter(active=True).count()

    @property
    def total_inactive_layers(self):
        return self.geoserverpublishchannel_set.exclude(active=True).count()

    @property
    def total_layers(self):
        return self.total_active_layers + self.total_inactive_layers

    ### User
    @handle_http_exceptions(log)
    def get_all_users(self):
        response = httpx.get(
            url=f"{self.base_url}/usergroup/users/",
            headers={"Accept": "application/json"},
            auth=self.auth
        )
        response.raise_for_status()
        existing_users = response.json()
        return existing_users['users']

    @handle_http_exceptions(log)
    def update_existing_user(self, user_data):
        response = httpx.post(
            url=f"{self.base_url}/usergroup/user/{user_data['user']['userName']}",
            headers={"Content-Type": "application/json"},
            content=json.dumps(user_data),
            auth=self.auth
        )
        log.info(f"User: [{user_data['user']['userName']}] has been updated successfully in GeoServer: [{self}].")
        return response

    @handle_http_exceptions(log)
    def create_new_user(self, user_data):
        response = httpx.post(
            url=f"{self.base_url}/usergroup/users/",
            headers={"Content-Type": "application/json"},
            content=json.dumps(user_data),
            auth=self.auth
        )
        log.info(f"User: [{user_data['user']['userName']}] has been created successfully in the GeoServer: [{self}].")
        return response

    @handle_http_exceptions(log)
    def delete_existing_user(self, username):
        response = httpx.delete(
            url=f"{self.base_url}/usergroup/user/{username}",
            auth=self.auth
        )
        log.info(f"User: [{username}] has been deleted successfully from the GeoServer: [{self}].")
        return response
    

    ### Group
    @handle_http_exceptions(log)
    def get_all_groups(self):
        response = httpx.get(
            url=f"{self.base_url}/usergroup/groups/",
            headers={"Accept": "application/json"},
            auth=self.auth
        )
        response.raise_for_status()
        existing_groups = response.json()
        return existing_groups['groups']

    @handle_http_exceptions(log)
    def get_all_groups_for_user(self, username):
        response = httpx.get(
            url=f"{self.base_url}/usergroup/user/{username}/groups",
            headers={"Accept": "application/json"},
            auth=self.auth
        )
        response.raise_for_status()
        groups_for_user = response.json()
        return groups_for_user['groups']

    @handle_http_exceptions(log)
    def create_new_group(self, group_name):
        response = httpx.post(
            url=f"{self.base_url}/usergroup/group/{group_name}",
            auth=self.auth
        )
        log.info(f"Group: [{group_name}] has been created successfully in the GeoServer: [{self}].")
        return response

    @handle_http_exceptions(log)
    def delete_existing_group(self, group_name):
        response = httpx.delete(
            url=f"{self.base_url}/usergroup/group/{group_name}",
            auth=self.auth
        )
        log.info(f"Group: [{group_name}] has been deleted successfully from the GeoServer: [{self}].")
        return response

    @handle_http_exceptions(log)
    def associate_user_with_group(self, username, group_name):
        response = httpx.post(
            url=f"{self.base_url}/usergroup/user/{username}/group/{group_name}",
            auth=self.auth
        )
        log.info(f"User: [{username}] has been successfully associated with the group: [{group_name}] in the GeoServer: [{self}].")
        return response

    @handle_http_exceptions(log)
    def disassociate_user_from_group(self, username, group_name):
        response = httpx.delete(
            url=f"{self.base_url}//usergroup/user/{username}/group/{group_name}",
            auth=self.auth
        )
        log.info(f"User: [{username}] has been successfully unassociated from the group: [{group_name}] in the GeoServer: [{self}].")
        return response


    ### Role
    @handle_http_exceptions(log)
    def get_all_roles(self):
        response = httpx.get(
            url=f"{self.base_url}/roles/",
            headers={"Accept": "application/json"},
            auth=self.auth
        )
        response.raise_for_status()
        existing_roles = response.json()
        return existing_roles['roles']
    
    def get_all_roles_for_user(self, username):
        response = httpx.get(
            url=f"{self.base_url}/roles/user/{username}",
            headers={"Accept": "application/json"},
            auth=self.auth
        )
        response.raise_for_status()
        roles_for_user = response.json()
        return roles_for_user['roles']

    def get_all_roles_for_group(self, group_name):
        response = httpx.get(
            url=f"{self.base_url}/roles/group/{group_name}",
            headers={"Accept": "application/json"},
            auth=self.auth
        )
        response.raise_for_status()
        roles_for_group = response.json()
        return roles_for_group['roles']

    def create_new_role(self, role_name):
        response = httpx.post(
            url=f"{self.base_url}/roles/role/{role_name}",
            auth=self.auth
        )
        log.info(f"Role: [{role_name}] has been created successfully in the GeoServer: [{self}].")
        return response

    def delete_existing_role(self, role_name):
        response = httpx.delete(
            url=f"{self.base_url}/roles/role/{role_name}",
            auth=self.auth
        )
        log.info(f"Role: [{role_name}] has been deleted successfully in the GeoServer: [{self}].")
        return response

    def associate_role_with_user(self, role_name, username):
        response = httpx.post(
            url=f"{self.base_url}/roles/role/{role_name}/user/{username}",
            auth=self.auth
        )
        log.info(f"Role: [{role_name}] has been associated successfully with the user: [{username}] in the GeoServer: [{self}].")
        return response

    def disassociate_role_from_user(self, role_name, username):
        response = httpx.delete(
            url=f"{self.base_url}/roles/role/{role_name}/user/{username}",
            auth=self.auth
        )
        log.info(f"Role: [{role_name}] has been disassociated successfully from the user: [{username}] in the GeoServer: [{self}].")
        return response

    def associate_role_with_group(self, role_name, group_name):
        response = httpx.post(
            url=f"{self.base_url}/roles/role/{role_name}/group/{group_name}",
            auth=self.auth
        )
        log.info(f"Role: [{role_name}] has been associated successfully with the group: [{group_name}] in the GeoServer: [{self}].")
        return response

    def disassociate_role_with_group(self, role_name, group_name):
        response = httpx.delete(
            url=f"{self.base_url}/roles/role/{role_name}/group/{group_name}",
            auth=self.auth
        )
        log.info(f"Role: [{role_name}] has been disassociated successfully from the group: [{group_name}] in the GeoServer: [{self}].")
        return response
