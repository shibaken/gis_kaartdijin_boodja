"""Django project views."""


# Third-Party
import os
from django import http
from django import shortcuts
from django.views.generic import base
from django.contrib import auth
from django import conf
from django.core.cache import cache
from owslib.wms import WebMapService
import json

# Internal
from govapp import settings
from govapp.apps.catalogue.models import catalogue_entries as catalogue_entries_models
from govapp.apps.publisher.models import publish_entries as publish_entries_models
from govapp.apps.catalogue.models import custodians as custodians_models
from govapp.apps.publisher.models import workspaces as publish_workspaces_models
from govapp.apps.catalogue.models import layer_symbology as catalogue_layer_symbology_models
from govapp.apps.catalogue.models import layer_attributes as catalogue_layer_attribute_models
from govapp.apps.catalogue.models import layer_metadata as catalogue_layer_metadata_models
from govapp.apps.catalogue.models import layer_submissions as catalogue_layer_submissions_models
from govapp.apps.catalogue.models import layer_subscriptions as catalogue_layer_subscription_models
from govapp.apps.catalogue import utils as catalogue_utils
from govapp.apps.accounts import utils

# Typing
from typing import Any

from govapp.apps.publisher.models.geoserver_pools import GeoServerPool

UserModel = auth.get_user_model()


class HomePage(base.TemplateView):
    """Home page view."""

    # Template name
    template_name = "govapp/home.html"

    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        """Provides the GET request endpoint for the HomePage view.

        Args:
            request (http.HttpRequest): The incoming HTTP request.
            *args (Any): Extra positional arguments.
            **kwargs (Any): Extra keyword arguments.

        Returns:
            http.HttpResponse: The rendered template response.
        """
        # Construct Context
        context: dict[str, Any] = {}
        return http.HttpResponseRedirect('/catalogue/entries/')
        # Render Template and Return
        return shortcuts.render(request, self.template_name, context)

class OldCatalogueVue(base.TemplateView):
    """Home page view."""

    # Template name
    template_name = "govapp/home.html"

    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        """Provides the GET request endpoint for the HomePage view.

        Args:
            request (http.HttpRequest): The incoming HTTP request.
            *args (Any): Extra positional arguments.
            **kwargs (Any): Extra keyword arguments.

        Returns:
            http.HttpResponse: The rendered template response.
        """
        # Construct Context
        context: dict[str, Any] = {}

        # Render Template and Return
        return shortcuts.render(request, self.template_name, context)


class PendingImportsView(base.TemplateView):
    template_name = "govapp/pending_imports.html"

    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        pathToFolder = settings.PENDING_IMPORT_PATH
        file_list = os.listdir(pathToFolder)

        context = {'file_list': file_list}
        return shortcuts.render(request, self.template_name, context)

class ManagementCommandsView(base.TemplateView):
    """Home page view."""

    # Template name
    template_name = "govapp/management_commands.html"

    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        # Construct Context
        context: dict[str, Any] = {}

        # Render Template and Return
        return shortcuts.render(request, self.template_name, context)

class PublishPage(base.TemplateView):
    """Home page view."""

    # Template name
    template_name = "govapp/publish.html"

    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        """Provides the GET request endpoint for the HomePage view.

        Args:
            request (http.HttpRequest): The incoming HTTP request.
            *args (Any): Extra positional arguments.
            **kwargs (Any): Extra keyword arguments.

        Returns:
            http.HttpResponse: The rendered template response.
        """
        # Construct Context
        context: dict[str, Any] = {}
        pe_list = []
        catalogue_entry_list = []

        # START - To be improved later todo a reverse table join      
        ce_obj = catalogue_entries_models.CatalogueEntry.objects.all()
        pe_obj = publish_entries_models.PublishEntry.objects.all()

        for pe in pe_obj:            
            pe_list.append(pe.catalogue_entry.id)

        for ce in ce_obj:
            if ce.id not in pe_list:
                catalogue_entry_list.append({'id': ce.id, 'name': ce.name})
                   
        is_administrator = utils.is_administrator(request.user)

        # END - To be improved later todo a reverse table join    
        context['catalogue_entry_list'] = catalogue_entry_list
        context['is_administrator'] = is_administrator
        # context['catalogue_entry_list'] = []

        # Render Template and Return
        return shortcuts.render(request, self.template_name, context)
    
class PublishView(base.TemplateView):
    """Home page view."""

    # Template name
    template_name = "govapp/publish_view.html"

    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        """Provides the GET request endpoint for the HomePage view.

        Args:
            request (http.HttpRequest): The incoming HTTP request.
            *args (Any): Extra positional arguments.
            **kwargs (Any): Extra keyword arguments.

        Returns:
            http.HttpResponse: The rendered template response.
        """
        # Construct Context
        context: dict[str, Any] = {}
        has_edit_access = False
        pe_list = []
        catalogue_entry_list = []
        custodians_obj = custodians_models.Custodian.objects.all()
        publish_entry_obj = publish_entries_models.PublishEntry.objects.get(id=self.kwargs['pk'])
        publish_workspaces = publish_workspaces_models.Workspace.objects.all()
        publish_workspace_list = [{'id': ws.id, 'name': ws.name} for ws in publish_workspaces]
        geoserver_pools = GeoServerPool.objects.filter(enabled=True)

        ### START - To be improved later todo a reverse table join      
        # This code lists CatalogueEntries not associated with any PublishEntry, along with CatalogueEntries associated with a specific PublishEntry.
        ce_obj = catalogue_entries_models.CatalogueEntry.objects.all()
        pe_obj = publish_entries_models.PublishEntry.objects.all()

        for pe in pe_obj:            
            pe_list.append(pe.catalogue_entry.id)

        for ce in ce_obj:
            if ce.id not in pe_list:
                catalogue_entry_list.append({'id': ce.id, 'name': ce.name})
                  
            if publish_entry_obj.catalogue_entry:  
                if ce.id == publish_entry_obj.catalogue_entry.id:
                    catalogue_entry_list.append({'id': ce.id, 'name': ce.name})
        ### END - To be improved later todo a reverse table join     

        system_users_list = []
        # system_users_obj = UserModel.objects.filter(is_active=True, groups__name=conf.settings.GROUP_ADMINISTRATOR_NAME)
        system_users_obj = UserModel.objects.filter(is_active=True, groups__name=settings.GROUP_ADMINISTRATORS)
        for su in system_users_obj:
            system_users_list.append({'first_name': su.first_name, 'last_name': su.last_name, 'id': su.id, 'email': su.email})

        geoserver_pool_list = {}
        for gsp in geoserver_pools:
            geoserver_pool_list[gsp.id] = gsp.name
                
        is_administrator = utils.is_administrator(request.user)
        if is_administrator is True and  publish_entry_obj.status == 2 and request.user == publish_entry_obj.assigned_to:
            has_edit_access = True

        context['catalogue_entry_list'] = catalogue_entry_list
        context['publish_entry_obj'] = publish_entry_obj
        context['publishable_to_cddp'] = publish_entry_obj.publishable_to_cddp
        context['publishable_to_ftp'] = publish_entry_obj.publishable_to_ftp
        context['custodians_obj'] = custodians_obj
        context['system_users'] = system_users_list
        context['publish_id'] = self.kwargs['pk']
        context['has_edit_access'] = has_edit_access
        context['publish_workspaces'] = publish_workspaces
        context['publish_workspace_list'] = publish_workspace_list
        context['geoserver_pools'] = geoserver_pools
        context['geoserver_pool_list_json'] = json.dumps(geoserver_pool_list)
    
        # Render Template and Return
        return shortcuts.render(request, self.template_name, context)
        

class CatalogueEntriesPage(base.TemplateView):
    """Home page view."""

    # Template name
    template_name = "govapp/catalogue_entries.html"

    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        """Provides the GET request endpoint for the HomePage view.

        Args:
            request (http.HttpRequest): The incoming HTTP request.
            *args (Any): Extra positional arguments.
            **kwargs (Any): Extra keyword arguments.

        Returns:
            http.HttpResponse: The rendered template response.
        """
        # Construct Context
        context: dict[str, Any] = {}
        pe_list = []
        catalogue_entry_list = []

        debug = request.GET.get('debug', False)

        # START - To be improved later todo a reverse table join      
        ce_obj = catalogue_entries_models.CatalogueEntry.objects.all()
        pe_obj = publish_entries_models.PublishEntry.objects.all()

        for pe in pe_obj:            
            pe_list.append(pe.catalogue_entry.id)

        for ce in ce_obj:
            if debug == 'true':
                catalogue_entry_list.append({'id': ce.id, 'name': ce.name})
            else:
                if ce.id not in pe_list:
                    catalogue_entry_list.append({'id': ce.id, 'name': ce.name})
                
        # END - To be improved later todo a reverse table join    
        context['catalogue_entry_list'] = catalogue_entry_list
        context['tab'] = 'catalogue_entries'

        # Render Template and Return
        return shortcuts.render(request, self.template_name, context)
    


class CatalogueEntriesView(base.TemplateView):
    """Home page view."""

    # Template name
    template_name = "govapp/catalogue_entries_view.html"

    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        """Provides the GET request endpoint for the HomePage view.

        Args:
            request (http.HttpRequest): The incoming HTTP request.
            *args (Any): Extra positional arguments.
            **kwargs (Any): Extra keyword arguments.

        Returns:
            http.HttpResponse: The rendered template response.
        """
        # Construct Context
        context: dict[str, Any] = {}
        has_edit_access = False
        pe_list = []
        catalogue_entry_list = []
        catalogue_id = self.kwargs['pk']
        symbology_definition = ''
        catalogue_layer_attributes = ''
        catalogue_layer_metadata = None

        custodians_obj = custodians_models.Custodian.objects.all()
        catalogue_entry_obj = catalogue_entries_models.CatalogueEntry.objects.get(id=self.kwargs['pk'])

        # publish_workspaces = publish_workspaces_models.Workspace.objects.all()

        # # START - To be improved later todo a reverse table join      
        # ce_obj = catalogue_entries_models.CatalogueEntry.objects.all()
        # pe_obj = publish_entries_models.PublishEntry.objects.all()

        # for pe in pe_obj:            
        #     pe_list.append(pe.catalogue_entry.id)

        # for ce in ce_obj:
        #     if ce.id not in pe_list:
        #         catalogue_entry_list.append({'id': ce.id, 'name': ce.name})
        #         print (ce.id)    
        #     if publish_entry_obj.catalogue_entry:  
        #         if ce.id == publish_entry_obj.catalogue_entry.id:
        #             catalogue_entry_list.append({'id': ce.id, 'name': ce.name})
        # # END - To be improved later todo a reverse table join     

        system_users_dict = {}
        # system_users_obj = UserModel.objects.filter(is_active=True, groups__name=conf.settings.GROUP_ADMINISTRATOR_NAME)
        system_users_obj = UserModel.objects.filter(is_active=True, groups__name=settings.GROUP_ADMINISTRATORS)
        for su in system_users_obj:
             system_users_dict[su.id] = {'first_name': su.first_name, 'last_name': su.last_name, 'id': su.id, 'email': su.email}
        
        for permission in catalogue_entry_obj.catalouge_permissions.all():
            system_users_dict[permission.user.id] = {
                'first_name': permission.user.first_name, 
                'last_name': permission.user.last_name, 
                'id': permission.user.id, 
                'email': permission.user.email}
            
        system_users_list = [system_users_dict[key] for key in system_users_dict]
        
                
        is_administrator = utils.is_administrator(request.user)
        if is_administrator is True and request.user == catalogue_entry_obj.assigned_to:
             if catalogue_entry_obj.status == 1 or catalogue_entry_obj.status == 4 or catalogue_entry_obj.status ==5:
                has_edit_access = True

        catalogue_layer_symbology_obj = catalogue_layer_symbology_models.LayerSymbology.objects.filter(catalogue_entry=catalogue_id)
        if catalogue_layer_symbology_obj.count() > 0:
            symbology_definition = catalogue_layer_symbology_obj[0]

        catalogue_layer_metadata_obj = catalogue_layer_metadata_models.LayerMetadata.objects.filter(catalogue_entry=catalogue_id)
        if catalogue_layer_metadata_obj.count() > 0:
            catalogue_layer_metadata = catalogue_layer_metadata_obj[0]

        catalogue_layer_attributes = catalogue_layer_attribute_models.LayerAttribute.objects.filter(catalogue_entry=catalogue_id)

        # context['catalogue_entry_list'] = catalogue_entry_list
        context['catalogue_entry_obj'] = catalogue_entry_obj
        context['custodians_obj'] = custodians_obj
        context['system_users'] = system_users_list
        context['catalogue_entry_id'] = self.kwargs['pk']
        context['tab'] = self.kwargs['tab']
        context['symbology_definition'] = symbology_definition
        context['catalogue_layer_metadata'] = catalogue_layer_metadata
        context['has_edit_access'] = has_edit_access
        context['catalogue_layer_attributes'] = catalogue_layer_attributes
        
    
        # Render Template and Return
        return shortcuts.render(request, self.template_name, context)
        



class LayerSubmission(base.TemplateView):
    """Layer Submissions view."""

    # Template name
    template_name = "govapp/layer_submissions.html"

    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        """Provides the GET request endpoint for the Submissions view.

        Args:
            request (http.HttpRequest): The incoming HTTP request.
            *args (Any): Extra positional arguments.
            **kwargs (Any): Extra keyword arguments.

        Returns:
            http.HttpResponse: The rendered template response.
        """

        # Construct Context
        context: dict[str, Any] = {}
        context['tab'] = 'layer_submission'

        # Render Template and Return
        return shortcuts.render(request, self.template_name, context)    
    

class LayerSubmissionView(base.TemplateView):
    """Layer Submissions view."""

    # Template name
    template_name = "govapp/layer_submissions_view.html"

    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        """Provides the GET request endpoint for the SubmissionsView view.

        Args:
            request (http.HttpRequest): The incoming HTTP request.
            *args (Any): Extra positional arguments.
            **kwargs (Any): Extra keyword arguments.

        Returns:
            http.HttpResponse: The rendered template response.
        """
        pk = self.kwargs['pk']
        layer_submission = catalogue_layer_submissions_models.LayerSubmission.objects.get(id=pk)

        # Construct Context
        context: dict[str, Any] = {}
        context['tab'] = self.kwargs['tab']
        context['layer_submission_obj'] = layer_submission
        context['id'] = layer_submission.catalogue_entry.id

        # Render Template and Return
        return shortcuts.render(request, self.template_name, context)   
    
    # def get_layer_file(request: http.HttpRequest, pk:int):
    #     layer_submission = catalogue_layer_submissions_models.LayerSubmission.objects.get(id=pk)
    #     file_name = os.path.basename(layer_submission.geojson)
    #     with open(layer_submission.geojson, 'rb') as file:
    #         response = http.FileResponse(file)
    #         response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    #         return response
    

class LayerSubscriptions(base.TemplateView):
    """Layer Subscriptions page."""

    # Template name
    template_name = "govapp/layer_subscriptions.html"
      
    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        """Provides the GET request endpoint for the Subscription.

        Args:
            request (http.HttpRequest): The incoming HTTP request.
            *args (Any): Extra positional arguments.
            **kwargs (Any): Extra keyword arguments.

        Returns:
            http.HttpResponse: The rendered template response.
        """
        is_administrator = False
        if utils.is_administrator(request.user) is True:
                is_administrator = True
                
        # Construct Context
        context: dict[str, Any] = {}
        context['is_administrator'] = is_administrator
        context['tab'] = "layer_subscriptions"
        
        # Render Template and Return
        return shortcuts.render(request, self.template_name, context)   
    
class LayerSubscriptionsView(base.TemplateView):
    """Layer Submissions view."""

    # Template name
    template_name = "govapp/layer_subscriptions_view.html"
    
    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        """Provides the GET request endpoint for the Subscription view.

        Args:
            request (http.HttpRequest): The incoming HTTP request.
            *args (Any): Extra positional arguments.
            **kwargs (Any): Extra keyword arguments.

        Returns:
            http.HttpResponse: The rendered template response.
        """
        
        pk = self.kwargs['pk']
        subscription_obj = catalogue_layer_subscription_models.LayerSubscription.objects.get(id=pk)
        LayerSubscriptionStatus = catalogue_layer_subscription_models.LayerSubscriptionStatus
        LayerSubscriptionType = catalogue_layer_subscription_models.LayerSubscriptionType
        
        system_users_list = []
        # system_users_obj = UserModel.objects.filter(is_active=True, groups__name=conf.settings.GROUP_ADMINISTRATOR_NAME)
        system_users_obj = UserModel.objects.filter(is_active=True, groups__name=settings.GROUP_ADMINISTRATORS)
        for su in system_users_obj:
            system_users_list.append({'first_name': su.first_name, 'last_name': su.last_name, 'id': su.id, 'email': su.email})
        has_edit_access = False
        if utils.is_administrator(request.user) is True and request.user == subscription_obj.assigned_to:
             if subscription_obj.status in (LayerSubscriptionStatus.DRAFT, LayerSubscriptionStatus.NEW_DRAFT, LayerSubscriptionStatus.PENDING):
                has_edit_access = True
        
        # Construct Context
        context: dict[str, Any] = {}
        context['subscription_obj'] = subscription_obj
        context['status'] = catalogue_utils.find_enum_by_value(LayerSubscriptionStatus, subscription_obj.status).name.replace('_', ' ')
        context['system_users'] = system_users_list
        context['is_system_user'] = utils.is_administrator(request.user)
        context['has_edit_access'] = has_edit_access
        context['type'] = catalogue_utils.find_enum_by_value(LayerSubscriptionType, subscription_obj.type).name.replace('_', ' ')
        context['workspaces'] = publish_workspaces_models.Workspace.objects.all()
        context['enabled_js'] = "true" if subscription_obj.enabled else "false"
        
        # Render Template and Return
        return shortcuts.render(request, self.template_name, context)        
    

class GeoServerQueue(base.TemplateView):
    """ GeoServer Queue to show Geoserver Queue status """
    
    # Template name
    template_name = "govapp/geoserverqueue.html"


class CDDPQueueView(base.TemplateView):
    """ Show CDDP Queue status """
    
    # Template name
    template_name = "govapp/cddpqueue.html"