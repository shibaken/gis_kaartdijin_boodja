"""Kaartdijin Boodja Publisher Django Application Views."""


# Third-Party
import os
from datetime import datetime
from django import shortcuts
from django.db import transaction
from django.contrib import auth
from django import http
from drf_spectacular import utils as drf_utils
from rest_framework import decorators
from rest_framework import request
from rest_framework import response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

# Local
from govapp import settings
from govapp.common import mixins
from govapp.common import utils
from govapp.apps.accounts import permissions as accounts_permissions
from govapp.apps.logs import mixins as logs_mixins
from govapp.apps.logs import utils as logs_utils
from govapp.apps.publisher import filters
from govapp.apps.publisher import models
from govapp.apps.publisher import permissions
from govapp.apps.publisher import serializers
from govapp.apps.publisher import geoserver_manager
from govapp.apps.publisher.models.geoserver_queues import GeoServerQueueStatus
from govapp.apps.catalogue.models import catalogue_entries

# Typing
from typing import cast, Any


# Shortcuts
UserModel = auth.get_user_model()


@drf_utils.extend_schema(tags=["Publisher - Publish Entries"])
class PublishEntryViewSet(
    mixins.ChoicesMixin,
    mixins.MultipleSerializersMixin,
    logs_mixins.ActionsLogMixin,
    logs_mixins.CommunicationsLogMixin,
    viewsets.mixins.CreateModelMixin,
    viewsets.mixins.DestroyModelMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Publish Entry View Set."""
    queryset = models.publish_entries.PublishEntry.objects.all()
    serializer_class = serializers.publish_entries.PublishEntrySerializer
    serializer_classes = {"create": serializers.publish_entries.PublishEntryCreateSerializer}
    filterset_class = filters.PublishEntryFilter
    search_fields = ["description", "catalogue_entry__name"]
    permission_classes = [permissions.IsPublishEntryPermissions]

    def list(self, request, *args, **kwargs):
        """Api to return a list of publish entry
            Convert date format of updated_at to %d %b %Y %H:%M %p

        Args:
            request (_type_): request object passed by Django framework

        Returns:
            response.Response: a full list of publish entry
        """
        response = super().list(request, *args, **kwargs)
        for result in response.data.get('results'):
            if result.get('updated_at'):
                date_obj = datetime.strptime(result.get('updated_at'), "%Y-%m-%dT%H:%M:%S.%f%z")
                result['updated_at'] = str(date_obj.astimezone().strftime('%d %b %Y %H:%M %p'))
                 
        return response
    
    @drf_utils.extend_schema(
        parameters=[drf_utils.OpenApiParameter("symbology_only", type=bool)],
        request=None,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    @decorators.action(detail=True, methods=["POST"])
    def publish(self, request: request.Request, pk: str) -> response.Response:
        """Publishes to both channels.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Publish Entry.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Retrieve Publish Entry
        # Help `mypy` by casting the resulting object to a Publish Entry
        publish_entry = self.get_object()
        publish_entry = cast(models.publish_entries.PublishEntry, publish_entry)

        # Retrieve `symbology_only` Query Parameter
        symbology_only = self.request.query_params.get("symbology_only")
        symbology_only = utils.string_to_boolean(symbology_only)  # type: ignore[assignment]

        # Publish!
        publish_entry.publish(symbology_only)

        # Add Action Log Entry
        logs_utils.add_to_actions_log(
            user=request.user,
            model=publish_entry,
            action="Publish entry was manually re-published to both channels"
        )

        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @drf_utils.extend_schema(
        parameters=[drf_utils.OpenApiParameter("symbology_only", type=bool)],
        request=None,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    @decorators.action(detail=True, methods=["POST"], url_path=r"publish/cddp")
    def publish_cddp(self, request: request.Request, pk: str) -> response.Response:
        """Publishes to the CDDP Channel.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Publish Entry.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Retrieve Publish Entry
        # Help `mypy` by casting the resulting object to a Publish Entry
        publish_entry = self.get_object()
        publish_entry = cast(models.publish_entries.PublishEntry, publish_entry)

        # Retrieve `symbology_only` Query Parameter
        symbology_only = self.request.query_params.get("symbology_only")
        symbology_only = utils.string_to_boolean(symbology_only)  # type: ignore[assignment]

        # Publish!
        publish_entry.publish_cddp(symbology_only)

        # Add Action Log Entry
        logs_utils.add_to_actions_log(
            user=request.user,
            model=publish_entry,
            action="Publish entry was manually re-published to the CDDP channel"
        )

        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @transaction.atomic()
    @drf_utils.extend_schema(
        parameters=[drf_utils.OpenApiParameter("symbology_only", type=bool)],
        request=None,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    @decorators.action(detail=True, methods=["POST"], url_path=r"publish/geoserver")
    def publish_geoserver(self, request: request.Request, pk: str) -> response.Response:
        """Publishes to the GeoServer Channel.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Publish Entry.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Retrieve Publish Entry
        # Help `mypy` by casting the resulting object to a Publish Entry
        publish_entry = self.get_object()
        publish_entry = cast(models.publish_entries.PublishEntry, publish_entry)

        # Retrieve `symbology_only` Query Parameter
        symbology_only = self.request.query_params.get("symbology_only")
        symbology_only = utils.string_to_boolean(symbology_only)  # type: ignore[assignment]

        # already exists
        if publish_entry.geoserver_queues.filter(
            status__in=[GeoServerQueueStatus.READY, GeoServerQueueStatus.ON_PUBLISHING]).exists():
            return response.Response(status=status.HTTP_409_CONFLICT)
        else:
            # creating a queue item when it doesn't exist
            res = geoserver_manager.push(publish_entry=publish_entry, 
                                               symbology_only=symbology_only, 
                                               submitter=request.user)
        if res:
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        else :
            return response.Response(status=status.HTTP_412_PRECONDITION_FAILED)


    @drf_utils.extend_schema(
        parameters=[drf_utils.OpenApiParameter("symbology_only", type=bool)],
        request=None,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    @decorators.action(detail=True, methods=["POST"], url_path=r"publish/ftp")
    def publish_ftp(self, request: request.Request, pk: str) -> response.Response:
        """Publishes to the FTP.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Publish Entry.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Retrieve Publish Entry
        # Help `mypy` by casting the resulting object to a Publish Entry
        publish_entry = self.get_object()
        publish_entry = cast(models.publish_entries.PublishEntry, publish_entry)

        # Retrieve `symbology_only` Query Parameter
        symbology_only = self.request.query_params.get("symbology_only")
        symbology_only = utils.string_to_boolean(symbology_only)  # type: ignore[assignment]

        # Publish!
        publish_entry.publish_ftp(symbology_only)

        # Add Action Log Entry
        logs_utils.add_to_actions_log(
            user=request.user,
            model=publish_entry,
            action="Publish entry was manually re-published to the FTP channel"
        )

        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(detail=True, methods=["GET"], url_path=r"geoserver")
    def geoserver_list(self, request: request.Request, pk: str) -> response.Response:
        """Produce a list of GeoServer publish configurations

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Publish Entry.

        Returns:
            response.Response: Empty response confirming success.
        """
        # # Retrieve Publish Entry
        # # Help `mypy` by casting the resulting object to a Publish Entry
        publish_entry = self.get_object()
        publish_entry = cast(models.publish_entries.PublishEntry, publish_entry)
        geoserver_publish_channel = models.publish_channels.GeoServerPublishChannel.objects.filter(publish_entry=publish_entry)
        serializer = serializers.publish_channels.GeoServerPublishChannelSerializer(geoserver_publish_channel, many=True)
        
        # Return Response
        return response.Response(serializer.data, status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["GET"], url_path=r"cddp")
    def cddp_list(self, request: request.Request, pk: str) -> response.Response:
        """Produce a list of CDDP publish configurations

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Publish Entry.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Retrieve Publish Entry
        # Help `mypy` by casting the resulting object to a Publish Entry
        publish_entry = self.get_object()
        publish_entry = cast(models.publish_entries.PublishEntry, publish_entry)
        cddp_publish_channel = models.publish_channels.CDDPPublishChannel.objects.filter(publish_entry=publish_entry)
        cddp_list = []
        for cpc in cddp_publish_channel:
            published_at = None
            
            if cpc.published_at:
                 published_at = cpc.published_at.astimezone().strftime('%d %b %Y %H:%M %p')                 
            cddp_list.append({
                "id": cpc.id, 
                "name":cpc.name, 
                "format": cpc.format, 
                "path": cpc.path, 
                "mode": cpc.mode, 
                "frequency": cpc.frequency, 
                "published_at": published_at,
                "xml_path":cpc.xml_path
                })

        # Return Response
        return response.Response(cddp_list, status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["GET"], url_path=r"ftp")
    def ftp_list(self, request: request.Request, pk: str) -> response.Response:
        """Produce a list of FTP publish configurations

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Publish Entry.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Retrieve Publish Entry
        # Help `mypy` by casting the resulting object to a Publish Entry
        publish_entry = self.get_object()
        publish_entry = cast(models.publish_entries.PublishEntry, publish_entry)
        ftp_publish_channel = models.publish_channels.FTPPublishChannel.objects.filter(publish_entry=publish_entry)
        ftp_list = []
        for cpc in ftp_publish_channel:
            published_at = None
            
            if cpc.published_at:
                 published_at = cpc.published_at.astimezone().strftime('%d %b %Y %H:%M %p')  
            ftp_server_id = ""
            ftp_server_name = ""
                                              
            if cpc.ftp_server:
                ftp_server_id = cpc.ftp_server.id
                ftp_server_name = cpc.ftp_server.name
                             
            ftp_list.append({"id": cpc.id, "name":cpc.name, "ftp_server_id": ftp_server_id, "ftp_server_name" : ftp_server_name, "format": cpc.format, "path": cpc.path, "frequency": cpc.frequency, "published_at": published_at})

        # Return Response
        return response.Response(ftp_list, status=status.HTTP_200_OK)

    # @decorators.action(detail=True, methods=["GET"], url_path=r"ftp-server")
    # def ftp_server_list(self, request: request.Request, pk: str) -> response.Response:
    #     """Produce a list of FTP Servers

    #     Args:
    #         request (request.Request): API request.
    #         pk (str): Primary key of the Publish Entry.

    #     Returns:
    #         response.Response: Empty response confirming success.
    #     """
    #     # Retrieve Publish Entry
    #     # Help `mypy` by casting the resulting object to a Publish Entry
    #     publish_entry = self.get_object()
    #     publish_entry = cast(models.publish_entries.PublishEntry, publish_entry)
    #     ftp_servers = models.publish_channels.FTPServer.objects.filter(enabled=True)
    #     ftp_servers_list = []
    #     for cpc in ftp_servers:              
    #         ftp_servers_list.append({"id": cpc.id, "name":cpc.name})

    #     # Return Response
    #     return response.Response(ftp_servers_list, status=status.HTTP_200_OK)

    @drf_utils.extend_schema(request=None, responses={status.HTTP_204_NO_CONTENT: None})
    @decorators.action(detail=True, methods=["POST"])
    def lock(self, request: request.Request, pk: str) -> response.Response:
        """Locks the Publish Entry.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Publish Entry.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Retrieve Publish Entry
        # Help `mypy` by casting the resulting object to a Publish Entry
        publish_entry = self.get_object()
        publish_entry = cast(models.publish_entries.PublishEntry, publish_entry)

        # Lock
        success = publish_entry.lock()

        # Check Success
        if success:
            # Add Action Log Entry
            logs_utils.add_to_actions_log(
                user=request.user,
                model=publish_entry,
                action="Publish entry was locked"
            )

        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)


    @drf_utils.extend_schema(request=None, responses=serializers.publish_entries.PublishEntryCreateEditorSerializer)
    @decorators.action(detail=True, methods=["POST"], url_path=r"editors/add/(?P<user_pk>\d+)")
    def add_editors(self, request: request.Request, pk: str, user_pk: str) -> response.Response:
        """Unlocks the Publish Entry.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Publish Entry.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Add Editor to Publish
        # Help `mypy` by casting the resulting object to a Publish Entry
        publish_entry = self.get_object()
        publish_entry = cast(models.publish_entries.PublishEntry, publish_entry)
        user = UserModel.objects.get(id=user_pk)
        publish_entry.editors.add(user)

        success = False
        editors = publish_entry.editors.all()
        if user in editors:
            success = True

        #Check Success
        if success:
            # Add Action Log Entry
            logs_utils.add_to_actions_log(
                user=request.user,
                model=publish_entry,
                action="Publish entry add editor {} with id {} ".format(user.first_name+' '+user.last_name, user_pk)
            )

        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @drf_utils.extend_schema(request=None, responses=serializers.publish_entries.PublishEntryListEditorSerializer)
    @decorators.action(detail=True, methods=["GET"], url_path=r"editors")
    def editors(self, request: request.Request, pk: str) -> response.Response:
        """Unlocks the Publish Entry.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Publish Entry.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Retrieve Publish Entry
        # Help `mypy` by casting the resulting object to a Publish Entry        
        publish_entry = self.get_object()
        editors = publish_entry.editors.all()
        editors_list = []
        for e in editors:
            editors_list.append({'id': e.id,'first_name' : e.first_name,'last_name' : e.last_name, 'email': e.email})

        # Return Response
        return response.Response(editors_list, status=status.HTTP_200_OK)

    @drf_utils.extend_schema(request=None, responses=serializers.publish_entries.PublishEntryCreateEditorSerializer)
    @decorators.action(detail=True, methods=["DELETE"], url_path=r"editors/delete/(?P<user_pk>\d+)")
    def delete_editors(self, request: request.Request, pk: str, user_pk: str) -> response.Response:
        """Unlocks the Publish Entry.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Publish Entry.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Retrieve Publish Entry
        # Help `mypy` by casting the resulting object to a Publish Entry
        publish_entry = self.get_object()
        publish_entry = cast(models.publish_entries.PublishEntry, publish_entry)
        user = UserModel.objects.get(id=user_pk)
        success = publish_entry.editors.remove(user)
        success = False
        editors = publish_entry.editors.all()
        if user not in editors:
            success = True
   
        #Check Success
        if success:
            # Add Action Log Entry
            logs_utils.add_to_actions_log(
                user=request.user,
                model=publish_entry,
                action="Publish entry delete editor {} with id {} ".format(user.first_name+' '+user.last_name, user_pk)
            )

        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)


    @drf_utils.extend_schema(request=None, responses={status.HTTP_204_NO_CONTENT: None})
    @decorators.action(detail=True, methods=["POST"])
    def unlock(self, request: request.Request, pk: str) -> response.Response:
        """Unlocks the Publish Entry.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Publish Entry.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Retrieve Publish Entry
        # Help `mypy` by casting the resulting object to a Publish Entry
        publish_entry = self.get_object()
        publish_entry = cast(models.publish_entries.PublishEntry, publish_entry)

        # Unlock
        success = publish_entry.unlock()

        # Check Success
        if success:
            # Add Action Log Entry
            logs_utils.add_to_actions_log(
                user=request.user,
                model=publish_entry,
                action="Publish entry was unlocked"
            )

        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @drf_utils.extend_schema(request=None, responses={status.HTTP_204_NO_CONTENT: None})
    @decorators.action(detail=True, methods=["POST"], url_path=r"assign/(?P<user_pk>\d+)")
    def assign(self, request: request.Request, pk: str, user_pk: str) -> response.Response:
        """Assigns the Publish Entry.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Publish Entry.
            user_pk (str): Primary key of the User to assign to.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Retrieve Publish Entry
        # Help `mypy` by casting the resulting object to a Publish Entry
        publish_entry = self.get_object()
        publish_entry = cast(models.publish_entries.PublishEntry, publish_entry)

        # Retrieve User
        user = shortcuts.get_object_or_404(UserModel, id=user_pk)

        # Assign!
        success = publish_entry.assign(user)

        # Check Success
        if success:
            # Add Action Log Entry
            logs_utils.add_to_actions_log(
                user=request.user,
                model=publish_entry,
                action=f"Publish entry was assigned to {user} (id: {user.pk})"
            )

        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @drf_utils.extend_schema(request=None, responses={status.HTTP_204_NO_CONTENT: None})
    @decorators.action(detail=True, methods=["POST"])
    def unassign(self, request: request.Request, pk: str) -> response.Response:
        """Unassigns the Publish Entry.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Publish Entry.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Retrieve Publish Entry
        # Help `mypy` by casting the resulting object to a Publish Entry
        publish_entry = self.get_object()
        publish_entry = cast(models.publish_entries.PublishEntry, publish_entry)

        # Unassign!
        success = publish_entry.unassign()

        # Check Success
        if success:
            # Add Action Log Entry
            logs_utils.add_to_actions_log(
                user=request.user,
                model=publish_entry,
                action="Publish entry was unassigned"
            )

        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)


@drf_utils.extend_schema(tags=["Publisher - CDDP Publish Channels"])
class CDDPPublishChannelViewSet(
    mixins.ChoicesMixin,
    mixins.MultipleSerializersMixin,
    viewsets.mixins.CreateModelMixin,
    viewsets.mixins.DestroyModelMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """CDDP Publish Channel View Set."""
    queryset = models.publish_channels.CDDPPublishChannel.objects.all()
    serializer_class = serializers.publish_channels.CDDPPublishChannelSerializer
    serializer_classes = {"create": serializers.publish_channels.CDDPPublishChannelCreateSerializer}
    filterset_class = filters.CDDPPublishChannelFilter
    search_fields = ["publish_entry__catalogue_entry__name",]# "publish_entry__description"]
    permission_classes = [permissions.HasPublishEntryPermissions]


@drf_utils.extend_schema(tags=["Publisher - GeoServer Publish Channels"])
class GeoServerPublishChannelViewSet(
    mixins.ChoicesMixin,
    mixins.MultipleSerializersMixin,
    viewsets.mixins.CreateModelMixin,
    viewsets.mixins.DestroyModelMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """GeoServer Publish Channel View Set."""
    queryset = models.publish_channels.GeoServerPublishChannel.objects.all()
    serializer_class = serializers.publish_channels.GeoServerPublishChannelSerializer
    serializer_classes = {"create": serializers.publish_channels.GeoServerPublishChannelCreateSerializer}
    filterset_class = filters.GeoServerPublishChannelFilter
    search_fields = ["publish_entry__catalogue_entry__name", "publish_entry__description"]
    permission_classes = [permissions.HasPublishEntryPermissions]


    # @decorators.action(detail=True, methods=["POST"], url_path=r"list")
    # def geoserver_list(self, request: request.Request, pk: str) -> response.Response:
    #     """Publishes to the GeoServer Channel.

    #     Args:
    #         request (request.Request): API request.
    #         pk (str): Primary key of the Publish Entry.

    #     Returns:
    #         response.Response: Empty response confirming success.
    #     """
    #     # Retrieve Publish Entry
    #     # Help `mypy` by casting the resulting object to a Publish Entry
    #     publish_entry = self.get_object()
    #     publish_entry = cast(models.publish_entries.PublishEntry, publish_entry)

    #     # Retrieve `symbology_only` Query Parameter
    #     symbology_only = self.request.query_params.get("symbology_only")
    #     symbology_only = utils.string_to_boolean(symbology_only)  # type: ignore[assignment]

    #     # Publish!
    #     publish_entry.publish_geoserver(symbology_only)

    #     # Add Action Log Entry
    #     logs_utils.add_to_actions_log(
    #         user=request.user,
    #         model=publish_entry,
    #         action="Publish entry was manually re-published to the GeoServer channel"
    #     )

    #     # Return Response
    #     return response.Response(status=status.HTTP_204_NO_CONTENT)


@drf_utils.extend_schema(tags=["Publisher - Notifications (Email)"])
class EmailNotificationViewSet(
    mixins.ChoicesMixin,
    mixins.MultipleSerializersMixin,
    viewsets.mixins.CreateModelMixin,
    viewsets.mixins.DestroyModelMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Email Notification View Set."""
    queryset = models.notifications.EmailNotification.objects.all()
    serializer_class = serializers.notifications.EmailNotificationSerializer
    serializer_classes = {"create": serializers.notifications.EmailNotificationCreateSerializer}
    filterset_class = filters.EmailNotificationFilter
    search_fields = ["name", "email"]
    permission_classes = [permissions.HasPublishEntryPermissions | accounts_permissions.IsInAdministratorsGroup]
    
    # to pass the pk to serializer
    def get_serializer_context(self):
        context = super().get_serializer_context()
        if context['request'].method == 'PUT':
            context['pk'] = self.kwargs['pk']
        return context


@drf_utils.extend_schema(tags=["Publisher - Workspaces"])
class WorkspaceViewSet(mixins.ChoicesMixin, viewsets.ReadOnlyModelViewSet):
    """Workspace View Set."""
    queryset = models.workspaces.Workspace.objects.all()
    serializer_class = serializers.workspaces.WorkspaceSerializer
    filterset_class = filters.WorkspaceFilter
    search_fields = ["name"]




@drf_utils.extend_schema(tags=["Publisher - FTP Publish Channels"])
class FTPPublishChannelViewSet(
    mixins.ChoicesMixin,
    mixins.MultipleSerializersMixin,
    viewsets.mixins.CreateModelMixin,
    viewsets.mixins.DestroyModelMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """FTP Publish Channel View Set."""
    queryset = models.publish_channels.FTPPublishChannel.objects.all()
    serializer_class = serializers.publish_channels.FTPPublishChannelSerializer
    serializer_classes = {"create": serializers.publish_channels.FTPPublishChannelCreateSerializer}
    filterset_class = filters.FTPPublishChannelFilter
    search_fields = ["publish_entry__catalogue_entry__name",]# "publish_entry__description"]
    permission_classes = [permissions.HasPublishEntryPermissions]


@drf_utils.extend_schema(tags=["Publisher - FTP Publish Channels"])
class FTPServerViewSet(
    mixins.ChoicesMixin,
    mixins.MultipleSerializersMixin,
    viewsets.mixins.CreateModelMixin,
    viewsets.mixins.DestroyModelMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """FTP Publish Channel View Set."""
    queryset = models.publish_channels.FTPServer.objects.all()
    serializer_class = serializers.publish_channels.FTPServerSerializer
    #serializer_classes = {"create": serializers.publish_channels.FTPPublishChannelCreateSerializer}
    serializer_classes = {}
    filterset_class = filters.FTPServerFilter
    search_fields = ["id","name",]# "publish_entry__description"]
    permission_classes = [permissions.HasPublishEntryPermissions]    
    
@drf_utils.extend_schema(tags=["Publisher - GeoServer Queues"])
class GeoServerQueueViewSet(
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """GeoServer Queue View Set."""
    queryset = models.geoserver_queues.GeoServerQueue.objects.all().order_by('-id')
    serializer_class = serializers.publish_channels.GeoServerQueueSerializer
    permission_classes = [accounts_permissions.IsInAdministratorsGroup]


class CDDPContentsViewSet(viewsets.ViewSet):
    """
    ViewSet for handling files within a specified directory.
    Provides list, retrieve, and delete functionalities.
    """
    pathToFolder = settings.AZURE_OUTPUT_SYNC_DIRECTORY

    def list(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        """
        List all files within the directory along with their metadata.
        """
        try:
            file_list = self._get_files_with_metadata(self.pathToFolder)
            return Response(file_list)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_files_with_metadata(self, directory: str) -> list:
        """
        Retrieve file paths and metadata for files within the specified directory.
        """
        file_list = []
        datetime_format = '%d-%m-%Y %H:%M:%S'
        try:
            for dirpath, _, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    file_stat = os.stat(filepath)
                    creation_time = datetime.fromtimestamp(file_stat.st_ctime).strftime(datetime_format)
                    last_access_time = datetime.fromtimestamp(file_stat.st_atime).strftime(datetime_format)
                    last_modify_time = datetime.fromtimestamp(file_stat.st_mtime).strftime(datetime_format)
                    size_bytes = file_stat.st_size
                    file_list.append({
                        'filepath': filepath,
                        'created_at': creation_time,
                        'last_accessed_at': last_access_time,
                        'last_modified_at': last_modify_time,
                        'size_bytes': size_bytes
                    })
        except Exception as e:
            raise RuntimeError(f"Error while retrieving file metadata: {str(e)}")
        return file_list

    @decorators.action(detail=False, methods=['get'], url_path='retrieve-file')
    def retrieve_file(self, request: http.HttpRequest) -> http.HttpResponse:
        """
        Retrieve the specified file's content.
        """
        filepath = request.query_params.get('filepath')
        if not filepath:
            return Response({'error': 'Filepath query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        if os.path.exists(filepath):
            try:
                with open(filepath, 'rb') as file:
                    return http.HttpResponse(file.read(), content_type='application/octet-stream')
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            raise http.Http404("File does not exist")

    @decorators.action(detail=False, methods=['delete'], url_path='delete-file')
    def destroy_file(self, request: http.HttpRequest) -> http.HttpResponse:
        """
        Delete the specified file.
        """
        filepath = request.query_params.get('filepath')
        if not filepath:
            return Response({'error': 'Filepath query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            raise http.Http404("File does not exist")

###############################

# class CDDPQueueView(base.TemplateView):
#     template_name = "govapp/cddp_queue.html"

#     def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
#         pathToFolder = settings.AZURE_OUTPUT_SYNC_DIRECTORY

#         file_list = self.get_files_with_metadata(pathToFolder)

#         context = {'file_list': file_list}
#         return shortcuts.render(request, self.template_name, context)

#     def get_files_with_metadata(self, directory):
#         """
#         Function to retrieve file paths and metadata for files within the specified directory.
#         """
#         file_list = []
#         for dirpath, _, filenames in os.walk(directory):
#             for filename in filenames:
#                 filepath = os.path.join(dirpath, filename)
#                 file_stat = os.stat(filepath)
#                 creation_time = datetime.fromtimestamp(file_stat.st_ctime).strftime('%d-%m-%Y %H:%M:%S')
#                 last_access_time = datetime.fromtimestamp(file_stat.st_atime).strftime('%d-%m-%Y %H:%M:%S')
#                 last_modify_time = datetime.fromtimestamp(file_stat.st_mtime).strftime('%d-%m-%Y %H:%M:%S')
#                 size_bytes = file_stat.st_size
#                 file_list.append({
#                     'filepath': filepath,
#                     'created_at': creation_time,
#                     'last_accessed_at': last_access_time,
#                     'last_modified_at': last_modify_time,
#                     'size_bytes': size_bytes
#                 })
#         return file_list
