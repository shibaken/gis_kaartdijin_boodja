"""Django project views."""


# Third-Party
from django import http
from django import shortcuts
from django.views.generic import base
from django.contrib import auth
from django import conf
from django.core.cache import cache
from owslib.wms import WebMapService
from django.db import connections
import json

# Internal
from govapp.apps.catalogue.models import catalogue_entries as catalogue_entries_models
from govapp.apps.publisher.models import publish_entries as publish_entries_models
from govapp.apps.catalogue.models import custodians as custodians_models
from govapp.apps.publisher.models import workspaces as publish_workspaces_models
from govapp.apps.catalogue.models import layer_symbology as catalogue_layer_symbology_models
from govapp.apps.catalogue.models import layer_metadata as catalogue_layer_metadata_models
from govapp.apps.catalogue.models import layer_submissions as catalogue_layer_submissions_models
from govapp.apps.catalogue.models import layer_subscriptions as catalogue_layer_subscription_models
from govapp.apps.catalogue import utils as catalogue_utils
from govapp.apps.accounts import utils

# Typing
from typing import Any

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
                   

        # END - To be improved later todo a reverse table join    
        context['catalogue_entry_list'] = catalogue_entry_list
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

        # START - To be improved later todo a reverse table join      
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
        # END - To be improved later todo a reverse table join     

        system_users_list = []
        system_users_obj = UserModel.objects.filter(is_active=True, groups__name=conf.settings.GROUP_ADMINISTRATOR_NAME)
        for su in system_users_obj:
            system_users_list.append({'first_name': su.first_name, 'last_name': su.last_name, 'id': su.id, 'email': su.email})
                
        is_administrator = utils.is_administrator(request.user)
        if is_administrator is True and  publish_entry_obj.status == 2 and request.user == publish_entry_obj.assigned_to:
            has_edit_access = True

        context['catalogue_entry_list'] = catalogue_entry_list
        context['publish_entry_obj'] = publish_entry_obj
        context['custodians_obj'] = custodians_obj
        context['system_users'] = system_users_list
        context['publish_id'] = self.kwargs['pk']
        context['has_edit_access'] = has_edit_access
        context['publish_workspaces'] = publish_workspaces
        context['publish_workspace_list'] = publish_workspace_list
    
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

        # START - To be improved later todo a reverse table join      
        ce_obj = catalogue_entries_models.CatalogueEntry.objects.all()
        pe_obj = publish_entries_models.PublishEntry.objects.all()

        for pe in pe_obj:            
            pe_list.append(pe.catalogue_entry.id)

        for ce in ce_obj:
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

        system_users_list = []
        system_users_obj = UserModel.objects.filter(is_active=True, groups__name=conf.settings.GROUP_ADMINISTRATOR_NAME)
        for su in system_users_obj:
             system_users_list.append({'first_name': su.first_name, 'last_name': su.last_name, 'id': su.id, 'email': su.email})
                
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

        # context['catalogue_entry_list'] = catalogue_entry_list
        context['catalogue_entry_obj'] = catalogue_entry_obj
        context['custodians_obj'] = custodians_obj
        context['system_users'] = system_users_list
        context['catalogue_entry_id'] = self.kwargs['pk']
        context['tab'] = self.kwargs['tab']
        context['symbology_definition'] = symbology_definition
        context['catalogue_layer_metadata'] = catalogue_layer_metadata
        context['has_edit_access'] = has_edit_access
        
    
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
        LayerSubscriptionStatus = catalogue_layer_subscription_models.LayerSubscriptionStatus;
        LayerSubscriptionType = catalogue_layer_subscription_models.LayerSubscriptionType;
        
        system_users_list = []
        system_users_obj = UserModel.objects.filter(is_active=True, groups__name=conf.settings.GROUP_ADMINISTRATOR_NAME)
        for su in system_users_obj:
            system_users_list.append({'first_name': su.first_name, 'last_name': su.last_name, 'id': su.id, 'email': su.email})
        has_edit_access = False
        if utils.is_administrator(request.user) is True and request.user == subscription_obj.assigned_to:
             if subscription_obj.status in (LayerSubscriptionStatus.DRAFT, LayerSubscriptionStatus.NEW_DRAFT, LayerSubscriptionStatus.PENDING):
                has_edit_access = True
        
        # mappings = list(catalogue_entries_models.CatalogueEntry.objects
        #                      .filter(layer_subscription=pk)
        #                      .values('id', 'mapping_name', 'layer_subscription', 'name', 'description'))
        # if not mappings:
        #     mappings = {}
        # else:
        #     mappings = {mapping['mapping_name']:{
        #                     'name':mapping['name'],
        #                     'description':mapping['description'],
        #                     'catalogue_entry_id':mapping['id']}
        #                 for mapping in mappings}
        
        def cache_or_call(url, key):
            mapping_names = cache.get(key)
            if not mapping_names:
                res = WebMapService(url=url)
                mapping_names = list(res.contents.keys())
                cache.set(key, mapping_names, conf.settings.SUBSCRIPTION_CACHE_TTL)
            return mapping_names
        
        def get_postgis_table_list():
            table_list = cache.get(conf.settings.POST_GIS_CACHE_KEY)
            if table_list:
                return table_list
            with connections['postgis'].cursor() as cursor:
                table_list = connections['postgis'].introspection.get_table_list(cursor)
            table_list = [table.name for table in table_list]
            cache.set(conf.settings.POST_GIS_CACHE_KEY, table_list, conf.settings.SUBSCRIPTION_CACHE_TTL)
            return table_list
    
        if subscription_obj.type == LayerSubscriptionType.WMS:
            mapping_names = cache_or_call(conf.settings.WMS_URL, conf.settings.WMS_CACHE_KEY)
        elif subscription_obj.type == LayerSubscriptionType.WFS:
            mapping_names = cache_or_call(conf.settings.WFS_URL, conf.settings.WFS_CACHE_KEY)
        elif subscription_obj.type == LayerSubscriptionType.POST_GIS:
            mapping_names = get_postgis_table_list()
        
        # Construct Context
        context: dict[str, Any] = {}
        context['subscription_obj'] = subscription_obj
        context['status'] = catalogue_utils.find_enum_by_value(LayerSubscriptionStatus, subscription_obj.status).name.replace('_', ' ')
        context['system_users'] = system_users_list
        context['is_system_user'] = utils.is_administrator(request.user)
        context['has_edit_access'] = has_edit_access
        context['type'] = catalogue_utils.find_enum_by_value(LayerSubscriptionType, subscription_obj.type).name.replace('_', ' ')
        context['workspaces'] = publish_workspaces_models.Workspace.objects.all()
        # context['enabled_js'] = "true" if subscription_obj.enabled else "false"
        context['mapping_names'] = json.dumps(mapping_names)
        # context['mapping_layers'] = json.dumps(["native layer name 03"])

        # Render Template and Return
        return shortcuts.render(request, self.template_name, context)        
    
    