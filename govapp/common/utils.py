"""Kaartdijin Boodja Django Application Utility Functions."""

import re
import string
import random

# Third-Party
from functools import wraps
from django.db import models
from django.forms import ValidationError
from rest_framework import status

# Typing
from typing import Any, Optional

import httpx

def remove_html_tags(text):
    clean_text = re.sub('<style.*?</style>', '', clean_text)
    clean_text = re.sub('<.*?>', '', text)
    return clean_text


def filtered_manager(**kwargs: Any) -> models.manager.BaseManager:
    """Generates a Model Manager with the supplied filters applied.

    Args:
        **kwargs (Any): Filters to apply to the queryset.

    Returns:
        models.manager.BaseManager: Generated Filtered Manager.
    """
    # Construct Class
    class Manager(models.Manager):
        def get_queryset(self) -> models.QuerySet:
            return super().get_queryset().filter(**kwargs)

    # Return Manager
    return Manager()


def string_to_boolean(value: Optional[str]) -> bool:
    """Coerces a string value to a boolean.

    Returns:
        bool: The coerced boolean value.
    """
    # Parse and Return
    return True if value and value.lower() == "true" else False


class UserGroupServiceNotFoundError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.status_code = status.HTTP_404_NOT_FOUND


def handle_http_exceptions(logger):
    """Decorator factory to handle HTTP exceptions and log them with the given logger."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except httpx.HTTPStatusError as e:
                logger.error(f'HTTP status error in {func.__name__}: {e.response.status_code} {(e.response.text)}')
                # Handle specific cases based on status code or message
                if e.response.status_code == 404 and 'group service does not exist' in e.response.text:
                    # Handle 404 Not Found
                    logger.error("UserGroup service name does not exist.")
                    # Return custom response or re-raise with custom exception
                    raise UserGroupServiceNotFoundError("UserGroup service name not found.")
                raise
            except httpx.RequestError as exc:
                logger.error(f"An error occurred while requesting {exc.request.url!r}: {(exc)}")
                raise
        return wrapper
    return decorator


def calculate_dict_differences(new_rules, existing_rules):
    """
    Calculate items that are common to both dictionaries (with the same values)
    and items that are only contained in one of the dictionaries.

    :param dict1: First dictionary
    :param dict2: Second dictionary
    :return: Tuple of three dictionaries: common_items, dict1_only_items, dict2_only_items
    """
    
    # Calculate common keys between both dictionaries
    common_keys = set(new_rules.keys()) & set(existing_rules.keys())

    # We want to overwrite the common key values by new rules
    items_to_update = {key: new_rules[key] for key in common_keys}

    # Calculate items present only in dict1
    items_to_create = {key: new_rules[key] for key in set(new_rules.keys()) - set(existing_rules.keys())}

    # Calculate items present only in dict2
    items_to_delete = {key: existing_rules[key] for key in set(existing_rules.keys()) - set(new_rules.keys())}

    return items_to_update, items_to_create, items_to_delete

def generate_random_password(self):
    """Generate a secure random password."""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(12))
