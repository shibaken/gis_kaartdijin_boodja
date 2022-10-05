from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic.base import View, TemplateView
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from govapp import forms as app_forms
from django.contrib.auth.models import User
from django.views.generic.base import View, TemplateView
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView

class HomePage(TemplateView):

    template_name = 'govapp/home.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class TestVueView(TemplateView):

    template_name = 'govapp/test-vue.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)

class TestMapView(TemplateView):

    template_name = 'govapp/test-map.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)

class TestContactView(CreateView):
    template_name = 'govapp/test-contact.html'
    model = User 

    def get(self, request, *args, **kwargs):
        return super(TestContactView, self).get(request, *args, **kwargs)

    def get_form_class(self):
        return app_forms.TestContactForm

    def get_context_data(self, **kwargs):
        context = super(TestContactView, self).get_context_data(**kwargs)
        request = self.request
        # Add some data
        context['state'] = "WA"
        return context

    def get_initial(self):
        initial = super(TestContactView, self).get_initial()
        # set a default value
        initial['first_name'] = 'John'
        return initial

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            return HttpResponseRedirect(reverse('home'))
        return super(TestContactView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        forms_data = form.cleaned_data
        if forms_data['first_name'] == '':
              print ("ERROR")

        self.object.save()
        return HttpResponseRedirect("/")
