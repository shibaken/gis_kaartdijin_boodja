"""Kaartdijin Boodja Catalogue Django Application Custodian Models."""


# Third-Party
from django.db import models
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
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
class CustomQueryFrequency(mixins.RevisionedMixin):
    """Model for a PostGisCustomQuery."""
    catalogue_entry = models.ForeignKey(
        CatalogueEntry,
        related_name="custom_query_frequencies",
        on_delete=models.CASCADE)
    type = models.IntegerField(choices=FrequencyType.choices)

    # optionals
    every_minutes = models.PositiveSmallIntegerField(
        null=True, blank=True, 
        validators=[MinValueValidator(1), MaxValueValidator(60)])
    every_hours = models.PositiveSmallIntegerField(
        null=True, blank=True, 
        validators=[MinValueValidator(1), MaxValueValidator(24)])
    hour = models.SmallIntegerField(
        null=True, blank=True, 
        validators=[MinValueValidator(0), MaxValueValidator(23)])
    minute = models.SmallIntegerField(
        null=True, blank=True, 
        validators=[MinValueValidator(0), MaxValueValidator(59)])
    day_of_week = models.IntegerField(
        null=True, blank=True, 
        choices=FrequencyDaysOfWeek.choices)
    date = models.PositiveSmallIntegerField(
        null=True, blank=True, 
        validators=[MinValueValidator(1), MaxValueValidator(31)])

    def clean(self):
        if (self.type == FrequencyType.EVERY_MINUTES and 
            self.every_minutes == None):
            raise exceptions.ValidationError(
                "If type is EVERY_MINUTES(1), every_minutes must be filled.")
        elif (self.type == FrequencyType.EVERY_HOURS and 
            self.every_hours == None):
            raise exceptions.ValidationError(
                "If type is EVERY_HOURS(2), every_hours must be filled.")
        elif (self.type == FrequencyType.DAILY and 
            (self.hour == None or self.minute == None)):
            raise exceptions.ValidationError(
                "If type is DAILY(3), hour must be filled.")
        elif (self.type == FrequencyType.WEEKLY and 
            (self.hour == None or self.minute == None or self.day_of_week == None)):
            raise exceptions.ValidationError(
                "If type is WEEKLY(4), hour, minute and day_of_week must be filled.")
        elif (self.type == FrequencyType.MONTHLY and 
            (self.hour == None or self.minute == None or self.date == None)):
            raise exceptions.ValidationError(
                "If type is MONTHLY(5), hour, minute and date must be filled.")
        
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
