# Kaartdijin Boodja - Backend Documentation
## Overview
The backend of Kaartdijin Boodja is a [Python](https://www.python.org/) [Django](https://www.djangoproject.com/) project
using [Django REST Framework](https://www.django-rest-framework.org/) backed by a [PostgreSQL](https://www.postgresql.org/)
database. The backend uses Poetry to manage its dependencies.

## Development
### Requirements
* [Python 3.10](https://www.python.org/downloads/release/python-3100/)
* [Pip](https://pypi.org/project/pip/)
* [Poetry 1.3.2](https://python-poetry.org/)
* [GDAL 3.6.2](https://gdal.org/download.html)

### Development Environment
To get a standard development environment up and running using Poetry and virtual environments:
```shell
# Ensure Poetry is installed
$ poetry --version
Poetry (version 1.3.2)

# Ensure Python 3.10 is currently activated
$ python3 --version
Python 3.10.4

# Create a virtual environment and install dependencies using Poetry
# The dependencies are installed from the `poetry.lock` file, providing
# consistent and reproducible installations across any machine.
$ poetry install

# Remember to enter the virtual environment shell after installation
$ poetry shell

# Check GDAL is installed correctly
$ gdal-config --version
3.6.2

# Install Python GDAL Manually
$ pip install gdal==`gdal-config --version`
```

### Linting
To run the linting process:
```shell
$ poetry shell
$ poe lint
```

### Type-Checking
To run the type-checking process:
```shell
$ poetry shell
$ poe type
```

### Unit-Testing
To run the unit tests:
```shell
$ poetry shell
$ poe test
```

### Development Server
To run a development server:
```shell
$ poetry shell
$ poe dev
```

### Management Commands
To run management commands (e.g, migrations):
```shell
$ poetry shell
$ poe manage migrate  # Run migrations
$ poe manage makemigrations catalogue publisher  # Create migrations
$ poe manage loaddata tests/fixtures/*/*.json  # Load json fixtures
...
```

## Configuration
The backend is configured in the `govapp/settings.py` file, see this for a full list of configuration values. The
following values are useful during development:
```shell
# Django
DEBUG=True  # <-- Enables debug mode in development
SECRET_KEY=django-insecure  # <-- Insecure key for development
DATABASE_URL=sqlite://./sqlite.db  # <-- Uses an on-disk sqlite database in development
ENABLE_DJANGO_LOGIN=True  # <-- Enables login screen for development, set to false in production
# Frontend Integration
DEV_APP_BUILD_URL="http://localhost:9072/src/main.ts"
# Email
DISABLE_EMAIL=True  # <-- Disables email in development
# Sharepoint
SHAREPOINT_INPUT_USERNAME="{SHAREPOINT_USERNAME}"
SHAREPOINT_INPUT_PASSWORD="{SHAREPOINT_PASSWORD}"
SHAREPOINT_OUTPUT_USERNAME="{SHAREPOINT_USERNAME}"
SHAREPOINT_OUTPUT_PASSWORD="{SHAREPOINT_PASSWORD}"
```
For convenience, these can also be defined in a `.env` file that will be loaded at runtime.

## Structure
The backend of the Kaartdijin Boodja project is structured as a regular `django` project using `django-rest-framework`.

An overview of the structure is shown below.
```shell
govapp
├── apps
│   ├── accounts
│   ├── catalogue
│   │   ├── management
│   │   │   └── commands
│   │   ├── migrations
│   │   ├── models
│   │   ├── serializers
│   │   └── templates
│   ├── emails
│   │   ├── management
│   │   │   └── commands
│   │   └── templates
│   ├── logs
│   │   └── migrations
│   ├── publisher
│   │   ├── migrations
│   │   ├── models
│   │   ├── serializers
│   │   └── templates
│   └── swagger
├── common
├── gis
│   └── readers
│       └── formats
├── templates
│   ├── govapp
│   ├── registration
│   └── webtemplate_dbca
│       └── includes
└── templatetags
```

Each of these directories is elaborated on below:
**`govapp`**
* The entire codebase is within the `govapp` directory
* This includes the backend and the frontend

**`govapp/apps`**
* Each of the separate `django` "apps" are separated within the `apps` directory
* For example, the `catalogue` and `publisher` apps

**`govapp/apps/accounts`**
* Provides REST API functionality for *users* and *groups*
* Provides utility functions for retrieving users in certain groups (e.g., Administrators)
* Provides utility classess for handling permissions on RESTAPI endpoints

**`govapp/apps/catalogue`**
* One of the main applications within the project
* Provides models, serializers, filters, permissions and REST API endpoints for interacting with the catalogue
* Provides cron jobs and functionality for scanning and absorbing GIS files from Sharepoint

**`govapp/apps/catalogue/management/commands`**
* Provides management commands for the `catalogue` app
* Provides the `absorb` app: `$ poe manage absorb <SHAREPOINT_FILEPATH>`
* Provides the `scan` app: `$ poe manage scan`

**`govapp/apps/catalogue/migrations`**
* Standard `django` migrations for the `catalogue` models

**`govapp/apps/catalogue/models`**
* Provides the models for the `catalogue` app
* Each model is defined within its own file for readability:
  - `catalogue_entries`
  - `custodians`
  - `layer_attributes`
  - `layer_metadata`
  - `layer_submissions`
  - `layer_subscriptions`
  - `layer_symbology`
  - `notifications`

**`govapp/apps/catalogue/serializers`**
* Provides the serializers for the models outlined above

**`govapp/apps/catalogue/templates`**
* Provides email templates for the `catalogue` email notifications

**`govapp/apps/emails`**
* Provides email functionality throughout the project

**`govapp/apps/emails/management/commands`**
* Provides management commands for the `emails` app
* Provides the `email` app: `$ poe manage email <TEST_EMAIL_RECIPIENT>`

**`govapp/apps/emails/templates`**
* Provides base templates for the email notifications

**`govapp/apps/logs`**
* Provides common logs functionality throughout the application
* Provides models, mixins and REST API endpoints for the `CommunicationsLogs` and `ActionsLogs`
* Both `CommunicationsLogs` and `ActionsLogs` are implemented with *Generic Foreign Keys*
* This means they can be foreign keyed to any other model without having to define a new table or copy-paste the models
* The mixins provided allow any model viewset in the application to automatically gain logs endpoints

**`govapp/apps/logs/migrations`**
* Standard `django` migrations for the `logs` models

**`govapp/apps/publisher`**
* One of the main applications within the project
* Provides models, serializers, filters, permissions and REST API endpoints for interacting with the publisher

**`govapp/apps/publisher/migrations`**
* Standard `django` migrations for the `publisher` models

**`govapp/apps/publisher/models`**
* Provides the models for the `publisher` app
* Each model is defined within its own file for readability:
  - `notifications`
  - `publish_channels`
  - `publish_entries`
  - `workspaces`

**`govapp/apps/publisher/serializers`**
* Provides the serializers for the models outlined above

**`govapp/apps/publisher/templates`**
* Provides email templates for the `publisher` email notifications

**`govapp/apps/swagger`**
* Provides automatic OpenAPI documentation and Swagger UI
* Go to `/api/docs` to see interactive fully documented REST API

**`govapp/common`**
* Provides common functionality among all of the applications
* For example:
  - Azure abstraction (now just moving files to a dircetory)
  - Sharepoint abstraction
  - Utility mixins (e.g., `django-reversion`, automatic choices API endpoints, multiple serializer endpoints)
  - Other common utility functions

**`govapp/gis`**
* Provides all GIS functionality, including interactions with `GDAL` and `ogr2ogr`
* Provides compression utilities (compressing and decompressing multi-file archives)
* Provides utlities to convert between GIS file types (e.g., `gpkg`, `shp`, `gdb`) using `ogr2ogr`
* Provides GeoServer API abstraction

**`govapp/gis/readers`**
* Provides base file reading functionality for GIS files
* Defines interface to read *attributes*, *metadata* and *symbology* from *ANY* GIS file type supported by GDAL
* This was adapted from `ogrinfo` source code
* See: https://github.com/OSGeo/gdal/blob/master/swig/python/gdal-utils/osgeo_utils/samples/ogrinfo.py

**`govapp/gis/readers/formats`**
* Provides format specific readers implementing the interface defined above
* Currently supported:
  - `geodatabase`
  - `geojson`
  - `geopackage`
  - `shapefile`

**`govapp/templates`**
* Part of the DBCA template

## Crons
The Cron jobs in this project are managed by `django-cron`. The `django-cron` settings can be found within the
`govapp/settings.py` file under the "# Cron Jobs" section. See below for a preview:
```python
# Cron Jobs
# https://django-cron.readthedocs.io/en/latest/installation.html
# https://django-cron.readthedocs.io/en/latest/configuration.html
CRON_SCANNER_CLASS = "govapp.apps.catalogue.cron.ScannerCronJob"
CRON_SCANNER_PERIOD_MINS = 5  # Run every 5 minutes
CRON_CLASSES = [
    CRON_SCANNER_CLASS,
]
```

### Scanner
The "scanner" Django cron is the process that scans the Sharepoint defined by `SHAREPOINT_INPUT_URL`, and subsequently
absorbs any GIS files that it finds. As above, this process runs every `CRON_SCANNER_PERIOD_MINS` (default 5 mins). This
cron job is defined at `govapp/apps/catalogue/cron.py` in the `ScannerCronJob` class, where it calls the "scan"
management command defined at `govapp/apps/catalogue/management/commands/scan.py`.

## Other Information
...
