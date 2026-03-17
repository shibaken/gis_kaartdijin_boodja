"""URL configuration for the kb-geoserver-manager API."""

# Third-Party
from rest_framework import routers

# Local
from govapp.apps.publisher import views_geoserver_manager


router = routers.DefaultRouter()
router.register(
    "layers",
    views_geoserver_manager.GeoServerManagerViewSet,
    basename="geoserver-manager-layers",
)

urlpatterns = router.urls
