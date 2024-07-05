"""Kaartdijin Boodja Accounts Django Application Views."""

import os

# Third-Party
from django.contrib import auth
from django.contrib.auth import models
from django.http import FileResponse, HttpResponseForbidden
from drf_spectacular import utils
from rest_framework import decorators
from rest_framework import request
from rest_framework import response
from rest_framework import viewsets
from rest_framework import views
from rest_framework import permissions


# Local
from govapp import settings
from govapp.apps.accounts import serializers
from govapp.apps.accounts import filters


# Shortcuts
UserModel = auth.get_user_model()
GroupModel = models.Group


@utils.extend_schema(tags=["Accounts - Users"])
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """User View Set."""
    queryset = UserModel.objects.all()
    serializer_class = serializers.UserSerializer
    filterset_class = filters.UserFilter

    @utils.extend_schema(request=None, responses=serializers.UserSerializer)
    @decorators.action(detail=False, methods=["GET"])
    def me(self, request: request.Request) -> response.Response:
        """Retrieves the currently logged in user.

        Args:
            request (request.Request): API request.

        Returns:
            response.Response: The currently logged in user if applicable.
        """
        # Retrieve User
        instance = request.user

        # Serialize User
        serializer = self.get_serializer(instance)

        # Return Response
        return response.Response(serializer.data)


@utils.extend_schema(tags=["Accounts - Groups"])
class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """Group View Set."""
    queryset = GroupModel.objects.all()
    serializer_class = serializers.GroupSerializer


class FileListView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        config_path = os.path.join(settings.BASE_DIR, 'config')
        files = []
        # Recursively collect all files
        for root, _, file_names in os.walk(config_path):
            for file_name in file_names:
                file_path = os.path.join(root, file_name)
                files.append(file_path.replace(config_path + os.sep, ''))  # Remove base directory from path
        return response.Response(files)


class FileDownloadView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        file_path = request.query_params.get('file_path', None)
        
        if not file_path:
            return response.Response({'error': 'File path is required as query parameter.'}, status=400)
        
        # Construct full path
        config_path = os.path.join(settings.BASE_DIR, 'config')
        file_full_path = os.path.join(config_path, file_path)

        # Check if the file is within the config directory and is a file
        common_path = os.path.commonpath([file_full_path, config_path,])
        if common_path == config_path and os.path.exists(file_full_path) and os.path.isfile(file_full_path):
            try:
                return FileResponse(open(file_full_path, 'rb'), as_attachment=True, filename=os.path.basename(file_full_path))
            except Exception as e:
                return response.Response({'error': str(e)}, status=500)
        else:
            return HttpResponseForbidden("You do not have permission to access this file.")