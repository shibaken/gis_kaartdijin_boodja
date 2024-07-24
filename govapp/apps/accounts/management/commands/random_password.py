from django.core.management.base import BaseCommand

from govapp import settings
from govapp.apps.publisher.models.geoserver_pools import GeoServerPool
from govapp.common.utils import generate_random_password



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
                new_password = generate_random_password(50)
                self.update_password(geoserver, user_name, new_password)

    def update_password(self, geoserver, user_name, new_password):
        """Update user password in GeoServer."""
        user_data = {
            "userName": user_name,
            "password": new_password,
            "enabled": True  # Ensure user is enabled
        }
        geoserver.update_existing_user(user_data)
