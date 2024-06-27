import random
import string
import httpx
import json
from django.core.management.base import BaseCommand

from govapp import settings
from govapp.apps.publisher.models.geoserver_pools import GeoServerPool



class Command(BaseCommand):
    help = 'Randomize passwords for all GeoServer user accounts.'

    def handle(self, *args, **options):
        geoservers = GeoServerPool.objects.filter(enabled=True)
        for geoserver in geoservers:
            self.randomize_passwords(geoserver)

    def randomize_passwords(self, geoserver):
        """Randomize passwords for all users in GeoServer."""
        users = geoserver.get_all_users()

        for user in users:
            user_name = user["userName"]
            if user_name not in settings.NON_DELETABLE_USERS:
                new_password = self.generate_random_password()
                self.update_password(geoserver, user_name, new_password)

    def generate_random_password(self):
        """Generate a secure random password."""
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for i in range(12))

    def update_password(self, geoserver, user_name, new_password):
        """Update user password in GeoServer."""
        user_data = {
            "userName": user_name,
            "password": new_password,
            "enabled": True  # Ensure user is enabled
        }
        geoserver.update_existing_user(user_data)
