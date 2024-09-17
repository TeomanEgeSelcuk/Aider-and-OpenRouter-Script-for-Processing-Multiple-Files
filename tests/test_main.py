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

from Aider_Project.main import execute, aider_runner  # Import the execute function from main.py
from Aider_Project.execute_helper import is_nested_empty_list # Import helper functions
import random
from typing import Any, List, Union, Dict, Generator
from pathlib import Path
import ast
import tempfile
import shutil  # Import shutil for directory removal
import os
import textwrap
import time 
from unittest.mock import patch

# For testing Aider package functionality
from aider.models import Model

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

def adjust_outputs(outputs: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    """
    Adjust outputs for comparison by consistently formatting directory paths
    to include the last two parts of the file path. Use for formatting the execute() functions 
    returns and used in the test_execute() function, to make simplified assertions.  

    Args:
        outputs (dict): The dictionary of outputs to adjust.

    Returns:
        dict: Adjusted outputs.

    Example usage:
        # Basic test output with directory paths adjusted
        outputs_1 = {
            "dir1/test_file1.py": {"stdout": "Test output 1", "stderr": ""},
            "dir2/test_file3.py": {"stdout": "Test output 2", "stderr": ""}
        }
        adjusted_outputs_1 = adjust_outputs(outputs_1)
        # Expected output: {'dir1/test_file1.py': {'stdout': 'Test output 1', 'stderr': ''}, 'dir2/test_file3.py': {'stdout': 'Test output 2', 'stderr': ''}}

        # Script output with adjusted directory paths
        outputs_2 = {
            "/tmp/pytest-of-user/pytest-198/test_execute_None_files_by_dir0/dir1/file1.py": {"stdout": "Script output 1", "stderr": ""},
            "/tmp/pytest-of-user/pytest-198/test_execute_None_files_by_dir0/dir2/file3.py": {"stdout": "Script output 2", "stderr": ""}
        }
        adjusted_outputs_2 = adjust_outputs(outputs_2)
        # Expected output: {'dir1/file1.py': {'stdout': 'Script output 1', 'stderr': ''}, 'dir2/file3.py': {'stdout': 'Script output 2', 'stderr': ''}}

        # Test output with stderr containing lines to be filtered
        outputs_3 = {
            "dir1/test_file1.py": {"stdout": "Test output 1", "stderr": "Debugger warning\nSome other error\nDebugging issue"},
            "dir2/test_file3.py": {"stdout": "Test output 2", "stderr": "Frozen modules warning\nAnother error"}
        }
        adjusted_outputs_3 = adjust_outputs(outputs_3)
        # Expected output: {'dir1/test_file1.py': {'stdout': 'Test output 1', 'stderr': 'Some other error'}, 'dir2/test_file3.py': {'stdout': 'Test output 2', 'stderr': 'Another error'}}
    """
    adjusted_outputs: Dict[str, Dict[str, str]] = {}
    
    for key, value in outputs.items():
        # Adjust the key to include the last two parts of the file path
        # Example: "C:/path/to/dir1/file1.py" -> "dir1/file1.py"
        adjusted_key = "/".join(Path(key).parts[-2:])  # Example: "dir1/file1.py"
        
        adjusted_outputs[adjusted_key] = value
    
        # Remove lines containing "debugger", "debugging", or "frozen modules" from stderr
        if 'stderr' in adjusted_outputs[adjusted_key]:
            # Split stderr by newlines to handle multiple lines of errors
            # Example: "Error occurred\nDebugger attached\nAnother error" -> ["Error occurred", "Debugger attached", "Another error"]
            stderr_lines = adjusted_outputs[adjusted_key]['stderr'].split('\n')
            
            # Filter out lines that contain the specified words, case-insensitive
            # Example: ["Error occurred", "Debugger attached", "Another error"] -> ["Error occurred", "Another error"]
            filtered_stderr_lines = [
                line for line in stderr_lines 
                if not any(word in line.lower() for word in ['debugger', 'debugging', 'frozen modules'])
            ]
            
            # Join the filtered lines back into a single string
            # Example: ["Error occurred", "Another error"] -> "Error occurred\nAnother error"
            adjusted_outputs[adjusted_key]['stderr'] = '\n'.join(filtered_stderr_lines)
    
    return adjusted_outputs

def assert_outputs(actual_outputs: Dict[str, Dict[str, str]], expected_outputs: Dict[str, Dict[str, str]], is_test: bool = False) -> bool:
    """
    Asserts that the actual outputs match the expected outputs. Used in the test_execute() function
    to validate the results of test cases for both test files and normal files.

    For test files:
    - Checks if the output contains specific substrings indicating that tests have passed.
    - Also compares the standard output and standard error with the expected values.

    For normal files:
    - Compares the standard output and standard error with the expected values.

    This ensures that the execute() function returns the correct results for both types of files.

    Args:
        actual_outputs (dict): Dictionary of actual outputs to check.
        expected_outputs (dict): Dictionary of expected outputs to compare against.
        is_test (bool): Flag to indicate if the outputs are from tests or scripts. Defaults to False.

    Returns:
        bool: True if all assertions pass, False if any assertion fails.
    """
    try:
        for expected_key, expected_output in expected_outputs.items():
            # Example: "dir1/test_file1.py" on Windows -> "dir1\\test_file1.py" -> normalized_key
            # Input Example: "C:\\some\\path\\dir1\\test_file1.py" -> Output Example: "dir1\\test_file1.py"
            normalized_key = os.path.join(*os.path.normpath(expected_key).split(os.sep)[-2:])

            # Find the corresponding key in the actual outputs, handling potential path discrepancies
            # Example: actual_outputs = {"C:\\some\\other\\path\\dir1\\test_file1.py": {...}} -> "dir1\\test_file1.py" == normalized_key -> actual_key
            actual_key = None
            for key in actual_outputs:
                # Normalize and extract the last two components (directory and file name)
                # Input Example: "C:\\some\\other\\path\\dir2\\test_file2.py" -> Output Example: "dir2\\test_file2.py"
                normalized_actual_key = os.path.join(*os.path.normpath(key).split(os.sep)[-2:])
                
                # Check if this normalized key matches the expected one
                if normalized_actual_key == normalized_key:
                    actual_key = key
                    break

            # Assert that a match was found
            # Example Assertion: If normalized_key is "dir1\\test_file1.py" and actual_key is None, the assertion fails.
            assert actual_key is not None, f"{normalized_key} not found in outputs"

            # Retrieve the actual output for comparison
            # Example: actual_outputs = {"dir1/test_file1.py": {"stdout": "output", "stderr": "error"}} -> actual_output = {"stdout": "output", "stderr": "error"}
            actual_output = actual_outputs[actual_key]

            if is_test and not (expected_output["stdout"] == "" and expected_output["stderr"] == ""):
                # Define the required substrings to check in stdout for a valid test output
                required_substrings = [
                    "============================= test session starts =============================",
                    f"{Path(expected_key).name}",  # Ensure the filename is in the output
                    "[100%]",
                    "1 passed in"
                ]
                # Check if all required substrings are present in stdout
                # Example: actual_output['stdout'] = "test session starts\nfile.py\n[100%]\n1 passed in" -> substring in actual_output['stdout']
                for substring in required_substrings:
                    # Example: "============================= test session starts =============================" -> True (if present)
                    assert substring in actual_output['stdout'], f"Output mismatch for {expected_key}: '{substring}' not found in stdout"
                
                # Special case handling for tests with "More output" in stdout
                # Example: expected_output['stdout'] = "More output\nDetails", actual_output['stdout'] = "More output\nDetails" -> "More output" in actual_output['stdout']
                if "More output" in expected_output['stdout']:
                    # Example: "More output" -> True (if present)
                    assert "More output" in actual_output['stdout'], f"Output mismatch for {expected_key}: 'More output' not found in stdout"
            else:
                # Assert that the stdout of the actual output matches the expected stdout
                # Example: actual_output['stdout'] = "output", expected_output['stdout'] = "output" -> actual_output['stdout'] == expected_output['stdout']
                assert actual_output['stdout'] == expected_output['stdout'], f"Output mismatch for {expected_key}: {actual_output['stdout']} != {expected_output['stdout']}"
            
            # Assert that stderr matches
            # Example: actual_output['stderr'] = "error", expected_output['stderr'] = "error" -> actual_output['stderr'] == expected_output['stderr']
            assert actual_output['stderr'] == expected_output['stderr'], f"Error output mismatch for {expected_key}: {actual_output['stderr']} != {expected_output['stderr']}"
        
        return True
    except AssertionError as e:
        # Example: AssertionError: "Error output mismatch for dir1/test_file1.py: error !="
        print(e)
        return False

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
        ),
    ],
    ids=[
        "1",  # Test Case 1
        "2",  # Test Case 2
        "3",  # Test Case 3
        "4",  # Test Case 4
        "5"   # Test Case 5
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

@pytest.mark.parametrize("outputs, expected", [
    # Basic test output with directory paths adjusted
    (
        {
            "dir1/test_file1.py": {"stdout": "Test output 1", "stderr": ""},
            "dir2/test_file3.py": {"stdout": "Test output 2", "stderr": ""}
        },
        {
            'dir1/test_file1.py': {'stdout': 'Test output 1', 'stderr': ''},
            'dir2/test_file3.py': {'stdout': 'Test output 2', 'stderr': ''}
        }
    ),
    # Script output with adjusted directory paths
    (
        {
            "/tmp/pytest-of-user/pytest-198/test_execute_None_files_by_dir0/dir1/file1.py": {"stdout": "Script output 1", "stderr": ""},
            "/tmp/pytest-of-user/pytest-198/test_execute_None_files_by_dir0/dir2/file3.py": {"stdout": "Script output 2", "stderr": ""}
        },
        {
            'dir1/file1.py': {'stdout': 'Script output 1', 'stderr': ''},
            'dir2/file3.py': {'stdout': 'Script output 2', 'stderr': ''}
        }
    ),
    # Test output with stderr containing lines to be filtered
    (
        {
            "dir1/test_file1.py": {"stdout": "Test output 1", "stderr": "Debugger warning\nSome other error\nDebugging issue"},
            "dir2/test_file3.py": {"stdout": "Test output 2", "stderr": "Frozen modules warning\nAnother error"}
        },
        {
            'dir1/test_file1.py': {'stdout': 'Test output 1', 'stderr': 'Some other error'},
            'dir2/test_file3.py': {'stdout': 'Test output 2', 'stderr': 'Another error'}
        }
    ),
    # Mixed output
    (
        {
            "dir1/test_file1.py": {"stdout": "Mixed output 1", "stderr": ""},
            "dir2/file3.py": {"stdout": "Mixed output 2", "stderr": ""}
        },
        {
            'dir1/test_file1.py': {'stdout': 'Mixed output 1', 'stderr': ''},
            'dir2/file3.py': {'stdout': 'Mixed output 2', 'stderr': ''}
        }
    ),
    # Test case with Windows-style paths and double backslashes
    (
        {
            "C:\\dir1\\test_file1.py": {"stdout": "Win output 1", "stderr": ""},
            "C:\\dir2\\test_file3.py": {"stdout": "Win output 2", "stderr": ""}
        },
        {
            'dir1/test_file1.py': {'stdout': 'Win output 1', 'stderr': ''},
            'dir2/test_file3.py': {'stdout': 'Win output 2', 'stderr': ''}
        }
    ),
    # Mixed case with Windows-style paths and stderr filtering
    (
        {
            "C:\\dir1\\test_file1.py": {"stdout": "Mixed Win output 1", "stderr": "Debugger warning\nSome other error"},
            "C:\\dir2\\test_file3.py": {"stdout": "Mixed Win output 2", "stderr": "Debugging issue\nAnother error"}
        },
        {
            'dir1/test_file1.py': {'stdout': 'Mixed Win output 1', 'stderr': 'Some other error'},
            'dir2/test_file3.py': {'stdout': 'Mixed Win output 2', 'stderr': 'Another error'}
        }
    ),
    # Test case with very long paths
    (
        {
            "/a/very/long/path/to/the/directory/structure/dir1/test_file1.py": {"stdout": "Long path output 1", "stderr": ""},
            "/a/very/long/path/to/the/directory/structure/dir2/test_file3.py": {"stdout": "Long path output 2", "stderr": ""}
        },
        {
            'dir1/test_file1.py': {'stdout': 'Long path output 1', 'stderr': ''},
            'dir2/test_file3.py': {'stdout': 'Long path output 2', 'stderr': ''}
        }
    ),
    # Test case with very long Windows-style paths
    (
        {
            "C:\\a\\very\\long\\path\\to\\the\\directory\\structure\\dir1\\test_file1.py": {"stdout": "Long Win path output 1", "stderr": ""},
            "C:\\a\\very\\long\\path\\to\\the\\directory\\structure\\dir2\\test_file3.py": {"stdout": "Long Win path output 2", "stderr": ""}
        },
        {
            'dir1/test_file1.py': {'stdout': 'Long Win path output 1', 'stderr': ''},
            'dir2/test_file3.py': {'stdout': 'Long Win path output 2', 'stderr': ''}
        }
    )
])
def test_adjust_outputs(outputs, expected):
    """
    Test the adjust_outputs function with various cases, handling different
    file path formats, and filtering stderr lines.

    Args:
        outputs (dict): The dictionary of outputs to adjust.
        expected (dict): The expected adjusted outputs.
    """
    result = adjust_outputs(outputs)
    assert result == expected

@pytest.mark.parametrize("actual_outputs, expected_outputs, is_test, should_fail", [
    # Test Case 1: Basic test case where actual and expected outputs match for a single test file
    (
        {
            "dir1/test_file1.py": {"stdout": "============================= test session starts =============================\ndir1/test_file1.py\n[100%]\n1 passed in", "stderr": ""}
        }, # actual_outputs
        {
            "dir1/test_file1.py": {"stdout": "============================= test session starts =============================\ndir1/test_file1.py\n[100%]\n1 passed in", "stderr": ""}
        }, # expected_outputs
        True, # is_test
        False # should_fail
    ),
    # Test Case 2: Test case with stderr output for a test file
    (
        {
            "dir1/test_file1.py": {"stdout": "============================= test session starts =============================\ndir1/test_file1.py\n[100%]\n1 passed in", "stderr": "Some error"}
        }, # actual_outputs
        {
            "dir1/test_file1.py": {"stdout": "============================= test session starts =============================\ndir1/test_file1.py\n[100%]\n1 passed in", "stderr": "Some error"}
        }, # expected_outputs
        True, # is_test
        False # should_fail
    ),
    # Test Case 3: Test case with Windows-style paths for a test file
    (
        {
            "C:\\dir1\\test_file1.py": {"stdout": "============================= test session starts =============================\ndir1\\test_file1.py\n[100%]\n1 passed in", "stderr": ""}
        }, # actual_outputs
        {
            "dir1/test_file1.py": {"stdout": "============================= test session starts =============================\ndir1/test_file1.py\n[100%]\n1 passed in", "stderr": ""}
        }, # expected_outputs
        True, # is_test
        False # should_fail
    ),
    # Test Case 4: Test case with additional required substrings in stdout for a test file
    (
        {
            "dir1/test_file1.py": {"stdout": "============================= test session starts =============================\ndir1/test_file1.py\n[100%]\n1 passed in\nMore output", "stderr": ""}
        }, # actual_outputs
        {
            "dir1/test_file1.py": {"stdout": "============================= test session starts =============================\ndir1/test_file1.py\n[100%]\n1 passed in\nMore output", "stderr": ""}
        }, # expected_outputs
        True, # is_test
        False # should_fail
    ),
    # Test Case 5: Normal script case where actual and expected outputs match (not a test case)
    (
        {
            "dir1/file1.py": {"stdout": "Result of add: 5\n", "stderr": ""},
            "dir2/file3.py": {"stdout": "Result of subtract: 2\n", "stderr": ""}
        }, # actual_outputs
        {
            "dir1/file1.py": {"stdout": "Result of add: 5\n", "stderr": ""},
            "dir2/file3.py": {"stdout": "Result of subtract: 2\n", "stderr": ""}
        }, # expected_outputs
        False, # is_test
        False # should_fail
    ),
    # Test Case 6: Normal script case with mixed outputs
    (
        {
            "dir1/file1.py": {"stdout": "Result of add: 5\n", "stderr": "Warning: something"},
            "dir2/file3.py": {"stdout": "Result of subtract: 2\n", "stderr": ""}
        }, # actual_outputs
        {
            "dir1/file1.py": {"stdout": "Result of add: 5\n", "stderr": "Warning: something"},
            "dir2/file3.py": {"stdout": "Result of subtract: 2\n", "stderr": ""}
        }, # expected_outputs
        False, # is_test
        False # should_fail
    ),
    # Test Case 7: Another normal script case with no output
    (
        {
            "dir1/empty_script.py": {"stdout": "", "stderr": ""}
        }, # actual_outputs
        {
            "dir1/empty_script.py": {"stdout": "", "stderr": ""}
        }, # expected_outputs
        False, # is_test
        False # should_fail
    ),
    # Test Case 8: Failing test case: Output mismatch in test file
    (
        {
            "dir1/test_file1.py": {"stdout": "============================= test session starts =============================\ndir1/test_file1.py\n[100%]\n1 passed in", "stderr": ""},
            "dir2/script_file.py": {"stdout": "Script output", "stderr": ""}
        }, # actual_outputs
        {
            "dir1/test_file1.py": {"stdout": "============================= test session starts =============================\ndir1/test_file1.py\n[100%]\n1 failed in", "stderr": ""},
            "dir2/script_file.py": {"stdout": "Script output", "stderr": ""}
        }, # expected_outputs
        True, # is_test
        True # should_fail
    ),
    # Test Case 9: Failing test case: Missing required substring in test file stdout
    (
        {
            "dir1/test_file1.py": {"stdout": "============================= test session starts =============================\ndir1/test_file1.py\n[90%]\n1 passed in", "stderr": ""},
            "dir2/script_file.py": {"stdout": "Script output", "stderr": ""}
        }, # actual_outputs
        {
            "dir1/test_file1.py": {"stdout": "============================= test session starts =============================\ndir1/test_file1.py\n[100%]\n1 passed in", "stderr": ""},
            "dir2/script_file.py": {"stdout": "Script output", "stderr": ""}
        }, # expected_outputs
        True, # is_test
        True # should_fail
    ),
    # Test Case 10: Failing test case: Error output mismatch in test file
    (
        {
            "dir1/test_file1.py": {"stdout": "============================= test session starts =============================\ndir1/test_file1.py\n[100%]\n1 passed in", "stderr": "Some error"},
            "dir2/script_file.py": {"stdout": "Script output", "stderr": ""}
        }, # actual_outputs
        {
            "dir1/test_file1.py": {"stdout": "============================= test session starts =============================\ndir1/test_file1.py\n[100%]\n1 passed in", "stderr": ""},
            "dir2/script_file.py": {"stdout": "Script output", "stderr": ""}
        }, # expected_outputs
        True, # is_test
        True # should_fail
    ),
    # Test Case 11: Failing test case: Script file output mismatch
    (
        {
            "dir1/file1.py": {"stdout": "Result of add: 4\n", "stderr": ""},
            "dir2/file3.py": {"stdout": "Result of subtract: 2\n", "stderr": ""}
        }, # actual_outputs
        {
            "dir1/file1.py": {"stdout": "Result of add: 5\n", "stderr": ""},
            "dir2/file3.py": {"stdout": "Result of subtract: 2\n", "stderr": ""}
        }, # expected_outputs
        False, # is_test
        True # should_fail
    ),
    # Test Case 12: Failing test case: Error output mismatch in script file
    (
        {
            "dir1/file1.py": {"stdout": "Result of add: 5\n", "stderr": "Warning: something"},
            "dir2/file3.py": {"stdout": "Result of subtract: 2\n", "stderr": "Error occurred"}
        }, # actual_outputs
        {
            "dir1/file1.py": {"stdout": "Result of add: 5\n", "stderr": "Warning: something"},
            "dir2/file3.py": {"stdout": "Result of subtract: 2\n", "stderr": ""}
        }, # expected_outputs
        False, # is_test
        True # should_fail
    ),
    # Test Case 13: No errors, matching actual and expected outputs
    (
        {
            "dir1/test_file1.py": {"stdout": "============================= test session starts =============================\ndir1/test_file1.py\n[100%]\n1 passed in 0.02s ==============================", "stderr": ""},
            "dir1/test_file2.py": {"stdout": "", "stderr": ""},
            "dir2/test_file3.py": {"stdout": "", "stderr": ""}
        }, # actual_outputs
        {
            "dir1/test_file1.py": {"stdout": "============================= test session starts =============================\ndir1/test_file1.py\n[100%]\n1 passed in 0.02s ==============================", "stderr": ""},
            "dir1/test_file2.py": {"stdout": "", "stderr": ""},
            "dir2/test_file3.py": {"stdout": "", "stderr": ""}
        }, # expected_outputs
        True, # is_test
        False # should_fail
    )
],
ids=[
    "1",  # Test Case 1
    "2",  # Test Case 2
    "3",  # Test Case 3
    "4",  # Test Case 4
    "5",  # Test Case 5
    "6",  # Test Case 6
    "7",  # Test Case 7
    "8",  # Test Case 8
    "9",  # Test Case 9
    "10", # Test Case 10
    "11", # Test Case 11
    "12", # Test Case 12
    "13"  # Test Case 13 
])
def test_assert_outputs(actual_outputs, expected_outputs, is_test, should_fail):
    """
    Test the assert_outputs function with various cases, including matching actual and expected outputs,
    handling different file path formats, and verifying specific substrings in stdout.

    Args:
        actual_outputs (dict): Dictionary of actual outputs to check.
        expected_outputs (dict): Dictionary of expected outputs to compare against.
        is_test (bool): Flag to indicate if the outputs are from tests or scripts.
        should_fail (bool): Flag to indicate if the test case is expected to fail.
    """
    if should_fail:
        # If should_fail is True, assert that assert_outputs returns False
        assert not assert_outputs(actual_outputs, expected_outputs, is_test), "Expected assert_outputs to return False"
        # Example: actual_outputs = ["output1"], expected_outputs = ["output2"], is_test = True or False -> assert_outputs(...) = False
    else:
        # If should_fail is False, assert that assert_outputs returns True
        assert assert_outputs(actual_outputs, expected_outputs, is_test), "Expected assert_outputs to return True"
        # Example: actual_outputs = ["output1"], expected_outputs = ["output1"], is_test = True or False -> assert_outputs(...) = True

@pytest.fixture
def mock_environment(tmp_path) -> Generator[Dict[str, Any], None, None]:
    """
    Fixture for creating a temporary directory for file operations and providing a model.

    Returns:
        dict: Dictionary containing a model object and a temp directory.
    """
    temp_dir = tmp_path / "mock_dir"
    temp_dir.mkdir()
    
    # Yield control to the test function, providing the model and temp directory
    yield {
        "model": Model("openrouter/deepseek/deepseek-coder"),  # Use the predefined model identifier
        "temp_dir": temp_dir  # Temporary directory for creating files
    }

    # Teardown: Cleanup of the temp_dir
    if temp_dir.exists():
        shutil.rmtree(temp_dir)  # Remove the parent of the parent directory

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


@pytest.fixture(scope="session", autouse=True)
def disable_frozen_modules():
    os.environ["PYTHONPATH"] = "-Xfrozen_modules=off"
    yield
    del os.environ["PYTHONPATH"]

@pytest.fixture(scope="session", autouse=True)
def disable_file_validation():
    os.environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"
    yield
    del os.environ["PYDEVD_DISABLE_FILE_VALIDATION"]

@pytest.fixture
def temp_directory(tmp_path):
    """
    Fixture to create a temporary directory structure for testing.

    Creates multiple directories with normal files and test files.
    """
    # Create main directories
    dir1 = tmp_path / "dir1"
    dir2 = tmp_path / "dir2"
    dir1.mkdir()
    dir2.mkdir()

    # Create normal files in dir1
    file1 = dir1 / "file1.py"
    file1.write_text(textwrap.dedent("""
    # file1.py
    # Some initial comment
    # Another comment line
    # This file is for demonstrating the add function
    # More comments to simulate a real file
    """))
    file2 = dir1 / "file2.py"
    file2.write_text(textwrap.dedent('''
    # file2.py
    # This file is for demonstrating the multiplication function 
    # Multiplies two input arguments 
    '''))

    # Create normal files in dir2
    file3 = dir2 / "file3.py"
    file3.write_text(textwrap.dedent("""
    # file3.py
    # This file contains the subtract function
    # Subtracts the second argument from the first argument
    """))

    # Create test files in dir1
    test_file1 = dir1 / "test_file1.py"
    test_file1.write_text(textwrap.dedent("""
    import pytest

    # Tests the addition function 
    # Makes a simple single assertion to test the add function
    """))

    test_file2 = dir1 / "test_file2.py"
    test_file2.write_text(textwrap.dedent("""
    import pytest

    # Tests the multipication function 
    # Makes a simple single assertion to test the multiply function
    """))

    # Create test files in dir2
    test_file3 = dir2 / "test_file3.py"
    test_file3.write_text(textwrap.dedent("""
    import pytest

    # Tests the subtraction function 
    # Makes a simple single assertion to test the subtraction function
    """))

    # Yield control to the test function, providing paths to directories
    directory_paths = [str(dir1), str(dir2)]
    yield {
        "directory_paths": directory_paths
    }

    # Teardown: Cleanup the directories after the test is complete
    for dir_path in directory_paths:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)


            
@pytest.fixture
def model():
    """
    Fixture to create the model instance for testing.

    Returns:
        Model: An instance of the Model class.
    """
    return Model("openrouter/openai/gpt-4o-mini")

@pytest.mark.parametrize(
    "directory_paths, files_by_directory, record_output_flag, run_tests_flag, test_file_names, record_test_output_values, verbose, instructions, expected_script_outputs, expected_test_outputs, expected_exception",
    [
        # Test case 1: Basic usage without tests
        # - Runs the scripts in two directories and records their outputs without running any tests.
        (
            None,  # directory_paths
            [["file1.py", "file2.py"], ["file3.py"]],  # files_by_directory
            [True, True, True],  # record_output_flag
            None,  # run_tests_flag
            None,  # test_file_names
            None,  # record_test_output_values
            True,  # verbose
            [
                ["Modify file1.py to add a function `def add(a, b): return a + b` and include `if __name__ == '__main__': print('Result of add:', add(2, 3))`",
                 "Modify file2.py to add a function `def multiply(a, b): return a * b` and include `if __name__ == '__main__': print('Result of multiply:', multiply(4, 5))`"
                ],
                ["Modify file3.py to add a function `def subtract(a, b): return a - b` and include `if __name__ == '__main__': print('Result of subtract:', subtract(5, 3))`"],       
            ],  # instructions
            {
                'dir1/file1.py': {'stdout': 'Result of add: 5\n', 'stderr': ''},
                'dir1/file2.py': {'stdout': 'Result of multiply: 20\n', 'stderr': ''},
                'dir2/file3.py': {'stdout': 'Result of subtract: 2\n', 'stderr': ''}
            },  # expected_script_outputs
            {},  # expected_test_outputs
            None  # expected_exception
        ),
        # Test case 2: Basic usage without tests with wrong file3.py assertion value
        # - Runs the scripts in two directories and records their outputs without running any tests.
        (
            None,  # directory_paths
            [["file1.py", "file2.py"], ["file3.py"]],  # files_by_directory
            [True, True, True],  # record_output_flag
            None,  # run_tests_flag
            None,  # test_file_names
            None,  # record_test_output_values
            False,  # verbose
            [
                ["Modify file1.py to add a function `def add(a, b): return a + b` and include `if __name__ == '__main__': print('Result of add:', add(2, 3))`",
                 "Modify file2.py to add a function `def multiply(a, b): return a * b` and include `if __name__ == '__main__': print('Result of multiply:', multiply(4, 5))`"
                ],
                ["Modify file3.py to add a function `def subtract(a, b): return a - b` and include `if __name__ == '__main__': print('Result of subtract:', subtract(5, 3))`"],       
            ],  # instructions
            {
                'dir1/file1.py': {'stdout': 'Result of add: 5\n', 'stderr': ''},
                'dir1/file2.py': {'stdout': 'Result of multiply: 18\n', 'stderr': ''},
                'dir2/file3.py': {'stdout': 'Result of subtract: 2\n', 'stderr': ''}
            },  # expected_script_outputs
            {},  # expected_test_outputs
            AssertionError  # expected_exception
        ),
        # Test case 3: Running scripts and tests with output recording
        # - Runs the scripts and their corresponding tests, recording both the script and test outputs.
        (
            None,  # directory_paths
            [["file1.py", "test_file1.py"], ["file3.py", "test_file3.py"]],  # files_by_directory
            [True, False, True, False],  # record_output_flag
            [True, True],  # run_tests_flag
            [["test_file1.py"], ["test_file3.py"]],  # test_file_names
            [True, True],  # record_test_output_values
            True,  # verbose
            [
                [
                    "Modify file1.py to add a function `def adder(a, b): return a + b` and include `if __name__ == '__main__': print('Result of adder:', adder(2, 3))`",
                    "Modify test_file1.py to import `adder` from `file1`: `from file1 import adder` and add a pytest function to test `adder(a, b)` from file1.py with a simple assertion like `assert adder(2, 3) == 5`"
                    "Modify file2.py to add a function `def multiplier(a, b): return a * b` and include `if __name__ == '__main__': print('Result of multiplier:', multiplier(4, 3))`",
                    "Modify test_file2.py to import `multiplier` from `file2`:  `from file2 import multiplier` and add a pytest function to test `multiplier(a, b)` from file2.py with a simple assertion like `assert multiplier(4, 3) == 12`"
                ],
                [
                    "Modify file3.py to add a function `def subtracter(a, b): return a - b` and include `if __name__ == '__main__': print('Result of subtracter:', subtracter(5, 3))`",
                    "Modify test_file3.py to import `subtracter` from `file3`: `from file1 import subtracter` and add a pytest function to test `subtracter(a, b)` from file3.py with a simple assertion like `assert subtracter(5, 3) == 2`"
                ]
            ],  # instructions
            {
                'dir1/file1.py': {'stdout': 'Result of adder: 5\n', 'stderr': ''},
                'dir2/file3.py': {'stdout': 'Result of subtracter: 2\n', 'stderr': ''}
            },  # expected_script_outputs
            {
                'dir1/test_file1.py': {'stdout': '============================= test session starts =============================\nplatform win32 -- Python ...t1/test_file1.py . [100%]\n\n============================== 1 passed in 0.01s ===============================\n', 'stderr': ''},
                'dir2/test_file3.py': {'stdout': '============================= test session starts =============================\nplatform win32 -- Python ...t2/test_file3.py . [100%]\n\n============================== 1 passed in 0.01s ===============================\n', 'stderr': ''}
            },  # expected_test_outputs0
            None  # expected_exception
        ),
        # Test case 4: Running scripts without recording their output since bool lists like record_output_flag, run_tests_flag, record_test_output_values 
        # needs to be a list of bools 
        # - Runs the script without recording its output and does not run any tests.
        (
            None,  # directory_paths
            [["file1.py"]],  # files_by_directory
            [False],  # record_output_flag
            [False],  # run_tests_flag
            [["test_file1.py"]],  # test_file_names
            None,  # record_test_output_values
            False,  # verbose
            ["Modify file1.py to add a function `def added_function(): print('Added function to file1')`"],  # instructions
            {
                'dir1/file1.py': {'stdout': '', 'stderr': ''}
            },  # expected_script_outputs
            {},  # expected_test_outputs
            TypeError  # expected_exception
        ),
        # Test case 5: Running scripts without recording their outputs 
        # - Runs the script without recording its output and does not run any tests.
        (
            None,  # directory_paths
            [["file1.py"]],  # files_by_directory
            [False],  # record_output_flag
            [False],  # run_tests_flag
            [["test_file1.py"]],  # test_file_names
            [False],  # record_test_output_values
            False,  # verbose
            ["Modify file1.py to add a function `def added_function(): print('Added function to file1')`"],  # instructions
            {},  # expected_script_outputs
            {},  # expected_test_outputs
            None  # expected_exception
        ),
        # Test case 6: Running scripts with instructions, ValueError raise since run_tests_flag must be None when test_file_names is None
        # - Runs the script with specific instructions to modify the script file.
        (
            None,  # directory_paths
            [["file1.py"]],  # files_by_directory
            [True],  # record_output_flag
            [False],  # run_tests_flag
            None,  # test_file_names
            None,  # record_test_output_values
            False,  # verbose
            ["Add a function to file1.py `def added_function(): print('Added function to file1')`"],  # instructions
            {
                'dir1/file1.py': {'stdout': 'Hello from file1\nAdded function to file1\n', 'stderr': ''}
            },  # expected_script_outputs
            {},  # expected_test_outputs
            ValueError  # expected_exception
        ),
        # Test case 7: Running scripts with instructions, ValueError raise since record_test_output_values must be None when test_file_names is None
        # - Runs the script with specific instructions to modify the script file.
        (
            None,  # directory_paths
            [["file1.py"]],  # files_by_directory
            [True],  # record_output_flag
            None,  # run_tests_flag
            None,  # test_file_names
            [False],  # record_test_output_values
            False,  # verbose
            ["Add a function to file1.py `def added_function(): print('Added function to file1')`"],  # instructions
            {
                'dir1/file1.py': {'stdout': 'Hello from file1\nAdded function to file1\n', 'stderr': ''}
            },  # expected_script_outputs
            {},  # expected_test_outputs
            ValueError  # expected_exception
        ),
        # Test case 8: Running scripts with instructions, ValueError raise since record_test_output_values and run_tests_flag
        #  must be None when test_file_names is None
        # - Runs the script with specific instructions to modify the script file.
        (
            None,  # directory_paths
            [["file1.py"]],  # files_by_directory
            [True],  # record_output_flag
            [False],  # run_tests_flag
            None,  # test_file_names
            [False],  # record_test_output_values
            False,  # verbose
            ["Add a function to file1.py `def added_function(): print('Added function to file1')`"],  # instructions
            {
                'dir1/file1.py': {'stdout': 'Hello from file1\nAdded function to file1\n', 'stderr': ''}
            },  # expected_script_outputs
            {},  # expected_test_outputs
            ValueError  # expected_exception
        ),
        # Test case 9: Complex case with mixed settings
        # - Demonstrates a complex scenario where different settings are applied for recording output and running tests across directories.
        (
            None,  # directory_paths
            [["file1.py", "test_file1.py", "file2.py", "test_file2.py"],
              ["file3.py", "test_file3.py"]],  # files_by_directory
            [True, False, True, False, True, False],  # record_output_flag , no need to record outputs of pytest files 
            [True, False, True],  # run_tests_flag
            [["test_file1.py", "test_file2.py"], ["test_file3.py"]],  # test_file_names
            [True, True, False],  # record_test_output_values
            True,  # verbose
            [
                [
                    "Modify file1.py to add a function `def adder(a, b): return a + b` and include `if __name__ == '__main__': print('Result of adder:', adder(2, 3))`",
                    "Modify test_file1.py to import add from 'file1': `from file1 import adder` and adder a pytest function to test adder(a, b) from file1.py with a simple assertion like `assert adder(2, 3) == 5`",
                    "Modify file2.py to add a function `def multiplyer(a, b): return a * b` and include `if __name__ == '__main__': print('Result of multiplyer:', multiplyer(4, 5))`"
                    "Modify test_file2.py to import multiplyer from 'file2': `from file2 import multiplyer` and add a pytest function to test multiplyer(a, b) from file2.py with a simple assertion like `assert multiplyer(4, 5) == 20`"
  
                ],
                [
                    "Modify file3.py to add a function `def subtracter(a, b): return a - b` and include `if __name__ == '__main__': print('Result of subtracter:', subtracter(5, 3))`",
                    "Modify test_file3.py to import subtracter from 'file3': `from file3 import subtracter` and add a pytest function to test subtracter(a, b) from file3.py with a simple assertion like `assert subtracter(5, 3) == 2`"
                ]
            ],  # instructions
            {
                'dir1/file1.py': {'stdout': 'Result of adder: 5\n', 'stderr': ''},
                'dir1/file2.py': {'stdout': 'Result of multiplyer: 20\n', 'stderr': ''},
                'dir2/file3.py': {'stdout': 'Result of subtracter: 2\n', 'stderr': ''}
            },  # expected_script_outputs
            {
                'dir1/test_file1.py': {'stdout': '============================= test session starts =============================\nplatf...d in 0.05s ==============================\n', 'stderr': ''},
                'dir1/test_file2.py': {'stdout': '', 'stderr': ''},
                'dir2/test_file3.py': {'stdout': '', 'stderr': ''}
            },  # expected_test_outputs
            None  # expected_exception
        ),
        # Test case 10: Empty directory paths
        # - Tests the scenario where the directory paths list is empty, expecting a ValueError.
        (
            [],  # directory_paths
            [],  # files_by_directory
            [],  # record_output_flag
            [],  # run_tests_flag
            None,  # test_file_names
            None,  # record_test_output_values
            False,  # verbose
            None,  # instructions
            {},  # expected_script_outputs
            {},  # expected_test_outputs
            ValueError  # expected_exception
        ),
        # Test case 11: Invalid directory paths
        # - Tests the scenario where directory paths contain invalid paths (empty strings), expecting a ValueError.
        (
            ["", ""],  # directory_paths
            [["file1.py"], ["file3.py"]],  # files_by_directory
            [True, True],  # record_output_flag
            [False, False],  # run_tests_flag
            None,  # test_file_names
            None,  # record_test_output_values
            False,  # verbose
            None,  # instructions
            {},  # expected_script_outputs
            {},  # expected_test_outputs
            ValueError  # expected_exception
        ),
        # Test case 12: Non-boolean record_output_flag
        # - Tests the scenario where record_output_flag contains a non-boolean value, expecting a ValueError.
        (
            None,  # directory_paths
            [["file1.py"], ["file3.py"]],  # files_by_directory
            [True, "False"],  # record_output_flag
            [False, False],  # run_tests_flag
            None,  # test_file_names
            None,  # record_test_output_values
            False,  # verbose
            None,  # instructions
            {},  # expected_script_outputs
            {},  # expected_test_outputs
            ValueError  # expected_exception
        ),
        # Test case 13: Mismatch in files_by_directory and record_output_flag lengths
        # - Tests the scenario where the lengths of files_by_directory and record_output_flag do not match, expecting a ValueError.
        (
            None,  # directory_paths
            [["file1.py"], ["file3.py"]],  # files_by_directory
            [True],  # record_output_flag
            [False, False],  # run_tests_flag
            None,  # test_file_names
            None,  # record_test_output_values
            False,  # verbose
            None,  # instructions
            {},  # expected_script_outputs
            {},  # expected_test_outputs
            ValueError  # expected_exception
        ),
        # Test case 14: Mismatch in test_file_names, run_tests_flag, and record_test_output_values lengths
        # - Tests the scenario where the lengths of test_file_names, run_tests_flag, and record_test_output_values do not match, expecting a ValueError.
        (
            None,  # directory_paths
            [["file1.py"], ["file3.py"]],  # files_by_directory
            [True, True],  # record_output_flag
            [True, False],  # run_tests_flag
            [["test_file1.py"], ["test_file3.py"]],  # test_file_names
            [True],  # record_test_output_values
            False,  # verbose
            None,  # instructions
            {},  # expected_script_outputs
            {},  # expected_test_outputs
            ValueError  # expected_exception
        ),
        # Test case 15: Invalid list structure or lengths
        # - Tests the scenario where the structure or lengths of the input lists are invalid, expecting a ValueError.
        (
            None,  # directory_paths
            ["file1.py"],  # files_by_directory
            [True],  # record_output_flag
            [False],  # run_tests_flag
            [["test_file1.py"]],  # test_file_names
            [False],  # record_test_output_values
            False,  # verbose
            None,  # instructions
            {},  # expected_script_outputs
            {},  # expected_test_outputs
            ValueError  # expected_exception
        ),
        # Test case 16: Nested empty lists
        # - Tests the scenario where files_by_directory or test_file_names contain nested empty lists, expecting a ValueError.
        (
            None,  # directory_paths
            [[]],  # files_by_directory
            [True],  # record_output_flag
            [False],  # run_tests_flag
            [[]],  # test_file_names
            [False],  # record_test_output_values
            False,  # verbose
            None,  # instructions
            {},  # expected_script_outputs
            {},  # expected_test_outputs
            ValueError  # expected_exception
        )
    ]
)
def test_execute(directory_paths, files_by_directory, model, record_output_flag, run_tests_flag, test_file_names, 
                record_test_output_values, verbose, instructions, expected_script_outputs, expected_test_outputs,
                expected_exception, temp_directory):
    """
    Test function for the execute function.

    This test covers various scenarios, including normal operations, edge cases, and validation checks.

    Args:
        directory_paths (List[str]): The directories to process.
        files_by_directory (List[List[str]]): The names of the files to process for each directory.
        model (Any): The model to use for processing.
        record_output_flag (List[bool]): Flags indicating whether to record the script output for each directory.
        run_tests_flag (List[bool]): Flags indicating whether to run the test files for each directory.
        test_file_names (List[List[str]], optional): The names of the test files to run for each directory. Defaults to None.
        record_test_output_values (List[bool], optional): Flags indicating whether to record the test output for each directory. Defaults to None.
        verbose (bool): Whether to print the outputs to the console.
        instructions (List[str]): The list of instructions to run on the files.
        expected_script_outputs (Dict[str, Any]): Expected script outputs.
        expected_test_outputs (Dict[str, Any]): Expected test outputs.
        expected_exception (Optional[Type[Exception]]): The type of exception expected to be raised. Defaults to None.
        temp_directory (Fixture): Fixture for the temporary directory structure.
    """
    # Use the fixture values as defaults if the parameterized values are None
    if directory_paths is None:
        directory_paths = temp_directory['directory_paths']
        # Example: directory_paths = None, temp_directory['directory_paths'] = ['path1', 'path2'] -> directory_paths = ['path1', 'path2']
    
    # Introduce a delay of one second between each parameterized test case to avoid API rate limit issues
    time.sleep(1)
    
    try:
        # Run the execute function and capture the outputs
        outputs = execute(directory_paths, files_by_directory, model, record_output_flag, run_tests_flag, test_file_names, record_test_output_values, verbose, instructions)
        # Example: execute(...) -> {"script_outputs": ["output1", "output2"], "test_outputs": ["test_output1", "test_output2"]}
    
        # If an exception was expected but not raised, this is a failure
        if expected_exception:
            raise AssertionError(f"Expected exception {expected_exception.__name__} was not raised.")
            # Example: expected_exception = ValueError, no exception raised -> AssertionError("Expected exception ValueError was not raised.")
    
        # Unpack the dictionary of outputs into script_outputs and test_outputs
        script_outputs, test_outputs = outputs["script_outputs"], outputs["test_outputs"]
        # Example: outputs = {"script_outputs": ["output1", "output2"], "test_outputs": ["test_output1", "test_output2"]} -> script_outputs = ["output1", "output2"], test_outputs = ["test_output1", "test_output2"]
    
        # Adjust script outputs without masking directory paths
        adjusted_script_outputs = adjust_outputs(script_outputs)
        # Example: script_outputs = ["output1", "output2"] -> adjusted_script_outputs = ["adjusted_output1", "adjusted_output2"]
    
        # Adjust test outputs with masking directory paths
        adjusted_test_outputs = adjust_outputs(test_outputs)
        # Example: test_outputs = ["test_output1", "test_output2"] -> adjusted_test_outputs = ["adjusted_test_output1", "adjusted_test_output2"]
    
        # Assert script outputs
        assert assert_outputs(adjusted_script_outputs, expected_script_outputs), "Script output assertion failed."
        # Example: adjusted_script_outputs = ["adjusted_output1", "adjusted_output2"], expected_script_outputs = ["expected_output1", "expected_output2"] -> assert_outputs(...) = True
    
        # Assert test outputs
        assert assert_outputs(adjusted_test_outputs, expected_test_outputs, is_test=True), "Test output assertion failed."
        # Example: adjusted_test_outputs = ["adjusted_test_output1", "adjusted_test_output2"], expected_test_outputs = ["expected_test_output1", "expected_test_output2"] -> assert_outputs(...) = True
    
    except Exception as e:
        # If an exception is raised, check if it matches the expected_exception
        if expected_exception and isinstance(e, expected_exception):
            print(f"Expected exception {expected_exception.__name__} occurred: {e}")
            assert True  # The test passes since the correct exception was raised.
            # Example: expected_exception = ValueError, e = ValueError("error message") -> print("Expected exception ValueError occurred: error message"), assert True
        else:
            # If a different exception occurred than expected, or no exception was expected, raise it to indicate a test failure
            raise
            # Example: expected_exception = ValueError, e = TypeError("error message") -> raise TypeError("error message")

# Run the tests
if __name__ == "__main__":
    pytest.main()