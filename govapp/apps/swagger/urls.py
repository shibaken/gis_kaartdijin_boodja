"""Kaartdijin Boodja Swagger UI Django Application URLs."""


# Third-Party
from django import urls
from django.views import generic
from drf_spectacular import views


# Swagger URL Patterns
urlpatterns = [
    # Redirect Index to Swagger UI
    urls.path("", generic.RedirectView.as_view(url="swagger", permanent=True)),

    # Swagger URLs
    urls.path("schema/", views.SpectacularAPIView.as_view(), name="schema"),
    urls.path("swagger/", views.SpectacularSwaggerView.as_view(), name="swagger"),
    urls.path("redoc/", views.SpectacularRedocView.as_view(), name="redoc"),
]
