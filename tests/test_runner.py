import pytest
from Aider_Project.runner import run_script_and_record_output

"""
Proposed Unit Tests:

1. Test with a valid script and no test files: Ensure the function correctly runs a valid script and captures its output.
2. Test with a valid script and valid test files: Verify that the function correctly runs the script and test files, capturing their outputs.
3. Test with record_output set to False: Ensure the function runs the script without capturing its output.
4. Test with record_test_output set to False: Ensure the function runs the test files without capturing their outputs.
5. Test with an invalid script path: Verify that the function handles invalid script paths gracefully.
6. Test with an invalid test file path: Verify that the function handles invalid test file paths gracefully.
7. Test with script_path set to None: Ensure the function handles None script path correctly without running the script.

Explanation:
============

Fixtures:
---------
- temp_script: Creates a temporary script file for testing.
- temp_test_file: Creates a temporary test file for testing.

Parameterization:
-----------------
- Tests are parameterized to run with different values for record_output, record_test_output, and run_tests_values flags, as well as valid and invalid paths.

Tests:
------
1. test_run_script_and_record_output: Tests running a script and optionally recording the output with different combinations of flags and paths.
"""

# Define a fixture to create a temporary script file for testing
@pytest.fixture
def temp_script(tmp_path):
    """Fixture to create a temporary script file."""
    # Create a path for the temporary script
    script_path = tmp_path / "temp_script.py"
    # Write a simple print statement to the temporary script file
    script_path.write_text("print('Hello from script')")
    # Return the path of the temporary script file
    return script_path

# Define a fixture to create a temporary test file for testing
@pytest.fixture
def temp_test_file(tmp_path):
    """Fixture to create a temporary test file."""
    # Create a path for the temporary test file
    test_file_path = tmp_path / "test_temp_script.py"
    # Write a simple test case to the temporary test file
    test_file_path.write_text("""
import pytest

def test_example():
    assert 1 == 1
""")
    # Return the path of the temporary test file
    return test_file_path

# Test running a script and optionally recording its output with different combinations of flags and paths
@pytest.mark.parametrize(
    "script_path, test_file_path, record_output, record_test_output, run_tests_values, expected_exception, expected_script_stdout, expected_test_stdout",
    [
        # Test Case 1: Valid script and no test files
        # - Runs a valid script and records its output.
        # - No test files are specified.
        # - Expects "Hello from script" in script output and no test output.
        ("valid", None, True, True, True, None, "Hello from script", None),
        
        # Test Case 2: Valid script and valid test files
        # - Runs a valid script and valid test files.
        # - Records output for both script and test files.
        # - Expects "Hello from script" in script output and "1 passed" in test output.
        ("valid", "valid", True, True, True, None, "Hello from script", "1 passed"),
        
        # Test Case 3: Record script output set to False
        # - Runs a valid script and valid test files.
        # - Does not record the script output but records the test output.
        # - Expects an empty script output and "1 passed" in test output.
        ("valid", "valid", False, True, True, None, "", "1 passed"),
        
        # Test Case 4: Record test output set to False
        # - Runs a valid script and valid test files.
        # - Records the script output but does not record the test output.
        ("valid", "valid", True, False, True, None, "Hello from script", ""),
        
        # Test Case 5: Invalid script path
        # - Attempts to run an invalid script path.
        # - Expects an exception to be raised and no output recorded.
        ("invalid", "valid", True, True, True, Exception, "", ""),
        
        # Test Case 6: Invalid test file path
        # - Runs a valid script and attempts to run an invalid test file path.
        # - Expects an exception to be raised for the test file and no test output.
        ("valid", "invalid", True, True, True, Exception, "Hello from script", ""),
        
        # Test Case 7: Valid script without running tests
        ("valid", "valid", True, True, False, None, "Hello from script", None),
        
        # Test Case 8: Script path set to None and no test files
        # - Does not run any script but attempts to run tests.
        # - Expects no script output and no test output.
        (None, None, True, True, True, None, "", None),
        
        # Test Case 9: Script path set to None with valid test files
        # - Does not run any script but runs valid test files.
        # - Expects no script output and "1 passed" in test output.
        (None, "valid", True, True, True, None, "", "1 passed"),
        
        # Test Case 10: Script path set to None and record_test_output set to False
        # - Does not run any script but runs valid test files.
        # - Does not record the test output.
        # - Expects no script output and no test output.
        (None, "valid", True, False, True, None, "", ""),
    ]
)
def test_run_script_and_record_output(
    temp_script, temp_test_file, script_path, test_file_path, record_output, record_test_output, run_tests_values, expected_exception, expected_script_stdout, expected_test_stdout):
    """Test running a script and optionally recording the output with different combinations of flags and paths."""
    
    # Determine the actual path for the script:
    # - If script_path is "valid", use the path of the temporary script (temp_script).
    #   Example: "valid" -> str(temp_script)
    # - If script_path is "invalid", use a deliberately invalid path ("invalid_script_path.py").
    #   Example: "invalid" -> "invalid_script_path.py"
    # - If script_path is None, set the path to None.
    #   Example: None -> None
    script_file_path = str(temp_script) if script_path == "valid" else "invalid_script_path.py" if script_path == "invalid" else None
    
    # Determine the actual path for the test file:
    # - If test_file_path is "valid", use the path of the temporary test file (temp_test_file).
    #   Example: "valid" -> str(temp_test_file)
    # - If test_file_path is "invalid", use a deliberately invalid path ("invalid_test_file_path.py").
    #   Example: "invalid" -> "invalid_test_file_path.py"
    # - If test_file_path is None, set the path to None.
    #   Example: None -> None
    test_file_path = str(temp_test_file) if test_file_path == "valid" else "invalid_test_file_path.py" if test_file_path == "invalid" else None
    
    # Run the function and capture the outputs:
    if expected_exception:
        # If an exception is expected, use pytest.raises to assert that the expected exception is raised.
        with pytest.raises(expected_exception):
            run_script_and_record_output(
                script_path=script_file_path,           # Path to the script to run
                record_output=record_output,            # Whether to record the script output
                test_file_path=test_file_path,          # Path to the test file to run
                record_test_output=record_test_output,  # Whether to record the test file output
                run_tests_values=run_tests_values       # Whether to run the test file
            )
    else:
        # If no exception is expected, run the function and capture its outputs.
        script_output, test_outputs = run_script_and_record_output(
            script_path=script_file_path,           # Path to the script to run
            record_output=record_output,            # Whether to record the script output
            test_file_path=test_file_path,          # Path to the test file to run
            record_test_output=record_test_output,  # Whether to record the test file output
            run_tests_values=run_tests_values       # Whether to run the test file
        )
    
        # Validate the script output:
        if record_output:
            # If recording the script output, check that the expected output is in the script's stdout.
            # Example: expected_script_stdout = "Hello, World!" -> script_output["stdout"] contains "Hello, World!"
            assert expected_script_stdout in script_output["stdout"]
        else:
            # If not recording the script output, assert that the script output should be empty.
            # Example: record_output = False -> script_output == {"stdout": "", "stderr": ""}
            assert script_output == {"stdout": "", "stderr": ""}
        
        # Validate the test output
        if run_tests_values:
            if record_test_output and test_file_path == str(temp_test_file):
                # If recording the test output and the test file path is valid, check that the expected output is in the test's stdout
                # Example: expected_test_stdout = "Test Passed" -> test_outputs["stdout"] contains "Test Passed"
                assert expected_test_stdout in test_outputs["stdout"]
            else:
                # Ensure the test file path exists in the test_outputs dictionary
                # and the output should be empty or match the expected output for invalid paths.
                # Example: test_file_path = "invalid_test_file_path.py" -> test_outputs.get(test_file_path, {"stdout": "", "stderr": ""}) == {"stdout": "", "stderr": ""}
                assert test_outputs.get(test_file_path, {"stdout": "", "stderr": ""}) == {"stdout": "", "stderr": ""}
        else:
            # If not running tests, the test outputs should be empty.
            # Example: run_tests_values = False -> test_outputs == {"stdout": "", "stderr": ""}
            assert test_outputs == {"stdout": "", "stderr": ""}

# Run the tests
if __name__ == "__main__":
    pytest.main()
