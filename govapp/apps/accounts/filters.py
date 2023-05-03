"""Kaartdijin Boodja Accounts Django Application Filters."""


# Third-Party
from django_filters import rest_framework as filters
from django.contrib import auth
from django.db.models import Q

# Shortcuts
UserModel = auth.get_user_model()


class UserFilter(filters.FilterSet):
    """User Filter."""
    order_by = filters.OrderingFilter(fields=("id", "username"))    
    q = filters.CharFilter(method='account_search', label="Search Accounts")


    class Meta:
        """User Filter Metadata."""
        model = UserModel
        #fields = {"id": ["in"], "username": ["in"], "first_name": ["in"]}
        fields = ['q']


    def account_search(self, queryset, name, value):
        return queryset.filter(
            Q(id__icontains=value) |
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) | 
            Q(email__icontains=value)             
        )