"""Azure Storage Service."""


# Third-Party
from azure.storage import blob
from django import conf


class AzureStorage:
    """Azure Storage Service."""

    def __init__(
        self,
        connection_string: str,
        container: str,
    ) -> None:
        """Instantiates the Azure Storage.

        Args:
            connection_string (str): Connection string for the Azure storage.
            container (str): Root container for the Azure storage.
        """
        # Instance Variables
        self.connection_string = connection_string
        self.container = container

        # Azure Connection
        self.service_client: blob.BlobServiceClient = blob.BlobServiceClient.from_connection_string(
            conn_str=self.connection_string,
        )
        self.container_client = self.service_client.get_container_client(  # type: ignore[attr-defined]
            container=self.container,
        )

    def put(self, path: str, contents: bytes) -> str:
        """Puts a file into the Azure Storage.

        Args:
            path (str): Path to put the file.
            contents (bytes): Contents of the file.

        Returns:
            str: URL path to the uploaded file.
        """
        # Upload File
        result = self.container_client.upload_blob(
            name=path,
            data=contents,
        )

        # Return
        return result.url  # type: ignore[no-any-return]


def azure_output() -> AzureStorage:
    """Helper constructor to instantiate AzureStorage (output).

    Returns:
        AzureStorage: Configured AzureStorage instance.
    """
    # Construct and Return
    return AzureStorage(
        connection_string=conf.settings.AZURE_OUTPUT_CONNECTION_STRING,
        container=conf.settings.AZURE_OUTPUT_CONTAINER,
    )
