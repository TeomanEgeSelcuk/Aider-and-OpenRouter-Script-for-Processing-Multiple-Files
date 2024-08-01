'''
Proposed Unit Tests:
1. Valid Inputs: Ensure the execute function processes the files correctly with valid directory paths, file names, and test file names.
2. Invalid Directory Paths: Verify that the function handles non-existent or invalid directory paths gracefully.
3. Invalid File Names: Ensure the function handles invalid file names within valid directories correctly.
4. Empty Lists: Verify that the function raises an error if both `files_by_directory` and `test_file_names` are empty.
5. Flag Settings: Test various combinations of flags (`print_files`, `record_output`, `run_tests`, `verbose`) and ensure the function behaves as expected.
6. Missing Model: Verify that the function raises a `ValueError` if no model is provided.
7. Invalid Model Name: Ensure the function handles an invalid model name correctly.
8. Nested List Structure: Ensure the function raises appropriate errors for invalid nested list structures in `files_by_directory`.
9. Single Empty List: Verify that the function handles cases where only one of the lists (`files_by_directory` or `test_file_names`) is empty.

Explanation:
===========
Fixtures:
1. temp_directory: Creates temporary directories and files needed for testing.
2. model: Provides a mock model for testing purposes.

Parameterization:
Tests are parameterized to cover various flag settings and input combinations using `pytest.mark.parametrize`.

Tests:
1. test_execute_combined: Tests the execute function with different combinations of inputs and flags, including handling invalid inputs and edge cases.
'''

import pytest
import itertools
from Aider_Project.main import execute, aider_runner  # Import the execute function from main.py
from Aider_Project.execute_helper import is_nested_empty_list, validate_lengths, generate_and_count_lists # Import helper functions
import random
from typing import Any, List, Union, Tuple, Dict
from pathlib import Path
import ast
# from unittest.mock import MagicMock
import tempfile
import os
import textwrap
import time 

# For testing Aider package functionality
from aider.coders import Coder
from aider.models import Model
from aider.io import InputOutput 

def generate_nested_lists() -> list:
    """
    Generates a nested list structure that can be either an empty list or 
    a list with multiple levels of nested empty lists.

    Use-case: This is used to make the test case more robust by providing different empty list structures for 
    files_by_directory_values (filenames to be used for editing, context, running and getting the output from terminal when the module is ran)
    and for test_file_names_values (test filenames for context, running and getting the output from terminal when the tests are ran).

    Found in: The test_generate_nested_lists function, and the combination variable declaration in files_by_directory_values 
    and test_file_names_values test case.
    
    Returns:
        list: A nested list which is either an empty list or contains 
              multiple levels of nested empty lists.

    Example Usage:
        >>> nested_list = generate_nested_lists()
        >>> print(nested_list)
        []
        >>> print(generate_nested_lists())
        [[[[]]], [[], []]]
    """
    # Randomly choose to return either an empty list or a nested lists with varying depths that are also each empty
    return [] if random.choice([True, False]) else [[[[] for _ in range(random.randint(0, 4))] for _ in range(random.randint(0, 4))] for _ in range(random.randint(0, 4))]


def extract_classes_and_functions(file_path: str) -> Dict[str, Union[List[str], None]]:
    """
    Extracts class and function names from a given Python file.

    Purpose: This function helps in testing by extracting class and function names from a file, 
    allowing verification of whether the file contains the specified classes and functions.

    Used in: This function is used in the `test_aider_runner` test case to verify the 
    structure of Python files after modifications. Also in test_extract_classes_and_functions 
    for testing this function.

    Args:
        file_path (str): The absolute path to the Python file.

    Returns:
        Dict[str, Union[List[str], None]]: A dictionary containing class names and their respective function names,
                                           and standalone function names as keys with None as their value.

    Example Usage:
        >>> extract_classes_and_functions('/absolute/path/to/test_file.py')
        {
            'TestClass': ['method_one', 'method_two'],
            'standalone_function': None
        }
        # Explanation: This file contains one class 'TestClass' with two methods, and one standalone function.

        >>> extract_classes_and_functions('/absolute/path/to/another_test_file.py')
        {
            'SampleClass': ['__init__', 'sample_method']
        }
        # Explanation: This file contains one class 'SampleClass' with two methods and no standalone functions.

        >>> extract_classes_and_functions('/absolute/path/to/yet_another_test_file.py')
        {
            'helper_function': None
        }
        # Explanation: This file contains only a standalone function 'helper_function' and no classes.

        >>> extract_classes_and_functions('/absolute/path/to/no_classes_file.py')
        {
            'function_one': None,
            'function_two': None
        }
        # Explanation: This file contains only standalone functions 'function_one' and 'function_two' and no classes.

        >>> extract_classes_and_functions('/absolute/path/to/empty_file.py')
        {}
        # Explanation: This file contains no classes or functions.
    """
    # Open the specified Python file in read mode with UTF-8 encoding
    with open(file_path, 'r', encoding='utf-8') as file:
        # Parse the file content into an abstract syntax tree (AST)
        tree = ast.parse(file.read(), filename=file_path)
    
    # Initialize an empty dictionary to hold class names and their functions
    classes_and_functions = {}
    
    # Initialize a set to hold names of methods to avoid counting them as standalone functions
    method_names = set()
    
    # Walk through all nodes in the AST
    for node in ast.walk(tree):
        # Check if the node is a class definition
        if isinstance(node, ast.ClassDef):
            class_name = node.name  # Get the name of the class
            # Get all function names within the class
            function_names = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            # Add the class name and its functions to the dictionary
            classes_and_functions[class_name] = function_names
            # Add all function names to the set of method names
            method_names.update(function_names)
        # Check if the node is a standalone function definition and not a method
        elif isinstance(node, ast.FunctionDef):
            # If the function name is not in the set of method names, it is a standalone function
            if node.name not in method_names:
                classes_and_functions[node.name] = None
    
    # Return the dictionary containing class names with their functions and standalone functions
    return classes_and_functions


@pytest.mark.parametrize("iterations", [10, 20, 30])
def test_generate_nested_lists(iterations):
    """
    Tests the generate_nested_lists function to ensure it returns either an empty list
    or a nested empty list structure.

    Args:
        iterations: The number of times to run the test to cover random outputs.
    """
    for _ in range(iterations):
        nested_list = generate_nested_lists()  # Generate a nested list
        assert is_nested_empty_list(nested_list)  # Assert that the generated list is either empty or a nested empty list


@pytest.mark.parametrize(
    "file_content, expected_result",
    [
        # Test case 1: File containing a class with methods and a standalone function
        (
            textwrap.dedent("""
            class TestClass:
                def method_one(self):
                    pass

                def method_two(self):
                    pass

            def standalone_function():
                pass
            """),
            {
                'TestClass': ['method_one', 'method_two'],
                'standalone_function': None
            }
        ),
        # Test case 2: File containing a class with methods and no standalone functions
        (
            textwrap.dedent("""
            class SampleClass:
                def __init__(self):
                    pass

                def sample_method(self):
                    pass
            """),
            {
                'SampleClass': ['__init__', 'sample_method']
            }
        ),
        # Test case 3: File containing only a standalone function
        (
            textwrap.dedent("""
            def helper_function():
                pass
            """),
            {
                'helper_function': None
            }
        ),
        # Test case 4: File containing only standalone functions
        (
            textwrap.dedent("""
            def function_one():
                pass

            def function_two():
                pass
            """),
            {
                'function_one': None,
                'function_two': None
            }
        ),
        # Test case 5: Empty file
        (
            "",
            {}
        )
    ]
)
def test_extract_classes_and_functions(file_content: str, expected_result: Dict[str, Union[List[str], None]]) -> None:
    """
    Parameterized test for the extract_classes_and_functions function.

    Args:
        file_content (str): The content of the Python file to be tested.
        expected_result (Dict[str, Union[List[str], None]]): The expected result after extracting classes and functions.

    Example Usage:
        >>> test_extract_classes_and_functions(file_content, expected_result)
        # This will run the test with the provided file content and expected result.
    """
    # Create a temporary file to hold the test content
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
        temp_file.write(file_content.encode('utf-8'))
        temp_file_path = temp_file.name

    try:
        # Call the function with the path to the temporary file
        result = extract_classes_and_functions(temp_file_path)
        # Assert that the result matches the expected result
        assert result == expected_result, f"Expected {expected_result}, but got {result}"
    finally:
        # Clean up the temporary file
        os.remove(temp_file_path)

@pytest.fixture
def mock_environment(tmp_path) -> Dict[str, Any]:
    """
    Fixture for creating a temporary directory for file operations and providing a model.

    Returns:
        dict: Dictionary containing a model object and a temp directory.
    """
    temp_dir = tmp_path / "mock_dir"
    temp_dir.mkdir()
    
    return {
        "model": Model("openrouter/deepseek/deepseek-coder"),  # Use the predefined model identifier
        "temp_dir": temp_dir  # Temporary directory for creating files
    }

@pytest.mark.parametrize(
    "directory, files_by_directory, instructions, expected_exception, expected_functions_classes",
    [
        # Valid inputs: directory and files exist, instructions provided to modify the files
        (
            "directory", 
            ["file1.py", "file2.py"], 
            ["file1.py: create function print_hello_world", "file2.py: create class SumCalculator with method calculate_sum"], 
            None,  # No exception expected
            {
                "file1.py": {
                    "print_hello_world": None
                },
                "file2.py": {
                    "SumCalculator": ["calculate_sum"]
                }
            }  # Expected content in the files
        ),
        # Empty file list: directory exists, but no files are listed to be modified. Should raise an error.
        (
            "empty_directory", 
            [], 
            ["file1.py: create function print_hello_world"], 
            ValueError,  # error expected due to empty file list
            {}  # No files to check for content
        ),
        # Single file: directory and one file exist, instruction provided to modify the single file
        (
            "directory_with_one_file", 
            ["single_file.py"], 
            ["single_file.py: create function print_numbers"], 
            None,  # No exception expected
            {
                "single_file.py": {
                    "print_numbers": None
                }
            }  # Expected content in the single file
        ),
        # Invalid directory: directory does not exist, should raise an error
        (
            "invalid_directory", 
            ["file1.py"], 
            ["file1.py: create function print_hello_world"], 
            FileNotFoundError,  # error expected due to invalid directory
            {}  # No files to check for content
        ),
        # Non-existent file: directory exists, but file does not exist, should raise an error
        (
            "valid_directory", 
            ["non_existent_file.py"], 
            ["non_existent_file.py: create function print_hello_world"], 
            FileNotFoundError,  # error expected due to non-existent file
            {}  # No files to check for content
        ),
        # No instructions: directory and file exist, but no instructions provided to modify the file
        (
            "directory", 
            ["file1.py"], 
            [], 
            None,  # No exception expected
            {"file1.py": {}}  # No expected content since no instructions were provided
        ),
    ]
)
def test_aider_runner(
    mock_environment: Dict[str, Any], 
    directory: str, 
    files_by_directory: List[str], 
    instructions: List[str], 
    expected_exception: Any,
    expected_functions_classes: Dict[str, Dict[str, Union[List[str], None]]]
) -> None:
    """
    Parameterized test for the aider_runner function.

    Args:
        mock_environment (dict): Dictionary containing a model object and a temp directory.
        directory (str): Directory path.
        files_by_directory (List[str]): List of file names in the directory.
        instructions (List[str]): List of instructions to run on the files.
        expected_exception (Exception or None): Expected exception to be raised, if any.
        expected_functions_classes (Dict[str, Dict[str, Union[List[str], None]]]): Expected functions or classes to be present in the files after modification.
    """
    model = mock_environment["model"]  # Get the mock model from the fixture
    temp_dir = mock_environment["temp_dir"]  # Get the temporary directory


    # Create mock files in the temporary directory
    dir_path = Path(temp_dir) / directory
    dir_path.mkdir(parents=True, exist_ok=True)  # Create the directory path
    for file_name in files_by_directory:
        (dir_path / file_name).touch()  # Create empty files for each file name in the list

    if expected_exception:
        # Handle special cases for invalid directory and non-existent files
        if directory == "invalid_directory":
            dir_path = Path("non_existent_directory_path")  # Set a non-existent directory path
        elif directory == "valid_directory" and "non_existent_file.py" in files_by_directory:
            non_existent_file_path = str(Path(temp_dir) / directory / "this_file_does_not_exist.py")
            files_by_directory = [non_existent_file_path]  # Set non-existent file paths

        # If an exception is expected, verify that it is raised
        with pytest.raises(expected_exception):
            aider_runner(str(dir_path), files_by_directory, model, instructions)
    else:
        # Call aider_runner with the provided parameters
        aider_runner(str(dir_path), files_by_directory, model, instructions)

        # Check the contents of the files to verify the expected functions/classes were added
        for file_name, expected_content in expected_functions_classes.items():
            file_path = dir_path / file_name  # Get the path of the file to check
            classes_and_functions = extract_classes_and_functions(str(file_path))  # Extract the classes and functions from the file
            for name, methods in expected_content.items():
                # Check if the expected class/function is in the extracted content
                assert name in classes_and_functions, f"Expected '{name}' in {file_name}"
                if methods is not None:
                    for method in methods:
                        assert method in classes_and_functions[name], f"Expected method '{method}' in class '{name}' in {file_name}"
        
        # Add a delay of one second after the else statement to avoid API rate limit issues
        time.sleep(1)

# Fixtures for creating temporary directories and files
@pytest.fixture
def temp_directory(tmp_path):
    # Use pytest's built-in tmp_path fixture to create a temporary directory for tests
    dir1 = tmp_path / "dir1"  # Create a subdirectory named 'dir1' within the temporary directory
    dir2 = tmp_path / "dir2"  # Create another subdirectory named 'dir2'
    dir1.mkdir()  # Actually create 'dir1' on the filesystem
    dir2.mkdir()  # Actually create 'dir2' on the filesystem
    # Create a file named 'math_functions.py' in 'dir1' with a simple print statement
    (dir1 / "math_functions.py").write_text("print('Math Functions')")
    # Create a test file named 'test.py' in 'dir1' with a simple print statement
    (dir1 / "test.py").write_text("print('Test File')")
    # Create another script file in 'dir2' with a simple print statement
    (dir2 / "another_script.py").write_text("print('Another Script')")
    # Create another test file in 'dir2' with a simple print statement
    (dir2 / "yet_another_test.py").write_text("print('Yet Another Test')")
    return [str(dir1), str(dir2)]  # Return the paths of the created directories as strings

# Define possible values for each parameter
directory_paths_values = [["invalid_dir"], ["dir1", "dir2"]]  # Possible values for directory paths
files_by_directory_values = [[['math_functions.py', 'test.py'], ['another_script.py', 'yet_another_test.py']], [['invalid_file.py'], ['invalid_script.py']], generate_nested_lists()]  # Possible values for files by directory
test_file_names_values = [[['test.py'], ['yet_another_test.py']], generate_nested_lists()]  # Possible values for test file names
record_output_values = [True, False, "Mix"]  # Possible values for record_output flag
record_test_output_values = [True, False, "Mix"]  # Possible values for record_test_output flag
run_tests_values = [True, False, "Mix"]  # Possible values for run_tests flag
verbose_values = [True, False]  # Possible values for verbose flag
model_provided_values = [True, False, "invalid_model_name"]  # Possible values for model provided flag

# Generate all combinations of these values
test_data = list(itertools.product(
    directory_paths_values,  # All combinations of directory paths values
    files_by_directory_values,  # All combinations of files by directory values
    test_file_names_values,  # All combinations of test file names values
    record_output_values,  # All combinations of record_output flag values
    record_test_output_values,  # All combinations of record_test_output flag values
    run_tests_values,  # All combinations of run_tests flag values
    verbose_values,  # All combinations of verbose flag values
    model_provided_values,  # All combinations of model provided values
))

def execute_with_exception_handling(directory_paths, files_by_directory, test_file_names, record_output, record_test_output, run_tests, verbose, model, expected_exception):
    """Helper function to execute with exception handling."""
    with pytest.raises(expected_exception):
        execute(
            directory_paths=directory_paths,
            files_by_directory=files_by_directory,
            record_output=record_output,
            record_test_output=record_test_output,
            run_tests=run_tests,
            test_file_names=test_file_names,
            verbose=verbose,
            model=model,
        )

@pytest.mark.parametrize("directory_paths, files_by_directory, test_file_names, record_output, record_test_output, run_tests, verbose, model_provided", test_data)
def test_execute_combined(temp_directory, model, directory_paths, files_by_directory, test_file_names, record_output, record_test_output, run_tests, verbose, model_provided):
    # Setup test directories and files
    if "dir1" in directory_paths:  # Check if "dir1" is in the directory paths
        directory_paths = temp_directory  # Use temporary directory if "dir1" is present
    
    if model_provided == "invalid_model_name":  # Check if an invalid model name is provided
        model = Model("invalid_model_name")  # Set model to an invalid model name
    elif model_provided:  # Check if a model is provided
        model = model  # Use the provided model
    else:
        model = None  # Set model to None if no model is provided
    
    # Call the generate_and_count_lists function which overwrites the record_output, record_test_output, and run_tests lists
    record_output, record_test_output, run_tests = generate_and_count_lists(
        files_by_directory, test_file_names, record_output, record_test_output, run_tests
    )

    # Execute the function with the provided parameters
    if directory_paths == ["invalid_dir"]:  # Check if the directory paths are invalid
        execute_with_exception_handling(directory_paths, files_by_directory, test_file_names, record_output, record_test_output, run_tests, verbose, model, instructions, Exception)
    elif files_by_directory == [['invalid_file.py'], ['invalid_script.py']]:  # Check if the files are invalid
        execute_with_exception_handling(directory_paths, files_by_directory, test_file_names, record_output, record_test_output, run_tests, verbose, model, instructions, Exception)
    elif validate_lengths(files_by_directory, run_tests_values, record_test_output) and validate_lengths(files_by_directory, record_output_values):  # Check if the lengths of the lists do not match
        execute_with_exception_handling(directory_paths, files_by_directory, test_file_names, record_output, record_test_output, run_tests, verbose, model, instructions, ValueError)
    elif is_nested_empty_list(files_by_directory) and is_nested_empty_list(test_file_names):  # Check if both files and test file lists are empty
        execute_with_exception_handling(directory_paths, files_by_directory, test_file_names, record_output, record_test_output, run_tests, verbose, model, instructions, Exception)
    elif not model_provided:  # Check if the model is not provided
        execute_with_exception_handling(directory_paths, files_by_directory, test_file_names, record_output, record_test_output, run_tests, verbose, model, instructions, ValueError)
    elif model_provided == "invalid_model_name":  # Check if the model provided is invalid
        execute_with_exception_handling(directory_paths, files_by_directory, test_file_names, record_output, record_test_output, run_tests, verbose, model, instructions, Exception)
    elif files_by_directory == [['math_functions.py', ['test.py']], ['another_script.py']]:  # Check if the nested list structure is invalid
        execute_with_exception_handling(directory_paths, files_by_directory, test_file_names, record_output, record_test_output, run_tests, verbose, model, instructions, Exception)
    else:  # For valid inputs
        script_outputs, test_outputs = execute(
            directory_paths=directory_paths,
            files_by_directory=files_by_directory,
            record_output=record_output,
            record_test_output=record_test_output,
            run_tests=run_tests,
            test_file_names=test_file_names,
            verbose=verbose,
            model=model,
        )
        assert isinstance(script_outputs, dict)  # Assert that script outputs are a dictionary
        assert isinstance(test_outputs, dict)  # Assert that test outputs are a dictionary

# Run the tests
if __name__ == "__main__":
    pytest.main()