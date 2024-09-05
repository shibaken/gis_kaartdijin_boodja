"""Kaartdijin Boodja Catalogue Django Application URLs."""


# Third-Party
from rest_framework import routers

# Local
from govapp.apps.catalogue import views


# Router
router = routers.DefaultRouter()
router.register("custodians", views.CustodianViewSet)
router.register("entries", views.CatalogueEntryViewSet)
router.register("layers/attributes", views.LayerAttributeViewSet)
router.register("layers/attribute/type", views.LayerAttributeTypeViewSet)
router.register("layers/metadata", views.LayerMetadataViewSet)
router.register("layers/submissions", views.LayerSubmissionViewSet)
router.register("layers/submissions2", views.LayerSubmissionViewSet2, basename='layersubmission2')
router.register("layers/subscriptions", views.LayerSubscriptionViewSet)
router.register("layers/symbologies", views.LayerSymbologyViewSet)
router.register("notifications/emails", views.EmailNotificationViewSet)
router.register("notifications/webhooks", views.WebhookNotificationViewSet)
router.register("permission", views.CataloguePermissionViewSet)


# Catalogue URL Patterns
urlpatterns = router.urls
