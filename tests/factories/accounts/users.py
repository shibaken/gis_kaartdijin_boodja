"""Model Factories for the Accounts User Model."""


# Standard
import random

# Third-Party
from django.contrib import auth
from django.contrib.auth import models
import factory
import pytest_factoryboy

# Typing
from typing import Any, Iterable, Optional


# Shortcuts
UserModel = auth.get_user_model()
GroupModel = models.Group


@pytest_factoryboy.register
class UserFactory(factory.django.DjangoModelFactory):
    """Factory for a User."""
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = factory.LazyAttribute(lambda a: f"{a.first_name}.{a.last_name}".lower())
    password = factory.PostGenerationMethodCall("set_password", "")
    email = factory.LazyAttribute(lambda a: f"{a.username}@example.com".lower())
    is_staff = True
    is_superuser = False
    is_active = True

    class Meta:
        """User Factory Metadata."""
        model = UserModel

    @factory.post_generation  # type: ignore
    def groups(
        self,
        create: bool,
        extracted: Optional[Iterable[GroupModel]],
        **kwargs: Any,
    ) -> None:
        """Adds groups to the user.

        Args:
            create (bool): Whether the object is being created.
            extracted (Optional[Iterable[GroupModel]]): Extracted values.
            **kwargs (Any): Extra keyword arguments.
        """
        # Check if the object is being created
        if create:
            # Check if groups have been passed in
            # If groups have not been passed in, assign some random Groups
            groups = extracted or random.choices(  # noqa: S311
                population=GroupModel.objects.all(),
                k=GroupModel.objects.count(),
            )

            # Loop through groups
            for group in groups:
                # Add group
                self.groups.add(group)
