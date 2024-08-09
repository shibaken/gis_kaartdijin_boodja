"""Kaartdijin Boodja Catalogue Django Application Catalogue Entry Models."""

# Standard
import os
import reversion
from datetime import datetime 

# Third-Party
from django.contrib import auth
from django.contrib.auth import models as auth_models
from django.db import models
from rest_framework import request


# Local
from govapp.common import mixins
from govapp.apps.accounts import utils as accounts_utils
from govapp.apps.catalogue import notifications as notifications_utils
from govapp.apps.catalogue import utils
from govapp.apps.catalogue.models import custodians


# Typing
from typing import Optional, Union, TYPE_CHECKING


# Type Checking
if TYPE_CHECKING:
    from govapp.apps.catalogue.models import layer_attributes
    from govapp.apps.catalogue.models import layer_metadata
    from govapp.apps.catalogue.models import layer_submissions
    from govapp.apps.catalogue.models import layer_symbology
    from govapp.apps.catalogue.models import notifications
    from govapp.apps.publisher.models import publish_entries
    from govapp.apps.publisher.models import geoserver_queues
    from govapp.apps.catalogue.models import permission
    from govapp.apps.catalogue.models.layer_subscriptions import LayerSubscription


# Shortcuts
UserModel = auth.get_user_model()


class CatalogueEntryPermissionType(models.IntegerChoices):
    PUBLIC = 1, 'Public'
    RESTRICTED = 2, 'Restricted'

    @staticmethod
    def get_choices_dict():
        return {choice.value: choice.label for choice in CatalogueEntryPermissionType}


class CatalogueEntryStatus(models.IntegerChoices):
    """Enumeration for a Catalogue Entry Status."""
    NEW_DRAFT = 1
    LOCKED = 2
    DECLINED = 3
    DRAFT = 4
    PENDING = 5
    
class CatalogueEntryType(models.IntegerChoices):
    """Enumeration for a Catalogue Entry Status."""
    SPATIAL_FILE = 1
    SUBSCRIPTION_WFS = 2
    SUBSCRIPTION_WMS = 3
    SUBSCRIPTION_POSTGIS = 4
    SUBSCRIPTION_QUERY = 5

    @classmethod
    def get_as_string(cls, num):
        if num == cls.SPATIAL_FILE:
            return 'Spatial file'
        elif num == cls.SUBSCRIPTION_WFS:
            return 'Subscription WFS'
        elif num == cls.SUBSCRIPTION_WMS:
            return 'Subscription WMS'
        elif num == cls.SUBSCRIPTION_POSTGIS:
            return 'Subscription Postgis'
        elif num == cls.SUBSCRIPTION_QUERY:
            return 'Subscription Query'
        else:
            return ''
    
CATALOGUE_ENTRY_TYPES_ALLOWED_FOR_CDDP = [
    CatalogueEntryType.SPATIAL_FILE,
    CatalogueEntryType.SUBSCRIPTION_QUERY,
]

CATALOGUE_ENTRY_TYPES_ALLOWED_FOR_FTP = [
    CatalogueEntryType.SPATIAL_FILE,
    CatalogueEntryType.SUBSCRIPTION_QUERY,
]


@reversion.register(
    follow=(
        "attributes",
        "metadata",
        "layers",
        "symbology",
        "email_notifications",
        "webhook_notifications",
        "publish_entry",
        "catalouge_permissions",
    )
)
class CatalogueEntry(mixins.RevisionedMixin):
    """Model for a Catalogue Entry."""
    name = models.TextField()
    description = models.TextField(blank=True)
    status = models.IntegerField(choices=CatalogueEntryStatus.choices, default=CatalogueEntryStatus.NEW_DRAFT)
    type = models.IntegerField(choices=CatalogueEntryType.choices, default=CatalogueEntryType.SPATIAL_FILE)
    mapping_name = models.CharField(max_length=1000, null=True)
    sql_query = models.TextField(null=True, blank=True)
    layer_subscription = models.ForeignKey(
        "LayerSubscription",
        null=True,
        related_name="catalogue_entries",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    custodian = models.ForeignKey(
        custodians.Custodian,
        default=None,
        blank=True,
        null=True,
        related_name="custody",
        on_delete=models.SET_NULL,
    )
    assigned_to = models.ForeignKey(
        UserModel,
        default=None,
        blank=True,
        null=True,
        related_name="assigned",
        on_delete=models.SET_NULL,
    )
    permission_type = models.IntegerField(choices=CatalogueEntryPermissionType.choices, default=CatalogueEntryPermissionType.PUBLIC)
    force_run_postgres_scanner = models.BooleanField(default=False)

    # Type Hints for Reverse Relations
    # These aren't exactly right, but are useful for catching simple mistakes.
    attributes: "models.Manager[layer_attributes.LayerAttribute]"
    layers: "models.Manager[layer_submissions.LayerSubmission]"
    metadata: "layer_metadata.LayerMetadata"
    symbology: "layer_symbology.LayerSymbology"
    email_notifications: "models.Manager[notifications.EmailNotification]"
    webhook_notifications: "models.Manager[notifications.WebhookNotification]"
    publish_entry: "Optional[publish_entries.PublishEntry]"
    catalouge_permissions: "models.Manager[permission.CatalogueEntryPermission]"

    class Meta:
        """Catalogue Entry Model Metadata."""
        verbose_name = "Catalogue Entry"
        verbose_name_plural = "Catalogue Entries"
        constraints = [
            models.UniqueConstraint(fields=['mapping_name', 'layer_subscription'], name='unique_mapping_subscription')
        ]

    def __str__(self) -> str:
        """Provides a string representation of the object.

        Returns:
            str: Human readable string representation of the object.
        """
        # Generate String and Return
        return f"{self.name}"

    @property
    def file_extension(self):
        from govapp.apps.catalogue.models.layer_submissions import LayerSubmission
        latest_submission = LayerSubmission.objects.filter(catalogue_entry=self).last()
        return os.path.splitext(latest_submission.file)[-1] if latest_submission else ''

    @property
    def active_layer(self) -> "layer_submissions.LayerSubmission":
        """Retrieves the currently active layer.

        Returns:
            layer_submissions.LayerSubmission: The currently active layer.
        """
        # Retrieve Active Layer
        active_layer = self.layers.filter(is_active=True).order_by('id').last()

        # Check only when the type is CatalogueEntryType.SPATIAL_FILE
        #if CatalogueEntryType.SPATIAL_FILE == self.type:
        #    assert active_layer is not None, f"{repr(self)} has no active layer"  # noqa: S101

        # Return
        return active_layer
    
    @property
    def editors(self) -> "auth_models.User":
        """Retrieves permissioned users of current catalogue entry

        Returns:
            [auth_models.User] : a list of users
        """
        return self.catalouge_permissions.all()
        # permissions= list(self.catalouge_permissions.all())
        # obj = types.SimpleNamespace()
        # obj.all = lambda : permissions

        # return obj

    @classmethod
    def from_request(cls, request: request.Request) -> Optional["CatalogueEntry"]:
        """Retrieves a possible Catalogue Entry from request data.

        Args:
            request (request.Request): Request to retrieve Catalogue Entry from.

        Returns:
            Optional[models.catalogue_entries.CatalogueEntry]: Catalogue Entry.
        """
        # Retrieve Possible Catalogue Entry and Return
        return cls.objects.filter(
            id=request.data.get("catalogue_entry", -1),  # -1 Sentinel Value for Non-Existent Catalogue Entry
        ).first()

    def is_locked(self) -> bool:
        """Determines whether the Catalogue Entry is locked.

        Returns:
            bool: Whether the Catalogue Entry is locked.
        """
        # Check and Return
        return self.status == CatalogueEntryStatus.LOCKED

    def is_pending(self) -> bool:
        """Determines whether the Catalogue Entry is locked (pending).

        Returns:
            bool: Whether the Catalogue Entry is locked (pending).
        """
        # Check and Return
        return self.status == CatalogueEntryStatus.PENDING

    def is_declined(self) -> bool:
        """Determines whether the Catalogue Entry is declined.

        Returns:
            bool: Whether the Catalogue Entry is declined.
        """
        # Check and Return
        return self.status == CatalogueEntryStatus.DECLINED

    def is_unlocked(self) -> bool:
        """Determines whether the Catalogue Entry is unlocked.

        Returns:
            bool: Whether the Catalogue Entry is unlocked.
        """
        # Check and Return
        return self.status in (CatalogueEntryStatus.DRAFT, CatalogueEntryStatus.NEW_DRAFT, CatalogueEntryStatus.PENDING)

    def is_new(self) -> bool:
        """Determines whether the Catalogue Entry is a new draft.

        Returns:
            bool: Whether the Catalogue Entry is a new draft.
        """
        # Check and Return
        return self.status == CatalogueEntryStatus.NEW_DRAFT

    def is_editor(self, user: Union[auth_models.User, auth_models.AnonymousUser]) -> bool:
        """Checks whether the user is one of this Catalogue Entry's editors.

        Args:
            user (Union[models.User, models.AnonymousUser]): User to be checked

        Returns:
            bool: Whether the user is one of this CataloguE entry's editors.
        """
        # Check and Return
        return self.editors.all().filter(user=user).exists()

    def lock(self) -> bool:
        """Locks the Catalogue Entry.

        Returns:
            bool: Whether the locking was successful.
        """
        lock_success = False
        # Check Catalogue Entry
        if self.is_unlocked():
            # Check if Catalogue Entry is new
            if self.is_new():
                # Lock the currently active layer
                self.active_layer.accept()

            # Calculate the attributes hash
            attributes_hash = utils.attributes_hash(self.attributes.all())

            # Compare attributes hash with current active layer submission
            if self.active_layer.hash == attributes_hash:
                # Set Catalogue Entry to Locked
                self.status = CatalogueEntryStatus.LOCKED
                lock_success = True
            else:
                # Set Catalogue Entry to Pending
                self.status = CatalogueEntryStatus.PENDING
                lock_success = False

            # Check for Publish Entry
            if hasattr(self, "publish_entry"):
                # Publish Symbology
                self.publish_entry.publish(symbology_only=True)  # type: ignore[union-attr]

            # Save the Catalogue Entry
            self.save()

            # Send Emails
            notifications_utils.catalogue_entry_lock(self)

            print ("TRYING TO LOCK")
            print (lock_success)
            # Success!
            return lock_success
    
        # Failed
        return lock_success

    def unlock(self) -> bool:
        """Unlocks the Catalogue Entry.

        Returns:
            bool: Whether unlocking was successful.
        """
        # Check Catalogue Entry
        if self.is_locked() or self.is_pending():
            # Set Catalogue Entry to Draft
            self.status = CatalogueEntryStatus.DRAFT
            self.save()

            # Success!
            return True

        # Failed
        return False

    def decline(self) -> bool:
        """Declines the Catalogue Entry.

        Returns:
            bool: Whether the declining was successful.
        """
        # Check Catalogue Entry
        if self.is_unlocked():
            # Check if Catalogue Entry is new
            if self.is_new():
                # Decline the currently active layer
                self.active_layer.decline()

            # Set Catalogue Entry to Declined
            self.status = CatalogueEntryStatus.DECLINED
            self.save()

            # Success!
            return True

        # Failed
        return False

    def assign(self, user: auth_models.User) -> bool:
        """Assigns a user to the Catalogue Entry if applicable.

        Args:
            user (auth_models.User): User to be assigned.

        Returns:
            bool: Whether the assigning was successful.
        """
        # Check if the user can be assigned
        # To be assigned, a user must be:
        # 1. In the Catalogue Editors group
        # 2. One of this Catalogue Entry's editors
        #if accounts_utils.is_catalogue_editor(user) and self.is_editor(user):
        if self.is_editor(user):
            self.assigned_to = user
            self.save()   
            # Success!
            return True         
        if accounts_utils.is_administrator(user):
            # Assign user
            self.assigned_to = user
            self.save()

            # Success!
            return True

        # Failed
        return False

    def unassign(self) -> bool:
        """Unassigns the Catalogue Entry's user if applicable.

        Returns:
            bool: Whether the unassigning was successful.
        """
        # Check if there is an assigned user
        if self.assigned_to is not None:
            # Unassign
            self.assigned_to = None
            self.save()

            # Success!
            return True

        # Failed
        return False



    def save(self, *args, **kwargs):
        print ("HERE")
        super(CatalogueEntry, self).save(*args, **kwargs)
        
        from govapp.apps.catalogue.models import layer_metadata
        if self.type == 5:
           lm = layer_metadata.LayerMetadata.objects.filter(catalogue_entry=self)
           if lm.count() > 0:
               pass
           else:
               layer_metadata.LayerMetadata.objects.create(catalogue_entry=self,created_at=datetime.now())
