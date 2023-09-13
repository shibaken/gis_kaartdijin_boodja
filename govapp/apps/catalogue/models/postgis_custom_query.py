"""Kaartdijin Boodja Catalogue Django Application Custodian Models."""


# Third-Party
from django.db import models
from django.core import validators
from django.core import exceptions
import reversion

# Local
from govapp.common import mixins
from govapp.apps.catalogue.models.catalogue_entries import CatalogueEntry

# Typing
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
    # from govapp.apps.catalogue.models.catalogue_entries import CatalogueEntry
    
class FrequencyType(models.IntegerChoices):
    """ Types of Frequency """
    EVERY_MINUTES = 1
    EVERY_HOURS = 2
    DAILY = 3
    WEEKLY = 4
    MONTHLY = 5
    
class FrequencyDaysOfWeek(models.IntegerChoices):
    """ Types of Frequency """
    MON = 1
    TUE = 2
    WED = 3
    THU = 4
    FRI = 5
    SAT = 6
    SUN = 7

@reversion.register()
class PostGisCustomQuery(mixins.RevisionedMixin):
    """Model for a PostGisCustomQuery."""
    catalogue_entry = models.OneToOneField(
        CatalogueEntry,
        related_name="custom_query",
        on_delete=models.CASCADE)
    sql_query = models.TextField()
    frequency_type = models.IntegerField(choices=FrequencyType.choices)
    
    # choices
    EVERY_MINUTES_CHOICES = ((i, f'Every {i} minutes') for i in (5, 10, 15, 20, 30))
    EVERY_HOURS_CHOICES = ((i, f'Every {i} hours') for i in (1, 2, 3, 6, 12))
    OCLOCK_CHOICES = ((i, f"0{i}:00" if i < 10 else f"{i}:00") for i in range(24))
    DATE_CHOICES = ((i, f"{i}") for i in range(1,29))

    # optionals
    frequency_every_minutes = models.PositiveSmallIntegerField(null=True, blank=True, choices=EVERY_MINUTES_CHOICES)
    frequency_every_hours = models.PositiveSmallIntegerField(null=True, blank=True, choices=EVERY_HOURS_CHOICES)
    frequency_oclock = models.SmallIntegerField(null=True, blank=True, choices=OCLOCK_CHOICES, 
                                                validators=[validators.MaxValueValidator(28), validators.MinValueValidator(0)])
    frequency_day_of_week = models.IntegerField(null=True, blank=True, choices=FrequencyDaysOfWeek.choices)
    frequency_date = models.PositiveSmallIntegerField(null=True, blank=True, choices=DATE_CHOICES)

    def clean(self):
        if (self.frequency_type == FrequencyType.EVERY_MINUTES and 
            self.frequency_every_minutes == None):
            raise exceptions.ValidationError(
                "If frequency_type is EVERY_MINUTES(1), "
                "frequency_every_minutes must be filled.")
        elif (self.frequency_type == FrequencyType.EVERY_HOURS and 
            self.frequency_every_hours == None):
            raise exceptions.ValidationError(
                "If frequency_type is EVERY_HOURS(2), "
                "frequency_every_hours must be filled.")
        elif (self.frequency_type == FrequencyType.DAILY and 
            self.frequency_oclock == None):
            raise exceptions.ValidationError(
                "If frequency_type is DAILY(3), "
                "frequency_oclock must be filled.")
        elif (self.frequency_type == FrequencyType.WEEKLY and 
            self.frequency_oclock == None and 
            self.frequency_day_of_week == None):
            raise exceptions.ValidationError(
                "If frequency_type is WEEKLY(4), "
                "frequency_oclock and frequency_day_of_week must be filled.")
        elif (self.frequency_type == FrequencyType.MONTHLY and 
            self.frequency_oclock == None and 
            self.frequency_date == None):
            raise exceptions.ValidationError(
                "If frequency_type is WEEKLY(4), "
                "frequency_oclock and frequency_day_of_week must be filled.")
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        """Custodian Model PostGisCustomQuery."""
        verbose_name = "PostGisCustomQuery"
        verbose_name_plural = "PostGisCustomQueries"

    def __str__(self) -> str:
        """Provides a string representation of the object.

        Returns:
            str: Human readable string representation of the object.
        """
        # Generate String and Return
        return f"{self.catalogue_entry.name}"
