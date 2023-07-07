"""Django project views."""


# Third-Party
from django import http
from django import shortcuts
from django.views.generic import base
from django.contrib import auth
from django import conf


from govapp.apps.catalogue.models import catalogue_entries as catalogue_entries_models
from govapp.apps.publisher.models import publish_entries as publish_entries_models
from govapp.apps.catalogue.models import custodians as custodians_models
from govapp.apps.publisher.models import workspaces as publish_workspaces_models
from govapp.apps.catalogue.models import layer_symbology as catalogue_layer_symbology_models
from govapp.apps.catalogue.models import layer_metadata as catalogue_layer_metadata_models
from govapp.apps.catalogue.models import layer_submissions as catalogue_layer_submissions_models
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
    #     allow_access = False
    #     #if request.user.is_superuser:
    #     file_record = Record.objects.get(id=file_id)
    #     app_id = file_record.file_group_ref_id 
    #     app_group = file_record.file_group

    #     if (file_record.file_group > 0 and file_record.file_group < 12) or (file_record.file_group == 2003):
    #         app = Application.objects.get(id=app_id)
    #         if app.id == file_record.file_group_ref_id:
    #             flow = Flow()
    #             workflowtype = flow.getWorkFlowTypeFromApp(app)
    #             flow.get(workflowtype)

    #         flowcontext = {}
    #         if app.assignee:
    #             flowcontext['application_assignee_id']=app.assignee.id
    #         if app.submitted_by:
    #             flowcontext['application_submitter_id'] = app.submitted_by.id

    #         #flowcontext['application_owner'] = app.
    #         if app.applicant:
    #             if app.applicant.id == request.user.id:
    #                flowcontext['application_owner'] = True
    #         if request.user.is_authenticated:
    #             if Delegate.objects.filter(email_user=request.user).count() > 0:
    #                  flowcontext['application_owner'] = True


    #         flowcontext = flow.getAccessRights(request, flowcontext, app.routeid, workflowtype)
    #         if flowcontext['allow_access_attachments'] == "True":
    #             allow_access = True
    #         if allow_access is False:
    #             if request.user.is_authenticated:
    #                 refcount = Referral.objects.filter(application=app,referee=request.user).exclude(status=5).count()
    #                 if refcount > 0:
    #                    allow_access = True
    #                    ref = Referral.objects.filter(application=app,referee=request.user).exclude(status=5)[0]                  
    #                #for i in ref.records.all():
    #                #    if int(file_id) == i.id:
    #                #       allow_access = True

    #     if file_record.file_group == 2005:
    #         app = Approval.objects.get(id=app_id)
    #         if app.applicant:
    #             if app.applicant.id == request.user.id or request.user.is_staff is True:
    #                 allow_access = True
        
    #     if file_record.file_group == 2007:
    #         app = Approval.objects.get(id=app_id)
    #         if app.applicant:
    #             if request.user.is_staff is True:
    #                 allow_access = True

    #     if file_record.file_group == 2006:
    #         app = Compliance.objects.get(id=app_id)
    #         if app.applicant:
    #             if app.applicant.id == request.user.id or request.user.is_staff is True:
    #                 allow_access = True
    
    #     if allow_access == True:
    #         file_record = Record.objects.get(id=file_id)
    #         file_name_path = file_record.upload.path
    #         if os.path.isfile(file_name_path) is True:
    #             the_file = open(file_name_path, 'rb')
    #             the_data = the_file.read()
    #             the_file.close()
    #             if extension == 'msg': 
    #                 return HttpResponse(the_data, content_type="application/vnd.ms-outlook")
    #             if extension == 'eml':
    #                 return HttpResponse(the_data, content_type="application/vnd.ms-outlook")
    #             return HttpResponse(the_data, content_type=mimetypes.types_map['.'+str(extension)])
    #     else:
    #         return HttpResponse("Error loading attachment", content_type="plain/html")
    #     return
    

class LayerSubscriptions(base.TemplateView):
    """Layer Submissions view."""

    # Template name
    template_name = "govapp/layer_subscriptions.html"

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
        context['tab'] = 'layer_subscriptions'

        # Render Template and Return
        return shortcuts.render(request, self.template_name, context)        