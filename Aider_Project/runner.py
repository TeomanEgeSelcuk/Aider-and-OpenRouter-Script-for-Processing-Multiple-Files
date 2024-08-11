import subprocess
from typing import Dict, Optional, Tuple

def run_script_and_record_output(script_path: Optional[str] = None, 
                                 record_output: bool = False, 
                                 test_file_path: Optional[str] = None,
                                 record_test_output: bool = False,
                                 run_tests_values: bool = False) -> Tuple[Dict[str, str], Dict[str, Dict[str, str]]]:
    """
    Run a script and optionally record the output. Optionally, run a test file and record its output.

    Args:
        script_path (str, optional): The path to the script to run. Defaults to None.
        record_output (bool): Whether to record the script output. Defaults to False.
        test_file_path (str, optional): The path to the test file to run. Defaults to None.
        record_test_output (bool): Whether to record the test file output. Defaults to False.
        run_tests_values (bool): Whether to run the test file. Defaults to False.

    Returns:
        Tuple[Dict[str, str], Dict[str, Dict[str, str]]]: A tuple containing dictionaries of script and test outputs.

    Raises:
        Exception: If there is an error running the script or test file.

    Example Usage:
        >>> # Running a script and recording its output, as well as running a test file and recording its output
        >>> script_output, test_output = run_script_and_record_output("example_script.py", record_output=True, test_file_path="test_example.py", record_test_output=True, run_tests_values=True)
        >>> print(script_output)
        {'stdout': 'Script started\\nProcessing data...\\nScript finished successfully.\\n', 'stderr': ''}
        >>> print(test_output)
        {'test_example.py': {'stdout': '============================= test session starts =============================\\ncollected 2 items\\n\\ntest_example.py::test_function PASSED\\ntest_example.py::test_another_function PASSED\\n\\n============================== 2 passed in 0.01s ===============================\\n', 'stderr': ''}}

        >>> # Running a script without recording its output and not running any tests
        >>> script_output, test_output = run_script_and_record_output("example_script.py", record_output=False, run_tests_values=False)
        >>> print(script_output)
        {'stdout': '', 'stderr': ''}
        >>> print(test_output)
        {}

        >>> # Running a script and recording its output, as well as running a test file and recording its output
        >>> script_output, test_output = run_script_and_record_output("example_script.py", record_output=True, test_file_path="test_example.py", record_test_output=True, run_tests_values=True)
        >>> print(script_output)
        {'stdout': 'Script started\\nProcessing data...\\nScript finished successfully.\\n', 'stderr': ''}
        >>> print(test_output)
        {'test_example.py': {'stdout': '============================= test session starts =============================\\ncollected 2 items\\n\\ntest_example.py::test_function PASSED\\ntest_example.py::test_another_function PASSED\\n\\n============================== 2 passed in 0.01s ===============================\\n', 'stderr': ''}}

        >>> # Running a script, recording its output, and running a test file without recording its output
        >>> script_output, test_output = run_script_and_record_output("example_script.py", record_output=True, test_file_path="test_example.py", record_test_output=False, run_tests_values=True)
        >>> print(script_output)
        {'stdout': 'Script started\\nProcessing data...\\nScript finished successfully.\\n', 'stderr': ''}
        >>> print(test_output)
        {'test_example.py': {'stdout': '', 'stderr': ''}}

        >>> # Running a script and recording its output, but not running any tests
        >>> script_output, test_output = run_script_and_record_output("example_script.py", record_output=True, test_file_path="test_example.py", run_tests_values=False)
        >>> print(script_output)
        {'stdout': 'Script started\\nProcessing data...\\nScript finished successfully.\\n', 'stderr': ''}
        >>> print(test_output)
        {}

        >>> # Running a script and recording its output, but with script_path set to None
        >>> script_output, test_output = run_script_and_record_output(script_path=None, record_output=True, run_tests_values=False)
        >>> print(script_output)
        {'stdout': '', 'stderr': ''}
        >>> print(test_output)
        {}
    """
    # Initialize a dictionary to store the main script's output
    script_output = {"stdout": "", "stderr": ""}
    # Initialize a dictionary to store outputs from the test file
    test_outputs = {"stdout": "", "stderr": ""}
    
    try:
        # If script_path is not None and we want to record the script's output
        if script_path and record_output:
            # Run the script using subprocess, capturing its output
            script_result = subprocess.run(["python", script_path], capture_output=True, text=True, check=True)
            # Store the script's standard output and error messages
            script_output["stdout"] = script_result.stdout
            script_output["stderr"] = script_result.stderr
        elif script_path:
            # If not recording output, just run the script without capturing output
            subprocess.run(["python", script_path], check=True)
    
        # If there is a test file to run and run_tests_values is True
        if test_file_path and run_tests_values:
            test_result = subprocess.run(["pytest", test_file_path], capture_output=True, text=True, check=True)
            # If we want to record the test's output
            if record_test_output:
                # Run the test using pytest, capturing its output
                # Store the test's standard output and error messages
                test_outputs["stdout"] = test_result.stdout
                test_outputs["stderr"] = test_result.stderr
            else:
                # If not recording output, just run the test without capturing output
                subprocess.run(["pytest", test_file_path], check=True)
    
    except subprocess.CalledProcessError as e:
        # If an error occurs, raise an exception with the error message
        raise Exception(f"Error running the script or test file: {e}")
    
    # Return the script's output and the test outputs
    return script_output, test_outputs
