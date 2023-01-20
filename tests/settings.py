"""Django unit test settings for the Kaartdijin Boodja project."""


# Standard
import tempfile

# Third-Party
import dj_database_url

# Local
from govapp.settings import *  # noqa: F401,F403


# Override Settings
# When performing unit tests, just use an in-memory SQLite database.
DATABASES = {
    "default": dj_database_url.parse("sqlite://memory"),
}
# When performing unit tests, just output emails to the console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# When performing unit tests, set media root to a random temporary directory
MEDIA_ROOT = tempfile.mkdtemp()
