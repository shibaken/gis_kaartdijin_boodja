"""Kaartdijin Boodja Catalogue Django Application URLs."""


# Third-Party
from rest_framework import routers

# Local
from . import views


# Router
router = routers.DefaultRouter()
router.register("entries", views.CatalogueEntryViewSet)
router.register("layers/attributes", views.LayerAttributeViewSet)
router.register("layers/metadata", views.LayerMetadataViewSet)
router.register("layers/submissions", views.LayerSubmissionViewSet)
router.register("layers/subscriptions", views.LayerSubscriptionViewSet)
router.register("layers/symbologies", views.LayerSymbologyViewSet)
router.register("notifications/emails", views.EmailNotificationViewSet)
router.register("notifications/webhooks", views.WebhookNotificationViewSet)


# Catalogue URL Patterns
urlpatterns = router.urls
