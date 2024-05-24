"""Kaartdijin Boodja Publisher Django Application URLs."""


# Third-Party
from rest_framework import routers
from django.urls import path

# Local
from govapp.apps.publisher import views


# Router
router = routers.DefaultRouter()
router.register("entries", views.PublishEntryViewSet)
router.register("channels/cddp", views.CDDPPublishChannelViewSet)
router.register("channels/ftp", views.FTPPublishChannelViewSet)
router.register("channels/ftp-server", views.FTPServerViewSet)
router.register("channels/geoserver", views.GeoServerPublishChannelViewSet)
router.register("notifications/emails", views.EmailNotificationViewSet)
router.register("workspaces", views.WorkspaceViewSet)
router.register("geoserverweb", views.GeoServerQueueViewSet)
router.register("cddp-contents", views.CDDPContentsViewSet, basename='cddp-contents')


# Catalogue URL Patterns
urlpatterns = router.urls
# urlpatterns.append(path('cddp-contents/<path:filepath>/', views.CDDPContentsViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}), name='cddpcontents-detail'))
