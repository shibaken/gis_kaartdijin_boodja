"""Base class for a storage service."""


# Standard
import abc
import pathlib


class StorageService(abc.ABC):
    """Storage Service Protocol."""

    @abc.abstractmethod
    def list(self, path: str) -> list[str]:  # noqa: A003
        """Lists contents of a storage location.

        Args:
            path (str): The location to list contents.

        Returns:
            list[str]: Contents under the specified path.
        """
        # Must be implemented on subclasses
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, path: str) -> pathlib.Path:
        """Retrieves file contents from a storage location.

        Args:
            path (str): The location of the file to be retrieved

        Returns:
            pathlib.Path: The retrieved file in a temporary directory.
        """
        # Must be implemented on subclasses
        raise NotImplementedError

    @abc.abstractmethod
    def put(self, path: str, contents: bytes) -> str:
        """Stores a file in a storage location.

        Args:
            path (str): The location of the file to be stored.
            contents (bytes): The content of the file to be stored.

        Returns:
            str: URL path to the uploaded file.
        """
        # Must be implemented on subclasses
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, path: str) -> None:
        """Deletes a file from a storage location.

        Args:
            path (str): The location of the file to be deleted.
        """
        # Must be implemented on subclasses
        raise NotImplementedError
