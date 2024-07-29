import subprocess
from typing import List, Dict, Optional, Tuple

def run_script_and_record_output(script_path: str, 
                                record_output: bool = True, 
                                test_file_paths: Optional[List[str]] = None,
                                record_test_output: bool = True,
                                run_tests_values: bool = True) -> Tuple[Dict[str, str], Dict[str, Dict[str, str]]]:
    """
    Run a script and optionally record the output. Optionally, run multiple test files and record their output.

    Args:
        script_path (str): The path to the script to run.
        record_output (bool): Whether to record the script output. Defaults to True.
        test_file_paths (List[str], optional): The paths to the test files to run. Defaults to None.
        record_test_output (bool): Whether to record the test files output. Defaults to True.
        run_tests_values (bool): Whether to run the test files. Defaults to True.

    Returns:
        Tuple[Dict[str, str], Dict[str, Dict[str, str]]]: A tuple containing dictionaries of script and test outputs.

    Raises:
        Exception: If there is an error running the script or test files.

    Example Usage:
        >>> # Running a script and recording its output, as well as running test files and recording their outputs
        >>> script_output, test_outputs = run_script_and_record_output("example_script.py", record_output=True, test_file_paths=["test_example.py"], record_test_output=True, run_tests_values=True)
        >>> print(script_output)
        {'stdout': 'Script started\\nProcessing data...\\nScript finished successfully.\\n', 'stderr': ''}
        >>> print(test_outputs)
        {'test_example.py': {'stdout': '============================= test session starts =============================\\ncollected 2 items\\n\\ntest_example.py::test_function PASSED\\ntest_example.py::test_another_function PASSED\\n\\n============================== 2 passed in 0.01s ===============================\\n', 'stderr': ''}}

        >>> # Running a script without recording its output and not running any tests
        >>> script_output, test_outputs = run_script_and_record_output("example_script.py", record_output=False, run_tests_values=False)
        >>> print(script_output)
        {'stdout': '', 'stderr': ''}
        >>> print(test_outputs)
        {}

        >>> # Running a script and recording its output, as well as running test files and recording their outputs
        >>> script_output, test_outputs = run_script_and_record_output("example_script.py", record_output=True, test_file_paths=["test_example.py"], record_test_output=True, run_tests_values=True)
        >>> print(script_output)
        {'stdout': 'Script started\\nProcessing data...\\nScript finished successfully.\\n', 'stderr': ''}
        >>> print(test_outputs)
        {'test_example.py': {'stdout': '============================= test session starts =============================\\ncollected 2 items\\n\\ntest_example.py::test_function PASSED\\ntest_example.py::test_another_function PASSED\\n\\n============================== 2 passed in 0.01s ===============================\\n', 'stderr': ''}}

        >>> # Running a script, recording its output, and running test files without recording their outputs
        >>> script_output, test_outputs = run_script_and_record_output("example_script.py", record_output=True, test_file_paths=["test_example.py"], record_test_output=False, run_tests_values=True)
        >>> print(script_output)
        {'stdout': 'Script started\\nProcessing data...\\nScript finished successfully.\\n', 'stderr': ''}
        >>> print(test_outputs)
        {'test_example.py': {'stdout': '', 'stderr': ''}}

        >>> # Running a script and recording its output, but not running any tests
        >>> script_output, test_outputs = run_script_and_record_output("example_script.py", record_output=True, test_file_paths=["test_example.py"], run_tests_values=False)
        >>> print(script_output)
        {'stdout': 'Script started\\nProcessing data...\\nScript finished successfully.\\n', 'stderr': ''}
        >>> print(test_outputs)
        {}
    """
    # Initialize a dictionary to store the main script's output
    script_output = {"stdout": "", "stderr": ""}
    # Initialize a dictionary to store outputs from test files
    test_outputs = {}
    
    try:
        # If we want to record the script's output
        if record_output:
            # Run the script using subprocess, capturing its output
            script_result = subprocess.run(["python", script_path], capture_output=True, text=True, check=True)
            # Store the script's standard output and error messages
            script_output["stdout"] = script_result.stdout
            script_output["stderr"] = script_result.stderr
        else:
            # If not recording output, just run the script without capturing output
            subprocess.run(["python", script_path], check=True)
    
        # If there are test files to run and run_tests_values is True
        if test_file_paths and run_tests_values:
            # Loop through each test file path
            for test_file_path in test_file_paths:
                # If we want to record the test's output
                if record_test_output:
                    # Run the test using pytest, capturing its output
                    test_result = subprocess.run(["pytest", test_file_path], capture_output=True, text=True, check=True)
                    # Store the test's standard output and error messages
                    test_outputs[test_file_path] = {
                        "stdout": test_result.stdout,
                        "stderr": test_result.stderr
                    }
                else:
                    # If not recording output, just run the test without capturing output
                    subprocess.run(["pytest", test_file_path], check=True)
    
    except subprocess.CalledProcessError as e:
        # If an error occurs, raise an exception with the error message
        raise Exception(f"Error running the script or test files: {e}")
    
    # Return the script's output and the test outputs
    return script_output, test_outputs
