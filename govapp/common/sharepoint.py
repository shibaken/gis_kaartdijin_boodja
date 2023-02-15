"""Sharepoint Storage Service."""


# Standard
import os
import pathlib
import tempfile
import urllib.parse

# Third-Party
from django import conf
import shareplum


class SharepointStorage:
    """Sharepoint Storage Service."""

    def __init__(
        self,
        url: str,
        root: str,
        username: str,
        password: str,
    ) -> None:
        """Instantiates the Sharepoint Storage.

        Args:
            url (str): URL for the Sharepoint storage.
            root (str): Root list for the Sharepoint storage.
            username (str): Username for the Sharepoint storage.
            password (str): Password for the Sharepoint storage.
        """
        # Instance Variables
        self.temp = tempfile.mkdtemp()
        self.url = url
        self.root = root
        self.username = username
        self.password = password

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

        # Recursively create directories if they don't exist
        # The Sharepoint API can only create a directory one level deep if it
        # doesn't already exist. However, the interface here presents no
        # restrictions on the depth of the filepath to push. As such, we need
        # to manually ensure each directory already exists by creating them.
        # For example, given the relative path:
        #   - "a/b/c/d"
        # The following code will create the directories in order:
        #   - "a"
        #   - "a/b"
        #   - "a/b/c"
        #   - "a/b/c/d"
        for directory in reversed(pathlib.Path(relative_path).parents[:-1]):
            self.site.Folder(str(directory))

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


def sharepoint_input() -> SharepointStorage:
    """Helper constructor to instantiate SharepointStorage (input).

    Returns:
        SharepointStorage: Configured SharepointStorage instance.
    """
    # Construct and Return
    return SharepointStorage(
        url=conf.settings.SHAREPOINT_INPUT_URL,
        root=conf.settings.SHAREPOINT_INPUT_LIST,
        username=conf.settings.SHAREPOINT_INPUT_USERNAME,
        password=conf.settings.SHAREPOINT_INPUT_PASSWORD,
    )


def sharepoint_output() -> SharepointStorage:
    """Helper constructor to instantiate SharepointStorage (output).

    Returns:
        SharepointStorage: Configured SharepointStorage instance.
    """
    # Construct and Return
    return SharepointStorage(
        url=conf.settings.SHAREPOINT_OUTPUT_URL,
        root=conf.settings.SHAREPOINT_OUTPUT_LIST,
        username=conf.settings.SHAREPOINT_OUTPUT_USERNAME,
        password=conf.settings.SHAREPOINT_OUTPUT_PASSWORD,
    )
