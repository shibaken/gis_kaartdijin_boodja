"""Provides utilities for unit testing."""


# Standard
import pathlib
import shutil
import tempfile


def test_file(file: str) -> pathlib.Path:
    """Retreives a test file from the `tests/data` directory.

    Args:
        file (str): Filename or path to find in the test data directory.

    Returns:
        pathlib.Path: Path to the retrieved file.
    """
    # Construct and Return
    return pathlib.Path(__file__).parent / "data" / file


def to_temporary_directory(filepath: pathlib.Path) -> pathlib.Path:
    """Copies the provided filepath to a temporary directory.

    Args:
        filepath (pathlib.Path): Filepath to be copied.

    Returns:
        pathlib.Path: Filepath of the copied file in a temporary directory.
    """
    # Create Temporary Directory
    temp = tempfile.mkdtemp()

    # Copy
    destination = shutil.copy(filepath, temp)

    # Return
    return pathlib.Path(destination)
