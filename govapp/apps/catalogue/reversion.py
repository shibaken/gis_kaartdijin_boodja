"""Kaartdijin Boodja Catalogue Django Application Reversion Registry."""


# Third-Party
import reversion

# Local
from . import models


# Register Models with Reversion
reversion.register(
    model=models.catalogue_entries.CatalogueEntry,
    follow=(
        "custodian",
        "assigned_to",
        "attributes",
        "metadata",
        "layers",
        "symbology",
    ),
)
reversion.register(model=models.custodians.Custodian)
reversion.register(model=models.layer_attributes.LayerAttribute)
reversion.register(model=models.layer_metadata.LayerMetadata)
reversion.register(model=models.layer_submissions.LayerSubmission)
reversion.register(model=models.layer_subscriptions.LayerSubscription)
reversion.register(model=models.layer_symbology.LayerSymbology)
reversion.register(model=models.notifications.EmailNotification)
reversion.register(model=models.notifications.WebhookNotification)
