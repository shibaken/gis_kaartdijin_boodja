"""Sharepoint Storage Service."""


# Standard
import os
import pathlib
import tempfile
import urllib.parse

# Third-Party
from django import conf
import shareplum

# Typing
from typing import Optional


class SharepointStorage:
    """Sharepoint Storage Service."""

    def __init__(
        self,
        url: Optional[str] = None,
        root: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """Instantiates the Sharepoint Storage.

        Args:
            url (Optional[str]): URL for the Sharepoint storage.
            root (Optional[str]): Root list for the Sharepoint storage.
            username (Optional[str]): Username for the Sharepoint storage.
            password (Optional[str]): Password for the Sharepoint storage.
        """
        # Instance Variables
        self.temp = tempfile.mkdtemp()
        self.url = url or conf.settings.SHAREPOINT_URL
        self.root = root or conf.settings.SHAREPOINT_LIST
        self.username = username or conf.settings.SHAREPOINT_USERNAME
        self.password = password or conf.settings.SHAREPOINT_PASSWORD

        # Sharepoint Connection
        auth_url = urllib.parse.urljoin(self.url, "/")  # Retrieves root URL of Sharepoint site
        auth = shareplum.Office365(auth_url, self.username, self.password)
        self.site = shareplum.Site(self.url, authcookie=auth.get_cookies(), version=shareplum.site.Version.v365)

    def list(self, path: str) -> list[str]:  # noqa: A003
        """Lists all files at the given path.

        Args:
            path (str): Relative path to list files for.

        Returns:
            list[str]: List of file paths found
        """
        # Construct Relative Path
        relative_path = os.path.join(self.root, path)

        # Retrieve Files
        raw_files = self.site.Folder(relative_path).files

        # Construct List
        files = [os.path.join(path, f["Name"]) for f in raw_files]

        # Return
        return files

    def get(self, path: str) -> pathlib.Path:
        """Retrieves a file at the given path.

        Args:
            path (str): Relative path to retrieve file for.

        Returns:
            pathlib.Path: Retrieved file contents as a temporary file.
        """
        # Get Relative Path
        relative_path = os.path.dirname(os.path.join(self.root, path))
        filename = os.path.basename(path)

        # Get File
        file: bytes = self.site.Folder(relative_path).get_file(filename)

        # Write File
        temp_file = pathlib.Path(self.temp) / pathlib.Path(path).name
        temp_file.write_bytes(file)

        # Return
        return temp_file

    def get_from_url(self, url: str) -> pathlib.Path:
        """Retrieves a file given a Sharepoint URL.

        Args:
            url (str): URL to the file to be downloaded.

        Returns:
            pathlib.Path: Retrieved file contents as a temporary file.
        """
        # Just parse the filepath relative to the root
        # Strip the leading slash if applicable
        path = url.split(self.root, 1)[-1]
        path = path.lstrip("/")

        # Get and Return
        return self.get(path)

    def put(self, path: str, contents: bytes) -> str:
        """Puts a file into the Sharepoint Storage.

        Args:
            path (str): Path to put the file.
            contents (bytes): Contents of the file.

        Returns:
            str: URL path to the uploaded file.
        """
        # Get Relative Path
        relative_path = os.path.dirname(os.path.join(self.root, path))
        filename = os.path.basename(path)

        # Upload File
        self.site.Folder(relative_path).upload_file(contents, filename)

        # Return
        return os.path.join(self.url, self.root, path)

    def delete(self, path: str) -> None:
        """Deletes a file from the Sharepoint Storage.

        Args:
            path (str): Path of the file to delete.
        """
        # Get Relative Path
        relative_path = os.path.dirname(os.path.join(self.root, path))
        filename = os.path.basename(path)

        # Delete File
        self.site.Folder(relative_path).delete_file(filename)
