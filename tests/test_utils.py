import pytest
import tempfile
import os
from pathlib import Path
from typing import List
from Aider_Project.utils import list_files

'''
Proposed Unit Tests:

Test with a valid directory: Ensure the function correctly lists all files in a valid directory.
Test with an invalid directory: Verify that the function raises a ValueError when given an invalid directory.
Test with an empty directory: Check that the function returns an empty list when the directory is empty.
Test with nested directories: Ensure the function lists files from nested directories.
Test with the print_files flag: Verify that the function prints the files when the print_files flag is set to True.

Explanation:
==============
Fixtures:

temp_dir: Creates a temporary directory for testing.
nested_dir: Creates a nested directory structure within the temporary directory.
empty_dir: Creates an empty directory within the temporary directory.
Parameterization:

Tests are parameterized to run with both True and False values for the print_files_flag.

Tests:

test_list_files_valid_directory: Tests listing files in a valid directory.
test_list_files_invalid_directory: Tests raising a ValueError for an invalid directory.
test_list_files_empty_directory: Tests listing files in an empty directory.
test_list_files_nested_directory: Tests listing files in a nested directory.
test_list_files_with_print: Tests listing files with the print_files flag set to True.
test_list_files_nested_with_print: Tests listing files in a nested directory with the print_files flag set to True.
'''

@pytest.fixture
def temp_dir():
    """Fixture to create a temporary directory for testing."""
    # Create a temporary directory that exists only for the duration of the test
    with tempfile.TemporaryDirectory() as temp_dir:
        # Provide the path of the temporary directory to the test function
        yield temp_dir

# Define a fixture to create a nested directory structure within a temporary directory
@pytest.fixture
def nested_dir(temp_dir):
    # Create a new directory named 'nested' inside the temporary directory
    nested_dir_path = Path(temp_dir) / 'nested'
    nested_dir_path.mkdir()  # Make the 'nested' directory
    # Create two empty files, 'file1.txt' and 'file2.txt', inside the 'nested' directory
    (nested_dir_path / 'file1.txt').touch()
    (nested_dir_path / 'file2.txt').touch()
    # Provide the path to the 'nested' directory to the test function
    yield nested_dir_path

# Define a fixture to create an empty directory within a temporary directory
@pytest.fixture
def empty_dir(temp_dir):
    # Create a new directory named 'empty' inside the temporary directory
    empty_dir_path = Path(temp_dir) / 'empty'
    empty_dir_path.mkdir()  # Make the 'empty' directory
    # Provide the path to the 'empty' directory to the test function
    yield empty_dir_path

# Define a test function that runs with both True and False values for print_files_flag
@pytest.mark.parametrize("print_files_flag", [False, True])
def test_list_files_valid_directory(temp_dir, print_files_flag):
    """Test listing files in a valid directory with and without printing."""
    # Create two empty files, 'file1.txt' and 'file2.txt', in the temporary directory
    file1 = Path(temp_dir) / 'file1.txt'
    file2 = Path(temp_dir) / 'file2.txt'
    file1.touch()  # Create 'file1.txt'
    file2.touch()  # Create 'file2.txt'

    # Define the expected list of file names
    expected_files = ['file1.txt', 'file2.txt']
    # Call the function under test, passing in the temporary directory and the print flag
    result = list_files(temp_dir, print_files_flag)

    assert sorted(result) == sorted(expected_files)

# Define a test for the scenario where an invalid directory is provided
def test_list_files_invalid_directory():
    # Expect a ValueError when listing files in a non-existent directory
    with pytest.raises(ValueError):
        list_files('invalid_directory')

# Define a test for listing files in an empty directory
def test_list_files_empty_directory(empty_dir):
    # Call list_files with a directory known to be empty
    result = list_files(empty_dir)
    # Check that the result is an empty list, as there are no files
    assert result == []

# Define a test for listing files in a directory with nested files
def test_list_files_nested_directory(nested_dir):
    # Define the expected list of file names
    expected_files = ['file1.txt', 'file2.txt']
    # Call list_files on a directory that contains nested files
    result = list_files(nested_dir)
    # Check that the result matches the expected list of files
    assert sorted(result) == sorted(expected_files)

@pytest.mark.parametrize("print_files_flag", [False, True])
def test_list_files_with_print(temp_dir, print_files_flag, capsys):
    """Test listing files with the print_files flag set to True."""
    # Create a file named 'file1.txt' in the temporary directory
    file1 = Path(temp_dir) / 'file1.txt'
    # Create a file named 'file2.txt' in the same temporary directory
    file2 = Path(temp_dir) / 'file2.txt'
    # Actually create the files on the filesystem
    file1.touch()
    file2.touch()

    # Call the list_files function to list files in the temporary directory
    # The print_files_flag controls whether the function prints the file names
    list_files(temp_dir, print_files_flag)

    # If we are supposed to print the file names (print_files_flag is True)
    if print_files_flag:
        # Capture the output printed to the console
        captured = capsys.readouterr()
        # Check if the output includes the expected introductory text
        assert 'Files in the directory:' in captured.out
        # Verify that the name of the first file appears in the output
        assert 'file1.txt' in captured.out
        # Verify that the name of the second file also appears in the output
        assert 'file2.txt' in captured.out

@pytest.mark.parametrize("print_files_flag", [False, True])
def test_list_files_nested_with_print(nested_dir, print_files_flag, capsys):
    """Test listing files in a nested directory with the print_files flag set to True."""
    # Call the list_files function with the nested_dir directory and the print_files_flag
    list_files(nested_dir, print_files_flag)
    
    # If print_files_flag is True, meaning we want to print the file names to the console
    if print_files_flag:
        # Capture the printed output from the console
        captured = capsys.readouterr()
        # Check if the output contains the expected introductory text
        assert 'Files in the directory:' in captured.out
        # Check if the name of the first file is in the output
        assert 'file1.txt' in captured.out
        # Check if the name of the second file is in the output
        assert 'file2.txt' in captured.out
