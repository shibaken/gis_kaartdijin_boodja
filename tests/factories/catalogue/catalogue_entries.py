"""Model Factories for the Catalogue Catalogue Entry Model."""


# Standard
import random

# Third-Party
from django.contrib import auth
import factory
import factory.fuzzy

# Local
from govapp.apps.catalogue import models
from tests.factories import accounts
from tests.factories.catalogue import custodians
from tests.factories.catalogue import layer_attributes
from tests.factories.catalogue import layer_metadata
from tests.factories.catalogue import layer_submissions
from tests.factories.catalogue import layer_symbology
from tests.factories.catalogue import notifications
from tests.factories.catalogue import workspaces
from tests.factories.publisher import publish_entries

# Typing
from typing import Any


# Shortcuts
UserModel = auth.get_user_model()


class CatalogueEntryFactory(factory.django.DjangoModelFactory):
    """Factory for a Catalogue Entry."""
    name = factory.Sequence(lambda n: f"Catalogue Entry {n + 1}")
    description = factory.Faker("paragraph")
    status = factory.fuzzy.FuzzyChoice(models.catalogue_entries.CatalogueEntryStatus)
    custodian = factory.SubFactory(custodians.CustodianFactory)
    assigned_to = factory.SubFactory(accounts.users.UserFactory)
    workspace = factory.SubFactory(workspaces.WorkspaceFactory)

    attributes = factory.RelatedFactoryList(
        layer_attributes.LayerAttributeFactory,
        size=lambda: random.randint(1, 5),  # noqa: S311
        factory_related_name="catalogue_entry",
    )
    metadata = factory.RelatedFactory(
        layer_metadata.LayerMetadataFactory,
        factory_related_name="catalogue_entry",
    )
    symbology = factory.RelatedFactory(
        layer_symbology.LayerSymbologyFactory,
        factory_related_name="catalogue_entry",
    )
    email_notifications = factory.RelatedFactoryList(
        notifications.EmailNotificationFactory,
        size=lambda: random.randint(1, 5),  # noqa: S311
        factory_related_name="catalogue_entry",
    )
    webhook_notifications = factory.RelatedFactoryList(
        notifications.WebhookNotificationFactory,
        size=lambda: random.randint(1, 5),  # noqa: S311
        factory_related_name="catalogue_entry",
    )
    layers = factory.RelatedFactoryList(
        layer_submissions.LayerSubmissionFactory,
        size=lambda: random.randint(1, 5),  # noqa: S311
        factory_related_name="catalogue_entry",
    )
    publish_entry = factory.RelatedFactory(
        publish_entries.PublishEntryFactory,
        factory_related_name="catalogue_entry",
    )

    class Meta:
        """Catalogue Entry Factory Metadata."""
        model = models.catalogue_entries.CatalogueEntry

    @factory.post_generation  # type: ignore
    def set_active_layer(
        self,
        create: bool,
        extracted: Any,
        **kwargs: Any,
    ) -> None:
        """Sets active layer for the catalogue entry.

        Args:
            create (bool): Whether the object is being created.
            extracted (Optional[LayerSubmission]): Extracted value.
            **kwargs (Any): Extra keyword arguments.
        """
        # Check if the object is being created
        if create:
            # Set most recent layer to active
            last = self.layers.order_by("submitted_at").last()
            last.is_active = True
            last.save()
