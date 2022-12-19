"""Kaartdijin Boodja Logs Django Application URLs."""


# Third-Party
from rest_framework import routers

# Local
from . import views


# Router
router = routers.DefaultRouter()
router.register("communications", views.CommunicationsLogEntryViewSet)


# Logs URL Patterns
urlpatterns = router.urls
