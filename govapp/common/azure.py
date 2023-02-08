"""Azure Storage Service."""


# Standard
import pathlib

# Third-Party
from django import conf


class AzureStorage:
    """Azure Storage Service."""

    def __init__(
        self,
        sync_directory: pathlib.Path,
    ) -> None:
        """Instantiates the Azure Storage.

        Args:
            sync_directory (pathlib.Path): Sync directory.
        """
        # Instance Variables
        self.sync_directory = sync_directory

    def put(self, path: str, contents: bytes) -> pathlib.Path:
        """Puts a file into the Azure Storage.

        Args:
            path (str): Path to put the file.
            contents (bytes): Contents of the file.

        Returns:
            pathlib.Path: Path to the written file.
        """
        # Construct Output Directory
        output_path = self.sync_directory / path
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write File
        output_path.write_bytes(contents)

        # Return
        return output_path


def azure_output() -> AzureStorage:
    """Helper constructor to instantiate AzureStorage (output).

    Returns:
        AzureStorage: Configured AzureStorage instance.
    """
    # Construct and Return
    return AzureStorage(
        sync_directory=pathlib.Path(conf.settings.AZURE_OUTPUT_SYNC_DIRECTORY),
    )
