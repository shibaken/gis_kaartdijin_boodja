"""GeoServer Abstractions."""


# Standard
import pathlib

# Third-Party
import httpx


class GeoServer:
    """GeoServer Abstraction."""

    def __init__(
        self,
        service_url: str,
        username: str,
        password: str,
        workspace: str = "default"
    ) -> None:
        """Instantiates the GeoServer Abstraction.

        Args:
            service_url (str): URL to the GeoServer service.
            username (str): Username for the GeoServer service.
            password (str): Password for the GeoServer service.
            workspace (str): Workspace to upload files to.
        """
        # Instance Attributes
        self.service_url = service_url.rstrip("/")  # Strip trailing slash
        self.username = username
        self.password = password
        self.workspace = workspace

    def upload_geopackage(self, filepath: pathlib.Path) -> None:
        """Uploads a Geopackage file to the GeoServer.

        Args:
            filepath (pathlib.Path): Path to the Geopackage file to upload.
        """
        # Construct URL
        url = "{0}/rest/workspaces/{1}/datastores/{2}/file.gpkg?filename={3}&update=overwrite".format(
            self.service_url,
            self.workspace,
            filepath.stem,
            filepath.name,
        )

        # Perform Request
        response = httpx.put(
            url=url,
            content=filepath.read_bytes(),
            headers={"Accept": "application/json"},
            auth=(self.username, self.password),
        )

        # Check Response
        response.raise_for_status()
