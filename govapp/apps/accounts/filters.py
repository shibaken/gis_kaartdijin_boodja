"""Kaartdijin Boodja Accounts Django Application Filters."""

# Third-Party
from django_filters import rest_framework as filters
from django.contrib import auth

models = auth.models


class UserFilter(filters.FilterSet):
    """User Filter."""
    order_by = filters.OrderingFilter(fields=("id", "username"))

    class Meta:
        """User Filter Metadata."""
        model = models.User
        fields = {"id": ["in"], "username": ["in"]}
