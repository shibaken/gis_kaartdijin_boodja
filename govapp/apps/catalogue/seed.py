"""Kaartdijin Boodja Catalogue Django Application Data Seeding Functions."""


# Third-Party
from django import conf
from django.apps import registry
from django.db.backends.base import schema


def add_groups(
    apps: registry.Apps,
    schema_editor: schema.BaseDatabaseSchemaEditor,
) -> None:
    """Adds the required initial groups to the database.

    For more information on Data Migrations see:
    https://docs.djangoproject.com/en/3.2/topics/migrations/#data-migrations

    Args:
        apps (registry.Apps): Registry of Django apps
        schema_editor (schema.BaseDatabaseSchemaEditor): Database schema editor
    """
    # We have to retrieve the *current* model with the `apps` registry, in
    # case the Django Group model changes.
    Group = apps.get_model("auth", "Group")

    # Create Administrators Group
    # Group.objects.create(
    #     id=conf.settings.GROUP_ADMINISTRATOR_ID,
    #     name=conf.settings.GROUP_ADMINISTRATOR_NAME,
    # )

    # Create Catalogue Editors Group
    # Group.objects.create(
    #     id=conf.settings.GROUP_CATALOGUE_EDITOR_ID,
    #     name=conf.settings.GROUP_CATALOGUE_EDITOR_NAME,
    # )
