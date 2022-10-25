"""govapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
#from django.urls import path
from django_media_serv.urls import urlpatterns as media_serv_patterns
from django.conf.urls import url, include
from govapp import views
from django.contrib.auth.views import LogoutView, LoginView
from django import urls
from django import conf
from django.conf import settings

# Admin Site Settings
admin.site.site_header = conf.settings.PROJECT_TITLE
admin.site.index_title = conf.settings.PROJECT_TITLE
admin.site.site_title = conf.settings.PROJECT_TITLE

urlpatterns = [
    urls.path('admin/', admin.site.urls),
    url(r'^$', views.HomePage.as_view(), name='home'),
    url(r'^test-contact', views.TestContactView.as_view(), name='test-contact'),
#    url(r'^test-vue', views.TestVueView.as_view(), name='test-vue'),
#    url(r'^test-map', views.TestMapView.as_view(), name='test-map'),

    # API Endpoints
    urls.path("api/accounts/", urls.include("govapp.apps.accounts.urls")),
    urls.path("api/docs/", urls.include("govapp.apps.swagger.urls")),
    urls.path("api/catalogue/", urls.include("govapp.apps.catalogue.urls")),
] + media_serv_patterns

urlpatterns.append(url(r'^logout/$', LogoutView.as_view(), {'next_page': '/'}, name='logout'))

if settings.ENABLE_DJANGO_LOGIN is True:
    urlpatterns.append(url(r'^ssologin/', LoginView.as_view(),name='ssologin'))
