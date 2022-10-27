"""Django unit test settings for the Kaartdijin Boodja project."""


# Third-Party
import dj_database_url

# Local
from govapp import settings
from govapp.settings import *  # noqa: F401,F403


# Override Settings
# When performing unit tests, just use an in-memory SQLite database.
DATABASES = {
    "default": dj_database_url.parse("sqlite://memory"),
}

# Fixtures Settings
# Discover fixture .json files in the fixtures directory for unit testing.
FIXTURES_DIR = settings.BASE_DIR / "tests/fixtures"
FIXTURES = list(FIXTURES_DIR.rglob("*.json"))
