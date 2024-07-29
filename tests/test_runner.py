import pytest
from pathlib import Path
from Aider_Project.runner import run_script_and_record_output

"""
Proposed Unit Tests:

1. Test with a valid script and no test files: Ensure the function correctly runs a valid script and captures its output.
2. Test with a valid script and valid test files: Verify that the function correctly runs the script and test files, capturing their outputs.
3. Test with record_output set to False: Ensure the function runs the script without capturing its output.
4. Test with record_test_output set to False: Ensure the function runs the test files without capturing their outputs.
5. Test with an invalid script path: Verify that the function handles invalid script paths gracefully.
6. Test with an invalid test file path: Verify that the function handles invalid test file paths gracefully.

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
    "script_path, test_file_paths, record_output, record_test_output, run_tests_values, expected_exception, expected_script_stdout, expected_test_stdout",
    [
        # Valid script and no test files
        ("valid", None, True, True, True, None, "Hello from script", None),
        # Valid script and valid test files
        ("valid", "valid", True, True, True, None, "Hello from script", "1 passed"),
        # Record output set to False
        ("valid", "valid", False, True, True, None, "", "1 passed"),
        # Record test output set to False
        ("valid", "valid", True, False, True, None, "Hello from script", ""),
        # Invalid script path
        ("invalid", "valid", True, True, True, Exception, "", ""),
        # Invalid test file path
        ("valid", "invalid", True, True, True, Exception, "Hello from script", ""),
        # Valid script without running tests
        ("valid", "valid", True, True, False, None, "Hello from script", None),
    ]
)
def test_run_script_and_record_output(
    temp_script, temp_test_file, script_path, test_file_paths, record_output, record_test_output, run_tests_values, expected_exception, expected_script_stdout, expected_test_stdout):
    """Test running a script and optionally recording the output with different combinations of flags and paths."""
    
    # Determine the actual paths for the script and test files
    script_file_path = str(temp_script) if script_path == "valid" else "invalid_script_path.py"
    test_file_list = [str(temp_test_file)] if test_file_paths == "valid" else ["invalid_test_file_path.py"] if test_file_paths == "invalid" else None

    # Run the test and capture the outputs
    if expected_exception:
        with pytest.raises(expected_exception):
            run_script_and_record_output(
                script_path=script_file_path,
                record_output=record_output,
                test_file_paths=test_file_list,
                record_test_output=record_test_output,
                run_tests_values=run_tests_values
            )
    else:
        script_output, test_outputs = run_script_and_record_output(
            script_path=script_file_path,
            record_output=record_output,
            test_file_paths=test_file_list,
            record_test_output=record_test_output,
            run_tests_values=run_tests_values
        )

        # Validate script output
        if record_output:
            assert expected_script_stdout in script_output["stdout"]
        else:
            assert script_output == {"stdout": "", "stderr": ""}
        
        # Validate test output
        if run_tests_values:
            if record_test_output and test_file_paths == "valid":
                assert expected_test_stdout in test_outputs[str(temp_test_file)]["stdout"]
            else:
                # Ensure the test file path exists in the test_outputs dictionary
                assert test_outputs.get(str(temp_test_file), {"stdout": "", "stderr": ""}) == {"stdout": "", "stderr": ""}
        else:
            assert test_outputs == {}

# Run the tests
if __name__ == "__main__":
    pytest.main()
