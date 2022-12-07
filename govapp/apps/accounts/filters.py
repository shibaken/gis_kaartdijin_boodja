"""Kaartdijin Boodja Accounts Django Application Filters."""


# Third-Party
from django_filters import rest_framework as filters
from django.contrib import auth


# Shortcuts
UserModel = auth.get_user_model()


class UserFilter(filters.FilterSet):
    """User Filter."""
    order_by = filters.OrderingFilter(fields=("id", "username"))

    class Meta:
        """User Filter Metadata."""
        model = UserModel
        fields = {"id": ["in"], "username": ["in"]}
