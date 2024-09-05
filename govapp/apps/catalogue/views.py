"""Kaartdijin Boodja Catalogue Django Application Views."""


# Third-Party
import logging
from django import conf
from django import shortcuts
from django.contrib import auth
from django.db import connection
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from drf_spectacular import utils as drf_utils
from rest_framework import decorators
from rest_framework import request
from rest_framework import response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from rest_framework.response import Response
from datetime import timedelta
from django.core.cache import cache
from owslib.wms import WebMapService
from owslib.wfs import WebFeatureService
import psycopg2
import json
import os

# Local
from govapp import settings
from govapp.common import mixins
from govapp.apps.accounts import permissions as accounts_permissions
from govapp.apps.catalogue import filters
from govapp.apps.catalogue import models
from govapp.apps.publisher import models as publish_models
from govapp.apps.catalogue import permissions
from govapp.apps.catalogue import serializers
from govapp.apps.catalogue import utils as catalogue_utils
from govapp.apps.catalogue.postgres_scanner import Scanner
from govapp.apps.catalogue.utils import validate_request
from govapp.apps.catalogue.models import layer_submissions as catalogue_layer_submissions_models
from govapp.apps.logs import mixins as logs_mixins
from govapp.apps.logs import utils as logs_utils


# Typing
from typing import Callable, cast
from typing import Any


# Shortcuts
UserModel = auth.get_user_model()

logger = logging.getLogger(__name__)


@drf_utils.extend_schema(tags=["Catalogue - Catalogue Entries"])
class CatalogueEntryViewSet(
    mixins.ChoicesMixin,
    mixins.HistoryMixin,
    logs_mixins.ActionsLogMixin,
    logs_mixins.CommunicationsLogMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Catalogue Entry View Set."""
    queryset = models.catalogue_entries.CatalogueEntry.objects.all()
    serializer_class = serializers.catalogue_entries.CatalogueEntrySerializer
    filterset_class = filters.CatalogueEntryFilter
    search_fields = ["name", "description", "assigned_to__username", "assigned_to__email", "custodian__name"]    
    permission_classes = [permissions.IsCatalogueEntryPermissions | accounts_permissions.IsInAdministratorsGroup]

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @decorators.action(detail=False, methods=["POST"], permission_classes=[accounts_permissions.IsInCatalogueAdminGroup])
    def delete_file(self, request: request.Request):
        filenameToDelete = request.POST.get('newFileName', '')
        if filenameToDelete:
            pathToFile = os.path.join(settings.PENDING_IMPORT_PATH,  filenameToDelete)
            if os.path.exists(pathToFile):
                os.remove(pathToFile)
                logger.info(f"File: [{pathToFile}] deleted successfully.")
                return JsonResponse({'message': 'File deleted successfully.'})
            else:
                logger.info(f"File: [{pathToFile}] doesn't exist.")
                return JsonResponse({'message': 'File does not exist.'})
        else:
            return JsonResponse({'message': 'No file specified.'})

    @decorators.action(detail=False, methods=["POST"], permission_classes=[accounts_permissions.IsInCatalogueAdminGroup])
    def upload_file(self, request: request.Request):
        if request.FILES:
            # uploaded_files = []  # Multiple files might be uploaded
            allowed_extensions = ['.zip', '.7z',]
            uploaded_file = request.FILES.getlist('file')[0]
            newFileName = request.POST.get('newFileName', '')

            logger.info(f'File: [{uploaded_file.name}] is being uploaded...')

            # Check file extensions
            _, file_extension = os.path.splitext(uploaded_file.name)
            if file_extension.lower() not in allowed_extensions:
                return JsonResponse({'error': 'Invalid file type. Only .zip and .7z files are allowed.'}, status=400)

            # Save files
            save_path = os.path.join(settings.PENDING_IMPORT_PATH,  newFileName)
            with open(save_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            logger.info(f"File: [{uploaded_file.name}] has been successfully saved.")
            return JsonResponse({'message': 'File(s) uploaded successfully.'})
        else:
            logger.info(f"No file(s) were uploaded.")
            return JsonResponse({'error': 'No file(s) were uploaded.'}, status=400)

    @drf_utils.extend_schema(request=None, responses={status.HTTP_204_NO_CONTENT: None})
    @decorators.action(detail=True, methods=["POST"])
    def lock(self, request: request.Request, pk: str) -> response.Response:
        """Locks the Catalogue Entry.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Catalogue Entry.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Retrieve Catalogue Entry
        # Help `mypy` by casting the resulting object to a Catalogue Entry
        # catalogue_entry = self.get_object()
        catalogue_entry = shortcuts.get_object_or_404(models.catalogue_entries.CatalogueEntry, id=pk)
        # catalogue_entry = cast(models.catalogue_entries.CatalogueEntry, catalogue_entry)

        # Lock
        success = catalogue_entry.lock()

        # Check Success
        if success:
            # Add Action Log Entry
            logs_utils.add_to_actions_log(
                user=request.user,
                model=catalogue_entry,
                action="Catalogue entry was locked"
            )

            # Return Response
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        else:
            # Return Response
            return response.Response("Error Locking Catalogue", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @drf_utils.extend_schema(request=None, responses={status.HTTP_204_NO_CONTENT: None})
    @decorators.action(detail=True, methods=["POST"])
    def unlock(self, request: request.Request, pk: str) -> response.Response:
        """Unlocks the Catalogue Entry.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Catalogue Entry.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Retrieve Catalogue Entry
        # Help `mypy` by casting the resulting object to a Catalogue Entry
        # catalogue_entry = self.get_object()
        # catalogue_entry = cast(models.catalogue_entries.CatalogueEntry, catalogue_entry)
        catalogue_entry = shortcuts.get_object_or_404(models.catalogue_entries.CatalogueEntry, id=pk)

        # Unlock
        success = catalogue_entry.unlock()

        # Check Success
        if success:
            # Add Action Log Entry
            logs_utils.add_to_actions_log(
                user=request.user,
                model=catalogue_entry,
                action="Catalogue entry was unlocked"
            )

        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @drf_utils.extend_schema(request=None, responses={status.HTTP_204_NO_CONTENT: None})
    @decorators.action(detail=True, methods=["POST"])
    def decline(self, request: request.Request, pk: str) -> response.Response:
        """Declines the Catalogue Entry.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Catalogue Entry.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Retrieve Catalogue Entry
        # Help `mypy` by casting the resulting object to a Catalogue Entry
        catalogue_entry = self.get_object()
        catalogue_entry = cast(models.catalogue_entries.CatalogueEntry, catalogue_entry)

        # Decline
        success = catalogue_entry.decline()

        # Check Success
        if success:
            # Add Action Log Entry
            logs_utils.add_to_actions_log(
                user=request.user,
                model=catalogue_entry,
                action="Catalogue entry was declined"
            )

        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @drf_utils.extend_schema(request=None, responses={status.HTTP_204_NO_CONTENT: None})
    @decorators.action(detail=True, methods=["POST"], url_path=r"assign/(?P<user_pk>\d+)")
    def assign(self, request: request.Request, pk: str, user_pk: str) -> response.Response:
        """Assigns the Catalogue Entry.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Catalogue Entry.
            user_pk (str): Primary key of the User to assign to.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Retrieve Catalogue Entry
        # Help `mypy` by casting the resulting object to a Catalogue Entry
        catalogue_entry = self.get_object()
        catalogue_entry = cast(models.catalogue_entries.CatalogueEntry, catalogue_entry)

        # Retrieve User
        user = shortcuts.get_object_or_404(UserModel, id=user_pk)

        # Assign!
        success = catalogue_entry.assign(user)

        # Check Success
        if success:
            # Add Action Log Entry
            logs_utils.add_to_actions_log(
                user=request.user,
                model=catalogue_entry,
                action=f"Catalogue entry was assigned to {user} (id: {user.pk})"
            )

        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @drf_utils.extend_schema(request=None, responses={status.HTTP_204_NO_CONTENT: None})
    @decorators.action(detail=True, methods=["POST"])
    def unassign(self, request: request.Request, pk: str) -> response.Response:
        """Unassigns the Catalogue Entry.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Catalogue Entry.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Retrieve Catalogue Entry
        # Help `mypy` by casting the resulting object to a Catalogue Entry
        catalogue_entry = self.get_object()
        catalogue_entry = cast(models.catalogue_entries.CatalogueEntry, catalogue_entry)

        # Unassign!
        success = catalogue_entry.unassign()

        # Check Success
        if success:
            # Add Action Log Entry
            logs_utils.add_to_actions_log(
                user=request.user,
                model=catalogue_entry,
                action="Catalogue entry was unassigned"
            )

        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)
    
    @decorators.action(detail=False, methods=["GET"], permission_classes=[accounts_permissions.IsAuthenticated],
                       url_path=r'(?P<name>\w+)/layer')
    def layer_by_name(self, request: request.Request, name: str):
        """ Api to provide geojson file

        Args:
            request (request.Request): request object passed by Django framework
            name (str): uri parameter represents name of layer submission(catalogue name)

        Returns:
            response.Response: HTTP response with geojson data file
        """
        entry = self.queryset.filter(name=name)
        if entry.exists():
            return self.layer_by_id(request, entry.first().id)
        else:
            return response.Response({"error": 'Invalid query param "name:{name}".'}, 
                                     status=status.HTTP_400_BAD_REQUEST)
        
    @decorators.action(detail=False, methods=["GET"], permission_classes=[accounts_permissions.IsAuthenticated],
                       url_path=r'(?P<id>\d+)/layer')
    def layer_by_id(self, request: request.Request, id: int):
        """ Api to provide geojson file

        Args:
            request (request.Request): request object passed by Django framework
            pk (int): uri parameter represents id of layer submission(catalogue id)

        Returns:
            response.Response: HTTP response with geojson data file
        """
        layer_submission = catalogue_layer_submissions_models.LayerSubmission.objects.filter(catalogue_entry=id, is_active=True).first()
        map_data = None
        try:
            with open(layer_submission.geojson) as file:
                map_data = file.read()
                map_data = json.loads(map_data)
        except Exception as e:
            return response.Response({"error": 'An exception was occured while loading a target file.'}, 
                                     status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return response.Response(map_data, content_type='application/json', status=status.HTTP_200_OK)
    
    @drf_utils.extend_schema(parameters=[drf_utils.OpenApiParameter("days_ago", type=int, required=True)])
    @decorators.action(detail=False, methods=['GET'])
    def recent(self, request: request.Request):
        """ Api to provide sumary of recent catalogue entries from n hours ago

        Args:
            request (request.Request): request object passed by Django framework - must include integer value of days_ago
            pk (str): uri parameter represents id of layer submission(catalogue id)

        Returns:
            response.Response: HTTP response with a list of summary of recent catalogue entries
        """
        
        days_ago = self.request.query_params.get("days_ago")
        
        # validate days_ago
        if days_ago is None or len(days_ago.strip()) == 0:
            return response.Response({"error": 'Field days_ago is required.'}, status=status.HTTP_400_BAD_REQUEST)
        elif not days_ago.isdigit() or int(days_ago) <= 0:
            return response.Response({"error": 'Field house_ago must be a positive integer.'}, status=status.HTTP_400_BAD_REQUEST)

        # select query using inner join and filter
        start_date = self.get_db_now() - timedelta(days=int(days_ago))
        filtered = models.layer_submissions.LayerSubmission.objects.select_related('catalogue_entry').filter(catalogue_entry__updated_at__gte=start_date, is_active=True)
        selected = filtered.values('catalogue_entry__id', 'catalogue_entry__name', 'catalogue_entry__created_at', 'catalogue_entry__updated_at', 'id')
        
        # build a response data
        response_data = [{
                'id': entry['catalogue_entry__id'],
                'name': entry['catalogue_entry__name'],
                'created_at': entry['catalogue_entry__created_at'],
                'updated_at': entry['catalogue_entry__updated_at'],
                'active_layer': entry['id']
            } for entry in list(selected)]
        return response.Response(response_data, content_type='application/json', status=status.HTTP_200_OK)
    
    def get_db_now(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT NOW()")
            result = cursor.fetchone()
            current_time = result[0]
        return current_time
    

@drf_utils.extend_schema(tags=["Catalogue - Custodians"])
class CustodianViewSet(mixins.ChoicesMixin, viewsets.ReadOnlyModelViewSet):
    """Custodian View Set."""
    queryset = models.custodians.Custodian.objects.all()
    serializer_class = serializers.custodians.CustodianSerializer
    filterset_class = filters.CustodianFilter
    search_fields = ["name", "contact_name", "contact_email", "contact_phone"]


@drf_utils.extend_schema(tags=["Catalogue - Layer Attributes"])
class LayerAttributeViewSet(
    mixins.ChoicesMixin,
    mixins.MultipleSerializersMixin,
    viewsets.mixins.CreateModelMixin,
    viewsets.mixins.DestroyModelMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Layer Attribute View Set."""
    queryset = models.layer_attributes.LayerAttribute.objects.all()
    serializer_class = serializers.layer_attributes.LayerAttributeSerializer
    serializer_classes = {"create": serializers.layer_attributes.LayerAttributeCreateSerializer}
    filterset_class = filters.LayerAttributeFilter
    search_fields = ["name", "type", "catalogue_entry__name"]
    permission_classes = [permissions.HasCatalogueEntryPermissions | accounts_permissions.IsInAdministratorsGroup]

    # to pass the pk to serializer
    def get_serializer_context(self):
        context = super().get_serializer_context()
        if context['request'].method == 'PUT':
            context['pk'] = self.kwargs['pk']
        return context


@drf_utils.extend_schema(tags=["Catalogue - Layer Attribute Types"])
class LayerAttributeTypeViewSet(
    viewsets.mixins.ListModelMixin,
    viewsets.GenericViewSet,
):      
    """Layer Attribute Type View Set."""
    queryset = models.layer_attribute_types.LayerAttributeType.objects.all()
    serializer_class = serializers.layer_attribute_types.LayerAttributeTypeSerializer
    filter_backends = []
    permission_classes = [permissions.HasCatalogueEntryPermissions | accounts_permissions.IsInAdministratorsGroup]
    pagination_class = None

    
@drf_utils.extend_schema(tags=["Catalogue - Layer Metadata"])
class LayerMetadataViewSet(
    mixins.ChoicesMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Layer Metadata View Set."""
    queryset = models.layer_metadata.LayerMetadata.objects.all()
    serializer_class = serializers.layer_metadata.LayerMetadataSerializer
    filterset_class = filters.LayerMetadataFilter
    search_fields = ["catalogue_entry__name"]
    permission_classes = [permissions.HasCatalogueEntryPermissions | accounts_permissions.IsInAdministratorsGroup]


@drf_utils.extend_schema(tags=["Catalogue - Layer Submissions2"])
class LayerSubmissionViewSet2(
    mixins.ChoicesMixin,
    logs_mixins.ActionsLogMixin,
    logs_mixins.CommunicationsLogMixin,
    viewsets.ReadOnlyModelViewSet,
):
    """Layer Submission View Set."""
    queryset = models.layer_submissions.LayerSubmission.objects.all()
    serializer_class = serializers.layer_submissions.LayerSubmissionSerializer
    filterset_class = filters.LayerSubmissionFilter
    search_fields = ["id",]
    permission_classes = [permissions.HasCatalogueEntryPermissions | accounts_permissions.IsInAdministratorsGroup]
    pagination_class = DatatablesPageNumberPagination
    page_size = 10

    def list(self, request, *args, **kwargs):
        # return super().list(request, *args, **kwargs)
        queryset = self.filter_queryset(self.get_queryset())

        self.paginator.page_size = queryset.count()
        result_page = self.paginator.paginate_queryset(queryset, request)
        serializer = serializers.layer_submissions.LayerSubmissionSerializer(result_page, many=True)
        temp = self.paginator.get_paginated_response(serializer.data)
        return temp

        # Sorting
        # ordering = request.GET.get('order[0][column]')
        # if ordering:
        #     column_index = int(ordering)
        #     column_name = request.GET.get('columns[{}][data]'.format(column_index))
        #     order_dir = request.GET.get('order[0][dir]')
        #     if column_name and order_dir:
        #         if order_dir == 'asc':
        #             queryset = queryset.order_by(column_name)
        #         else:
        #             queryset = queryset.order_by(f'-{column_name}')
        
        # Pagination
        # page_size = int(request.GET.get('length', 10))
        # start = int(request.GET.get('start', 0))
        # page = start // page_size + 1

        # paginator = self.pagination_class()
        # paginator.page_size = page_size
        # paginator.page = page

        # result_page = paginator.paginate_queryset(queryset, request)
        
        # if result_page is not None:
        #     serializer = self.get_serializer(result_page, many=True)
        #     # temp = paginator.get_paginated_response(serializer.data)
        #     response_data = {
        #         'draw': int(request.GET.get('draw', 1)),
        #         'recordsTotal': queryset.count(),
        #         'recordsFiltered': queryset.count(),
        #         'results': serializer.data
        #     }
        #     return Response(response_data)

        # serializer = self.get_serializer(queryset, many=True)
        # return Response(serializer.data)


@drf_utils.extend_schema(tags=["Catalogue - Layer Submissions"])
class LayerSubmissionViewSet(
    mixins.ChoicesMixin,
    logs_mixins.ActionsLogMixin,
    logs_mixins.CommunicationsLogMixin,
    viewsets.ReadOnlyModelViewSet,
):
    """Layer Submission View Set."""
    queryset = models.layer_submissions.LayerSubmission.objects.all()
    serializer_class = serializers.layer_submissions.LayerSubmissionSerializer
    filterset_class = filters.LayerSubmissionFilter
    search_fields = ["description", "catalogue_entry__name"]
    permission_classes = [permissions.HasCatalogueEntryPermissions | accounts_permissions.IsInAdministratorsGroup]

    @decorators.action(detail=True, methods=["GET"], url_path="file", permission_classes=[accounts_permissions.IsAuthenticated])
    def download_file(self, request: request.Request, pk: str):
        layer_submission = shortcuts.get_object_or_404(models.layer_submissions.LayerSubmission, id=pk)
        user_access_permission = layer_submission.get_user_access_permission(request.user)
        if layer_submission.is_restricted and user_access_permission not in ['read', 'read_write',]:
            return response.Response({'error_msg':f'User does not have permissions to access the file.'}, status=status.HTTP_403_FORBIDDEN)

        file_path = self.queryset.get(id=pk).file

        if file_path == None or os.path.exists(file_path) == False:
            return response.Response({"message":"The target file does not exist."}, 
                                     content_type='application/json', 
                                     status=status.HTTP_404_NOT_FOUND)
            
        with open(file_path, 'rb') as fh:
            res = HttpResponse(fh.read(), 
                                content_type='application/octet-stream', 
                                status=status.HTTP_200_OK)
            res['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            res['Filename'] = os.path.basename(file_path)
            return res
        

@drf_utils.extend_schema(tags=["Catalogue - Layer Subscriptions"])
class LayerSubscriptionViewSet(
    mixins.ChoicesMixin, 
    mixins.MultipleSerializersMixin,
    logs_mixins.ActionsLogMixin,
    logs_mixins.CommunicationsLogMixin,
    viewsets.mixins.CreateModelMixin,
    viewsets.mixins.DestroyModelMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.GenericViewSet): 
                            #    viewsets.ReadOnlyModelViewSet):
    """Layer Subscription View Set."""
    queryset = models.layer_subscriptions.LayerSubscription.objects.all()
    serializer_class = serializers.layer_subscriptions.LayerSubscriptionSerializer
    serializer_classes = {"create":serializers.layer_subscriptions.LayerSubscriptionCreateSerializer,
                          "update":serializers.layer_subscriptions.LayerSubscriptionUpdateSerializer}
    filterset_class = filters.LayerSubscriptionFilter
    search_fields = ["catalogue_entry__name"]
    permission_classes = [permissions.HasCatalogueEntryPermissions | accounts_permissions.IsInAdministratorsGroup]

    def create(self, request):
        # Validation check
        data = validate_request(self.serializer_classes['create'], request.data)
        
        # Convert data types
        for key in data:
            if key in ['type', 'connection_timeout', 'max_connections', 'read_timeout'] and data.get(key) is not None:
                data[key] = int(data.get(key))
                
        # Check duplicated catalogue entry name
        if models.catalogue_entries.CatalogueEntry.objects.filter(name=data['name']).exists():
            return response.Response({'error_msg':f"catalogue entry name '{data['name']}' has been already taken."}, 
                                      content_type='application/json', status=status.HTTP_400_BAD_REQUEST)     
        
        # Check type
        type = None
        try:
            type = catalogue_utils.find_enum_by_value(models.layer_subscriptions.LayerSubscriptionType, data.get('type'))
            # type = {type.value:type for type in models.layer_subscriptions.LayerSubscriptionType}.get()
        except ValueError as exc:
            return response.Response({'error_msg':f"type '{data.get('type')}' is invalid."}, 
                                    content_type='application/json', status=status.HTTP_400_BAD_REQUEST) 
        
        # Create layer subscription
        models.layer_subscriptions.LayerSubscription.objects.create(
            type=type,
            name=data.get('name'),
            description=data.get('description'),
            workspace=data.get('workspace'),
            enabled=data.get('enabled'),
            url=data.get('url'),
            host=data.get('host'),
            port=data.get('port'),
            database=data.get('database'),
            username=data.get('username'),
            userpassword=data.get('userpassword'),
            connection_timeout=data.get('connection_timeout'),
            max_connections=data.get('max_connections'),
            min_connections=data.get('min_connections'),
            read_timeout=data.get('read_timeout'),
            schema=data.get('schema'),
            fetch_size=data.get('fetch_size')
        )
        
        return response.Response({'msg':"success"}, content_type='application/json', status=status.HTTP_200_OK)
    
    def update(self, request: request.Request, pk: str):
        
        # Retrieve object from DB
        subscription = self.get_object()
        subscription_obj = cast(models.layer_subscriptions.LayerSubscription, subscription)
        
        # Validation check
        data = request.data
        data['type'] = subscription_obj.type
        data = validate_request(self.serializer_classes['update'], data)
        
        if subscription_obj.is_locked():
             return response.Response({'error_msg':f'This  subscription "{pk}" is locked.'}, 
                                      content_type='application/json', status=status.HTTP_404_NOT_FOUND)
        
        # Convert string numbers to integer
        for key in data:
            if key in ['workspace', 'connection_timeout', 'max_connections', 'read_timeout'] and data.get(key) is not None:
                data[key] = int(data.get(key))
        
        ### Update subscription
        # Check workspace
        workspace = None
        if 'workspace' in data:
            workspace = publish_models.workspaces.Workspace.objects.filter(id=data.get('workspace'))
            if not workspace.exists():
                return response.Response({'error_msg':f"workspace '{data.get('workspace')}' does not exist."}, 
                                        content_type='application/json', status=status.HTTP_400_BAD_REQUEST)
            data['workspace'] = workspace.first()
        
        for key in data:
            setattr(subscription_obj, key, data[key])
        
        subscription_obj.save()
        
        return response.Response({'msg':"success"}, content_type='application/json', status=status.HTTP_200_OK)
            
    
    @drf_utils.extend_schema(request=None, responses={status.HTTP_204_NO_CONTENT: None})
    @decorators.action(detail=True, methods=["POST"])
    def lock(self, request: request.Request, pk: str) -> response.Response:
        """Locks the Layer Subscription.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Layer Subscription.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Retrieve Layer Subscription
        # Help `mypy` by casting the resulting object to a Layer Subscription
        subscription = self.get_object()
        subscription = cast(models.layer_subscriptions.LayerSubscription, subscription)

        # Lock
        success = subscription.lock()

        # Check Success
        if success:
            # Add Action Log Entry
            logs_utils.add_to_actions_log(
                user=request.user,
                model=subscription,
                action="Layer Subscription was locked"
            )

        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @drf_utils.extend_schema(request=None, responses={status.HTTP_204_NO_CONTENT: None})
    @decorators.action(detail=True, methods=["POST"])
    def unlock(self, request: request.Request, pk: str) -> response.Response:
        """Unlocks the Layer Subscription.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Layer Subscription.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Retrieve Layer Subscription
        # Help `mypy` by casting the resulting object to a Layer Subscription
        subscription = self.get_object()
        subscription = cast(models.layer_subscriptions.LayerSubscription, subscription)

        # Unlock
        success = subscription.unlock()

        # Check Success
        if success:
            # Add Action Log Entry
            logs_utils.add_to_actions_log(
                user=request.user,
                model=subscription,
                action="Layer Subscription was unlocked"
            )

        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    # @drf_utils.extend_schema(request=None, responses={status.HTTP_204_NO_CONTENT: None})
    # @decorators.action(detail=True, methods=["POST"])
    # def decline(self, request: request.Request, pk: str) -> response.Response:
    #     """Declines the Layer Subscription.

    #     Args:
    #         request (request.Request): API request.
    #         pk (str): Primary key of the Layer Subscription.

    #     Returns:
    #         response.Response: Empty response confirming success.
    #     """
    #     # Retrieve Layer Subscription
    #     # Help `mypy` by casting the resulting object to a Layer Subscription
    #     catalogue_entry = self.get_object()
    #     catalogue_entry = cast(models.catalogue_entries.CatalogueEntry, catalogue_entry)

    #     # Decline
    #     success = catalogue_entry.decline()

    #     # Check Success
    #     if success:
    #         # Add Action Log Entry
    #         logs_utils.add_to_actions_log(
    #             user=request.user,
    #             model=catalogue_entry,
    #             action="Catalogue entry was declined"
    #         )

    #     # Return Response
    #     return response.Response(status=status.HTTP_204_NO_CONTENT)

    @drf_utils.extend_schema(request=None, responses={status.HTTP_204_NO_CONTENT: None})
    @decorators.action(detail=True, methods=["POST"], url_path=r"assign/(?P<user_pk>\d+)")
    def assign(self, request: request.Request, pk: str, user_pk: str) -> response.Response:
        """Assigns the Layer Subscription.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Layer Subscription.
            user_pk (str): Primary key of the User to assign to.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Retrieve Layer Subscription
        # Help `mypy` by casting the resulting object to a Layer Subscription
        subscription = self.get_object()
        subscription = cast(models.layer_subscriptions.LayerSubscription, subscription)

        # Retrieve User
        user = shortcuts.get_object_or_404(UserModel, id=user_pk)

        # Assign!
        success = subscription.assign(user)

        # Check Success
        if success:
            # Add Action Log Entry
            logs_utils.add_to_actions_log(
                user=request.user,
                model=subscription,
                action=f"Layer Subscription was assigned to {user} (id: {user.pk})"
            )

        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @drf_utils.extend_schema(request=None, responses={status.HTTP_204_NO_CONTENT: None})
    @decorators.action(detail=True, methods=["POST"])
    def unassign(self, request: request.Request, pk: str) -> response.Response:
        """Unassigns the Layer Subscription.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Layer Subscription.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Retrieve Layer Subscription
        # Help `mypy` by casting the resulting object to a Layer Subscription
        subscription = self.get_object()
        subscription = cast(models.layer_subscriptions.LayerSubscription, subscription)

        # Unassign!
        success = subscription.unassign()

        # Check Success
        if success:
            # Add Action Log Entry
            logs_utils.add_to_actions_log(
                user=request.user,
                model=subscription,
                action="Layer Subscription was unassigned"
            )

        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)
    
    @drf_utils.extend_schema(
        request=serializers.catalogue_entries.CatalogueEntryCreateSubscriptionMappingSerializer,
        responses={status.HTTP_204_NO_CONTENT: None})
    @decorators.action(detail=True, methods=["POST"], url_path="mapping")
    def mapping(self, request: request.Request, pk: str,) -> response.Response:
        """Add mapping to target service.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Layer Subscription.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Retrieve Layer Subscription
        # Help `mypy` by casting the resulting object to a Layer Subscription
        subscription = self.get_object()
        subscription = cast(models.layer_subscriptions.LayerSubscription, subscription)
        
         # Validation Check
        data = validate_request(serializers.catalogue_entries.CatalogueEntryCreateSubscriptionMappingSerializer, request.data)
        
        # Set Type
        catalogue_type = models.catalogue_entries.CatalogueEntryType.SUBSCRIPTION_WFS
        if subscription.type == models.layer_subscriptions.LayerSubscriptionType.WFS:
            catalogue_type = models.catalogue_entries.CatalogueEntryType.SUBSCRIPTION_WFS
        elif subscription.type == models.layer_subscriptions.LayerSubscriptionType.WMS:
            catalogue_type = models.catalogue_entries.CatalogueEntryType.SUBSCRIPTION_WMS
        elif subscription.type == models.layer_subscriptions.LayerSubscriptionType.POST_GIS:
            catalogue_type = models.catalogue_entries.CatalogueEntryType.SUBSCRIPTION_POSTGIS
            
        # Create Catalogue Entry
        catalogue_entry = models.catalogue_entries.CatalogueEntry.objects.create(
            name=data['name'],
            description=data['description'] if 'description' in data else None,
            mapping_name=data['mapping_name'],
            type=catalogue_type,
            layer_subscription=subscription
        )
        logger.info(f'New CatalogueEntry: [{catalogue_entry}] has been created.')
        
        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)
    
    @drf_utils.extend_schema(
        request=serializers.catalogue_entries.CatalogueEntryUpdateSubscriptionMappingSerializer,
        responses={status.HTTP_204_NO_CONTENT: None})
    @decorators.action(detail=True, methods=["PUT"], url_path=r"mapping/(?P<catalogue_id>\d+)")
    def update_mapping(self, request: request.Request, pk: str, catalogue_id: str) -> response.Response:
        """Update mapping to target service.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Layer Subscription.
            catalogue_id (str): Primary key of the Catalogue Entry.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Retrieve Layer Subscription
        # Help `mypy` by casting the resulting object to a Layer Subscription
        subscription = self.get_object()
        subscription = cast(models.layer_subscriptions.LayerSubscription, subscription)
        
        # Check Catalogue Entry
        if not models.catalogue_entries.CatalogueEntry.objects.filter(id=catalogue_id).exists():
            return response.Response({'error_msg':f'catalogue entry({catalogue_id}) does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        catalogue_entry = models.catalogue_entries.CatalogueEntry.objects.get(id=catalogue_id)
        
        # Validation check
        data = validate_request(serializers.catalogue_entries.CatalogueEntryUpdateSubscriptionMappingSerializer, request.data)
        
        # Update Catalogue Entry
        catalogue_entry.name = data['name']
        catalogue_entry.description = data['description']
        catalogue_entry.mapping_name = data['mapping_name']
        
        catalogue_entry.save()
        
        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)
    
    @drf_utils.extend_schema(
        request=serializers.catalogue_entries.CatalogueEntryGetSubscriptionMappingSerializer,
        responses={status.HTTP_200_OK: None})
    @mapping.mapping.get
    def get_mapping(self, request: request.Request, pk: str) -> response.Response:
        """Add mapping to target service.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Layer Subscription.

        Returns:
            response.Response: A dictionary of mapping data.
        """
        # Retrieve Layer Subscription
        # Help `mypy` by casting the resulting object to a Layer Subscription
        subscription = self.get_object()
        subscription = cast(models.layer_subscriptions.LayerSubscription, subscription)
        
        # Retrieve Catalogue Entry with Layer Submission Id
        mappings = list(models.catalogue_entries.CatalogueEntry.objects
                             .filter(layer_subscription=subscription)
                             .values('id', 'mapping_name', 'layer_subscription', 'name', 'description'))
        if not mappings:
            mappings = {}
        else:
            mappings = {mapping['mapping_name']:{
                            'name':mapping['name'],
                            'description':mapping['description'],
                            'catalogue_entry_id':mapping['id']}
                        for mapping in mappings}
            
        # Return Response
        return response.Response({'results':mappings}, content_type='application/json', status=status.HTTP_200_OK)
    
    @drf_utils.extend_schema(
        request=serializers.catalogue_entries.CatalogueEntryUpdateSubscriptionMappingSerializer,
        responses={status.HTTP_200_OK: None})
    @decorators.action(detail=True, methods=["GET"], url_path="mapping/source")
    def get_mapping_source(self, request: request.Request, pk: str) -> response.Response:
        """Response mapping source.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Layer Subscription.

        Returns:
            response.Response: A list of mapping source names
        """
        # Retrieve Layer Subscription
        # Help `mypy` by casting the resulting object to a Layer Subscription
        subscription = self.get_object()
        subscription_obj = cast(models.layer_subscriptions.LayerSubscription, subscription)
        LayerSubscriptionType = models.layer_subscriptions.LayerSubscriptionType

        def cache_or_callback(key, callback):
            val = cache.get(key)
            if not val:
                try:
                    val = callback()
                    cache.set(key, val, conf.settings.SUBSCRIPTION_CACHE_TTL)
                except Exception as e:
                    print(e)
            return val
        
        if subscription_obj.type == LayerSubscriptionType.WMS:
            def get_wms():
                res = WebMapService(url=subscription_obj.url, 
                                    username=subscription_obj.username, 
                                    password=subscription_obj.userpassword)
                # return [key.replace(':', '_') for key in res.contents.keys()]
                return res.contents.keys()
            mapping_names = cache_or_callback(conf.settings.WMS_CACHE_KEY + str(subscription_obj.id), get_wms)
        elif subscription_obj.type == LayerSubscriptionType.WFS:
            def get_wfs():
                res = WebFeatureService(url=subscription_obj.url, 
                                    username=subscription_obj.username, 
                                    password=subscription_obj.userpassword)
                # return [key.replace(':', '_') for key in res.contents.keys()]
                return res.contents.keys()
            mapping_names = cache_or_callback(conf.settings.WFS_CACHE_KEY + str(subscription_obj.id), get_wfs)
        elif subscription_obj.type == LayerSubscriptionType.POST_GIS:
            def get_post_gis():
                conn = psycopg2.connect(
                    host=subscription_obj.host,
                    database=subscription_obj.database,
                    user=subscription_obj.username,
                    password=subscription_obj.userpassword,
                    port=subscription_obj.port
                )
                query = """
                            SELECT table_name 
                            FROM information_schema.tables 
                            WHERE table_schema = %s;
                        """
                with conn.cursor() as cursor:
                    cursor.execute(query, [subscription_obj.schema])
                    return [e[0] for e in cursor.fetchall()]
            mapping_names = cache_or_callback(conf.settings.POST_GIS_CACHE_KEY + str(subscription_obj.id), get_post_gis)
        
        # Return Response
        return response.Response({'results':mapping_names}, content_type='application/json', status=status.HTTP_200_OK)
        
    @transaction.atomic()
    @drf_utils.extend_schema(
        request=serializers.catalogue_entries.CatalogueEntryCreateSubscriptionQuerySerializer,
        responses={status.HTTP_204_NO_CONTENT: None})
    @decorators.action(detail=True, methods=["POST"], url_path="query")
    def query(self, request: request.Request, pk: str,) -> response.Response:
        """Add a custom query.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Layer Subscription.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Retrieve Layer Subscription
        # Help `mypy` by casting the resulting object to a Layer Subscription
        subscription = self.get_object()
        subscription = cast(models.layer_subscriptions.LayerSubscription, subscription)
        
        # Validation check
        data = validate_request(serializers.catalogue_entries.CatalogueEntryCreateSubscriptionQuerySerializer, request.data)
        if 'frequency_type' not in request.data:
            raise ValidationError("frequency_type is required")
        frequency_type = request.data['frequency_type']
        if ('frequency_options' not in request.data or
            type(request.data['frequency_options']) != list):
            raise ValidationError("frequency_options is required")
        frequency_options = request.data['frequency_options']
        self._validate_frequency(frequency_type, frequency_options)
            
        # Create Catalogue Entry
        catalogue_entry = models.catalogue_entries.CatalogueEntry.objects.create(
            name=data['name'],
            description=data['description'] if 'description' in data else None,
            sql_query=data['sql_query'],
            type=models.catalogue_entries.CatalogueEntryType.SUBSCRIPTION_QUERY,
            layer_subscription=subscription
        )
        logger.info(f'New CatalogueEntry: [{catalogue_entry}] has been created.')
        
        # Create Custom Query Frequency
        for option in frequency_options:
            freq_options = self._make_frequency_option(frequency_type, option)
            freq_options['catalogue_entry'] = catalogue_entry
            freq_options['type'] = frequency_type
            models.custom_query_frequency.CustomQueryFrequency.objects.create(**freq_options)
        
        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)
    
    def _validate_frequency(self, frequency_type, frequency_options):
        for option in frequency_options:
            if frequency_type == models.custom_query_frequency.FrequencyType.EVERY_MINUTES:
                if 'minutes' not in option:
                    raise ValidationError("minutes is required if FrequencyType is EVERY_MINUTES(1)")
            elif frequency_type == models.custom_query_frequency.FrequencyType.EVERY_HOURS:
                if 'hours' not in option:
                    raise ValidationError("hours is required if FrequencyType is EVERY_HOURS(2)")
                pass
            elif frequency_type == models.custom_query_frequency.FrequencyType.DAILY:
                if 'hour' not in option or 'minute' not in option:
                    raise ValidationError("hour and minute is required if FrequencyType is DAILY(3)")
            elif frequency_type == models.custom_query_frequency.FrequencyType.WEEKLY:
                if 'hour' not in option or 'minute' not in option or 'day' not in option:
                    raise ValidationError("hour, minute, and day is required if FrequencyType is WEEKLY(4)")
            elif frequency_type == models.custom_query_frequency.FrequencyType.MONTHLY:
                if 'hour' not in option or 'minute' not in option or 'date' not in option:
                    raise ValidationError("hour, minute, and date is required if FrequencyType is MONTHLY(4)")
                
    def _make_frequency_option(self, frequency_type, option):
        freq_options = {}
        
        if frequency_type == models.custom_query_frequency.FrequencyType.EVERY_MINUTES:
            freq_options['every_minutes'] = option['minutes']
        elif frequency_type == models.custom_query_frequency.FrequencyType.EVERY_HOURS:
            freq_options['every_hours'] = option['hours']
        elif frequency_type == models.custom_query_frequency.FrequencyType.DAILY:
            freq_options['hour'] = option['hour']
            freq_options['minute'] = option['minute']
        elif frequency_type == models.custom_query_frequency.FrequencyType.WEEKLY:
            freq_options['hour'] = option['hour']
            freq_options['minute'] = option['minute']
            freq_options['day_of_week'] = option['day']
        elif frequency_type == models.custom_query_frequency.FrequencyType.MONTHLY:
            freq_options['hour'] = option['hour']
            freq_options['minute'] = option['minute']
            freq_options['date'] = option['date']
            
        return freq_options
    
    @transaction.atomic()
    @drf_utils.extend_schema(
        request=serializers.catalogue_entries.CatalogueEntryUpdateSubscriptionQuerySerializer,
        responses={status.HTTP_204_NO_CONTENT: None})
    @decorators.action(detail=True, methods=["PUT"], url_path=r"query/(?P<catalogue_id>\d+)")
    def update_query(self, request: request.Request, pk: str, catalogue_id: str) -> response.Response:
        """Update a custom query.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Layer Subscription.

        Returns:
            response.Response: Empty response confirming success.
        """
        # Retrieve Layer Subscription
        # Help `mypy` by casting the resulting object to a Layer Subscription
        subscription = self.get_object()
        subscription = cast(models.layer_subscriptions.LayerSubscription, subscription)
        
         # Validation check
        data = validate_request(serializers.catalogue_entries.CatalogueEntryUpdateSubscriptionQuerySerializer, request.data)
        
        # Update Catalogue Entry
        catalogue_entry = models.catalogue_entries.CatalogueEntry.objects.get(pk=catalogue_id)
        catalogue_entry.name = data['name'] if 'name' in data else catalogue_entry.name
        catalogue_entry.description = data['description'] if 'description' in data else catalogue_entry.description
        catalogue_entry.sql_query = data['sql_query'] if 'sql_query' in data else catalogue_entry.sql_query
        catalogue_entry.force_run_postgres_scanner = True if request.data.get('force_run_postgres_scanner', False) else False
        catalogue_entry.save()
        
        # Validation check
        data = validate_request(serializers.catalogue_entries.CatalogueEntryCreateSubscriptionQuerySerializer, request.data)
        if 'frequency_type' not in request.data:
            raise ValidationError("frequency_type is required")
        frequency_type = request.data['frequency_type']
        if ('frequency_options' not in request.data or
            type(request.data['frequency_options']) != list):
            raise ValidationError("frequency_options is required")
        frequency_options = request.data['frequency_options']
        self._validate_frequency(frequency_type, frequency_options)
        
        # Update Custom Query Frequency
        models.custom_query_frequency.CustomQueryFrequency.objects.filter(catalogue_entry=catalogue_entry).delete()
        for option in frequency_options:
            freq_options = self._make_frequency_option(frequency_type, option)
            freq_options['catalogue_entry'] = catalogue_entry
            freq_options['type'] = frequency_type
            models.custom_query_frequency.CustomQueryFrequency.objects.create(**freq_options)
        
        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)
    
    @drf_utils.extend_schema(
        request=serializers.catalogue_entries.CatalogueEntryGetSubscriptionQuerySerializer,
        responses={status.HTTP_200_OK: None})
    # @decorators.action(detail=True, methods=["GET"], url_path="query")
    @query.mapping.get
    def get_query(self, request: request.Request, pk: str) -> response.Response:
        """get a custom query.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Layer Subscription.

        Returns:
            response.Response: A dictionary of mapping data.
        """
        # Retrieve Layer Subscription
        # Help `mypy` by casting the resulting object to a Layer Subscription
        subscription = self.get_object()
        subscription = cast(models.layer_subscriptions.LayerSubscription, subscription)
        
        # Retrieve Catalogue Entry with Layer Submission Id
        catalogue_entries = subscription.catalogue_entries.filter(sql_query__isnull=False).prefetch_related('custom_query_frequencies').all()
        results = []
        for catalogue_entry in catalogue_entries:
            frequencies = []
            for freq in catalogue_entry.custom_query_frequencies.all():
                frequencies.append({
                    'type':freq.type, 
                    'type_label': freq.get_type_display(),
                    'minutes':freq.every_minutes, 
                    'hours':freq.every_hours,
                    'hour':freq.hour,
                    'minute':freq.minute,
                    'day':freq.day_of_week,
                    'date':freq.date,
                })
            results.append({
                'id': catalogue_entry.id,
                'name': catalogue_entry.name,
                'description' : catalogue_entry.description,
                'sql_query' : catalogue_entry.sql_query,
                'frequencies' : frequencies,
                'force_run_postgres_scanner': catalogue_entry.force_run_postgres_scanner,
            })
            
        # Return Response
        return response.Response({'results':results}, content_type='application/json', status=status.HTTP_200_OK)
    
    @decorators.action(detail=True, methods=["POST"], url_path=r"convert-query/(?P<catalogue_id>\d+)")
    def convert_query(self, request: request.Request, pk: str, catalogue_id: str) -> response.Response:
        try:
            catalogue_entry_obj = shortcuts.get_object_or_404(models.catalogue_entries.CatalogueEntry, id=catalogue_id)
            new_path = Scanner.run_postgres_to_shapefile(catalogue_entry_obj)
            return response.Response({'message': f'[CE{catalogue_entry_obj.id}: {catalogue_entry_obj.name}] has been converted to the shapefile: [{new_path}].'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return response.Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @drf_utils.extend_schema(
        request=serializers.catalogue_entries.CatalogueEntryGetSubscriptionQuerySerializer,
        responses={status.HTTP_200_OK: None})
    @decorators.action(detail=True, methods=["DELETE"], url_path=r"delete-query/(?P<catalogue_id>\d+)")
    def delete_query(self, request: request.Request, pk: str, catalogue_id: str) -> response.Response:
        """delete a custom query.

        Args:
            request (request.Request): API request.
            pk (str): Primary key of the Layer Subscription.

        Returns:
            response.Response: A dictionary of mapping data.
        """
        # Retrieve Catalogue Entry with Layer Submission Id
        models.catalogue_entries.CatalogueEntry.objects.get(pk=catalogue_id).delete()
            
        # Return Response
        return response.Response(status=status.HTTP_204_NO_CONTENT)
    
@drf_utils.extend_schema(tags=["Catalogue - Layer Symbology"])
class LayerSymbologyViewSet(
    mixins.ChoicesMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Layer Symbology View Set."""
    queryset = models.layer_symbology.LayerSymbology.objects.all()
    serializer_class = serializers.layer_symbology.LayerSymbologySerializer
    filterset_class = filters.LayerSymbologyFilter
    search_fields = ["catalogue_entry__name"]
    permission_classes = [permissions.HasCatalogueEntryPermissions | accounts_permissions.IsInAdministratorsGroup]


@drf_utils.extend_schema(tags=["Catalogue - Notifications (Email)"])
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
    permission_classes = [permissions.HasCatalogueEntryPermissions | accounts_permissions.IsInAdministratorsGroup]
    
    # to pass the pk to serializer
    def get_serializer_context(self):
        context = super().get_serializer_context()
        if context['request'].method == 'PUT':
            context['pk'] = self.kwargs['pk']
        return context
    

@drf_utils.extend_schema(tags=["Catalogue - Notifications (Webhook)"])
class WebhookNotificationViewSet(
    mixins.ChoicesMixin,
    mixins.MultipleSerializersMixin,
    viewsets.mixins.CreateModelMixin,
    viewsets.mixins.DestroyModelMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Webhook Notification View Set."""
    queryset = models.notifications.WebhookNotification.objects.all()
    serializer_class = serializers.notifications.WebhookNotificationSerializer
    serializer_classes = {"create": serializers.notifications.WebhookNotificationCreateSerializer}
    filterset_class = filters.WebhookNotificationFilter
    search_fields = ["name", "url"]
    permission_classes = [permissions.HasCatalogueEntryPermissions | accounts_permissions.IsInAdministratorsGroup]
    
@drf_utils.extend_schema(tags=["Catalogue - Permissions"])
class CataloguePermissionViewSet(
    mixins.MultipleSerializersMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.CreateModelMixin,
    viewsets.mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):      
    """Catalogue Permission View Set."""
    queryset = models.permission.CatalogueEntryPermission.objects.all()
    serializer_class = serializers.permission.CatalogueEntryPermissionSerializer
    serializer_classes = {"create": serializers.permission.CatalogueEntryPermissionCreateSerializer}
    filterset_class = filters.CataloguePermissionFilter
    permission_classes = [permissions.HasCatalogueEntryPermissions | accounts_permissions.IsInAdministratorsGroup]
    pagination_class = None
