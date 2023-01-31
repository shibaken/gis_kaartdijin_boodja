"""Kaartdijin Boodja Publisher Django Application URLs."""


# Third-Party
from rest_framework import routers

# Local
from govapp.apps.publisher import views


# Router
router = routers.DefaultRouter()
router.register("entries", views.PublishEntryViewSet)
router.register("channels/cddp", views.CDDPPublishChannelViewSet)
router.register("channels/geoserver", views.GeoServerPublishChannelViewSet)


# Catalogue URL Patterns
urlpatterns = router.urls
