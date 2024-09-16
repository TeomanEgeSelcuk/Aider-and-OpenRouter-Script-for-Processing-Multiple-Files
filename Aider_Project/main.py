from pathlib import Path
from typing import  List, Optional, Dict, Any, Tuple
from aider.coders import Coder
# from aider.models import Model
from aider.io import InputOutput
import os

# Modules within this project 
# from Aider_Project.utils import get_openrouter_api_key, list_files
from Aider_Project.runner import run_script_and_record_output 
from Aider_Project.execute_helper import is_nested_empty_list, validate_lengths, check_nested_lists_and_flat_list, organize_flags, get_flag_value

'''
main.py: Contains the execute function and the entry point.
utils.py: Contains utility functions such as get_openrouter_api_key and list_files.
runner.py: Contains the run_script_and_record_output function.
execute_helper.py: Contains helper functions for the execute function: is_nested_empty_list, validate_lengths, check_nested_lists_and_flat_list
'''

def aider_runner(directory: str, files_by_directory: List[str], model: Any, instructions: List[str]) -> None:
    """
    Processes a single directory and its corresponding files by converting file names to absolute paths,
    creating a Coder object, setting the working directory, disabling auto commits, and running the prompts on the files.
    It makes edits to the chosen files specified within the instructions using Aider and the chosen OpenRouter LLM model.
    
    Args:
        directory (str): The directory to process.
        files_by_directory (List[str]): The names of the files to process for the directory.
        model (Any): The model to use for processing.
        instructions (List[str]): The list of instructions to run on the files.
    """

    # Check if the directory exists
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"Directory '{directory}' does not exist.")
    
    # Convert file names to absolute paths
    fnames = [str(Path(directory) / file_name) for file_name in files_by_directory]
    
    # Check if fnames is empty
    if not fnames:
        raise ValueError("No files provided to process.")
    
    # Check if each file exists
    for fname in fnames:
        if not os.path.isfile(fname):
            raise FileNotFoundError(f"File '{fname}' does not exist.")
    
    # Create InputOutput object with yes set to True
    # This means that any prompts asking for user confirmation will automatically be answered 'yes'
    # It's useful for automated or batch processing where you don't want to manually confirm every action
    io = InputOutput(yes=True)
    
    # Create a Coder object and set the working directory
    coder = Coder.create(main_model=model, fnames=fnames, io=io)
    coder.root = Path(directory).resolve()  # Set the working directory
    
    # Disable Git functionality
    coder.repo = None  # Disable the Git repository
    coder.dirty_commits = False  # Disable dirty commits
    coder.check_for_dirty_commit = lambda path: None  # Disable checking for dirty commits
    coder.allowed_to_edit = lambda path: True  # Always allow editing without Git checks
    coder.auto_commit = lambda edited, context=None: None  # Accepts context but does nothing


    # Run the prompts on the files
    for instruction in instructions:
        # Execute each instruction on the files
        coder.run(instruction)

# Combines everything and runs the script as the main starting point
def execute(directory_paths: List[str], 
            files_by_directory: List[List[str]], 
            model: Any, 
            record_output_flag: List[bool], 
            run_tests_flag: Optional[List[bool]] = None,
            test_file_names: Optional[List[List[str]]] = None,
            record_test_output_values: Optional[List[bool]] = None, 
            verbose: bool = False, 
            instructions: List[str] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    execute function to process the files in multiple directories.

    Args:
        directory_paths (List[str]): The directories to process.
        files_by_directory (List[List[str]]): The names of the files to process for each directory.
        model (Any): The model to use for processing.
        record_output_flag (List[bool]): Flags indicating whether to record the script output for each directory.
        run_tests_flag (List[bool]): Flags indicating whether to run the test files for each directory.
        test_file_names (List[List[str]], optional): The names of the test files to run for each directory. Defaults to None.
        record_test_output_values (List[bool], optional): Flags indicating whether to record the test output for each directory. Defaults to None.
        verbose (bool): Whether to print the outputs to the console. Defaults to False.
        instructions (List[str]): The list of instructions to run on the files. Defaults to None.

    Raises:
        Exception: If there is an error in the processing or if model is not provided.

    Returns:
        Tuple[Dict[str, Any], Dict[str, Any]]: A tuple containing dictionaries of script and test outputs.

    Example Usage:
        1. Basic usage without tests:
        >>> directory_paths = ["dir1", "dir2"]
        >>> files_by_directory = [["file1.py", "file2.py"], ["file3.py"]]
        >>> model = Model("some-model")
        >>> record_output_flag = [True, True]
        >>> run_tests_flag = [False, False]
        >>> execute(directory_paths, files_by_directory, model, record_output_flag, run_tests_flag)
        # This example runs the scripts in two directories and records their outputs without running any tests.
        # Outputs:
        ({'dir1-file1.py': {'stdout': 'Output from file1.py', 'stderr': ''}, 'dir1-file2.py': {'stdout': 'Output from file2.py', 'stderr': ''}, 'dir2-file3.py': {'stdout': 'Output from file3.py', 'stderr': ''}}, {})

        2. Running scripts and tests with output recording:
        >>> directory_paths = ["dir1", "dir2"]
        >>> files_by_directory = [["file1.py"], ["file3.py"]]
        >>> model = Model("some-model")
        >>> record_output_flag = [True, True]
        >>> run_tests_flag = [True, True]
        >>> test_file_names = [["test_file1.py"], ["test_file3.py"]]
        >>> record_test_output_values = [True, True]
        >>> execute(directory_paths, files_by_directory, model, record_output_flag, run_tests_flag, test_file_names, record_test_output_values)
        # This example runs the scripts and their corresponding tests, recording both the script and test outputs.
        # Outputs:
        ({'dir1-file1.py': {'stdout': 'Output from file1.py', 'stderr': ''}, 'dir2-file3.py': {'stdout': 'Output from file3.py', 'stderr': ''}}, {'dir1-test_file1.py': {'stdout': 'Output from test_file1.py', 'stderr': ''}, 'dir2-test_file3.py': {'stdout': 'Output from test_file3.py', 'stderr': ''}})

        3. Running scripts without recording their output:
        >>> directory_paths = ["dir1"]
        >>> files_by_directory = [["file1.py"]]
        >>> model = Model("some-model")
        >>> record_output_flag = [False]
        >>> run_tests_flag = [False]
        >>> execute(directory_paths, files_by_directory, model, record_output_flag, run_tests_flag)
        # This example runs the script without recording its output and does not run any tests.
        # Outputs:
        ({'dir1-file1.py': {'stdout': '', 'stderr': ''}}, {})

        4. Running scripts with instructions:
        >>> directory_paths = ["dir1"]
        >>> files_by_directory = [["file1.py"]]
        >>> model = Model("some-model")
        >>> record_output_flag = [True]
        >>> run_tests_flag = [False]
        >>> instructions = ["Add a function to file1.py"]
        >>> execute(directory_paths, files_by_directory, model, record_output_flag, run_tests_flag, instructions=instructions)
        # This example runs the script with specific instructions to modify the script file.
        # Outputs:
        ({'dir1-file1.py': {'stdout': 'Output from file1.py with added function', 'stderr': ''}}, {})

        5. Complex case with mixed settings:
        >>> directory_paths = ["dir1", "dir2"]
        >>> files_by_directory = [["file1.py", "file2.py"], ["file3.py"]]
        >>> model = Model("some-model")
        >>> record_output_flag = [True, False]
        >>> run_tests_flag = [True, False]
        >>> test_file_names = [["test_file1.py", "test_file2.py"], []]
        >>> record_test_output_values = [True, False]
        >>> execute(directory_paths, files_by_directory, model, record_output_flag, run_tests_flag, test_file_names, record_test_output_values)
        # This example demonstrates a complex scenario where different settings are applied for recording output and running tests across directories.
        # Outputs:
        ({'dir1-file1.py': {'stdout': 'Output from file1.py', 'stderr': ''}, 'dir1-file2.py': {'stdout': '', 'stderr': ''}, 'dir2-file3.py': {'stdout': '', 'stderr': ''}}, {'dir1-test_file1.py': {'stdout': 'Output from test_file1.py', 'stderr': ''}, 'dir1-test_file2.py': {'stdout': 'Output from test_file2.py', 'stderr': ''}})
    """
    try:
        # Check that directory_paths is not empty and contains valid paths
        if not directory_paths or not all(directory_paths):
            # This check ensures that the directory_paths list is not empty and that each path in the list is valid (i.e., not an empty string).
            raise ValueError("directory_paths cannot be empty and must contain valid paths")

        # Ensure record_output_flag contains only boolean values
        if not all(isinstance(flag, bool) for flag in record_output_flag):
            raise ValueError("record_output_flag must contain boolean values")

        # Validate input lengths for files_by_directory and record_output_flag
        if validate_lengths(files_by_directory, record_output_flag):
            # If the lengths of files_by_directory and record_output_flag do not match, raise an error
            raise ValueError("Mismatch in the lengths of files_by_directory and record_output_flag")
            # This ensures that each directory has a corresponding flag to indicate whether to record its output

        # Validate the test file names and record test output values lengths if run_tests_flag and test_file_names are provided
        if run_tests_flag is not None and test_file_names is not None:
            # Ensure run_tests_flag and record_test_output_values contain only boolean values
            if not all(isinstance(flag, bool) for flag in run_tests_flag):
                raise ValueError("run_tests_flag must contain boolean values")
            if not all(isinstance(flag, bool) for flag in record_test_output_values):
                raise ValueError("record_test_output_values must contain boolean values")

            # If both run_tests_flag and test_file_names are provided
            if validate_lengths(test_file_names, run_tests_flag, record_test_output_values):
                # Validate that the lengths of test_file_names, run_tests_flag, and record_test_output_values match
                raise ValueError("Mismatch in the lengths of test_file_names, run_tests_flag, or record_test_output_values")
                # This ensures that each test file has corresponding flags to indicate whether to run the tests and record their outputs

        # Check for valid nested lists and flat list structure
        if not check_nested_lists_and_flat_list(files_by_directory, test_file_names, directory_paths):
            # Ensure that the structure of files_by_directory and test_file_names matches the structure of directory_paths
            raise ValueError("Invalid list structure or lengths between nested lists and directory_paths")
            # This ensures that each directory has a corresponding list of files and test files with the correct structure

        # Ensure files_by_directory and test_file_names are not nested empty lists
        if is_nested_empty_list(files_by_directory) or (test_file_names is not None and is_nested_empty_list(test_file_names)):
            # Check if files_by_directory or test_file_names contain nested empty lists
            raise ValueError("Files by directory list or test file names list is a nested empty list")
            # This ensures that there are no empty lists within the nested structure, which would indicate missing data

        # Initialize dictionaries to store outputs
        script_outputs: Dict[str, Any] = {}
        test_outputs: Dict[str, Any] = {}

        # Call organize_flags to get the organized flags based on the input structure
        organized_flags = organize_flags(directory_paths=directory_paths, 
                                        files_by_directory=files_by_directory, 
                                        record_output_flag=record_output_flag, 
                                        run_tests_flag=run_tests_flag, 
                                        record_test_output_values=record_test_output_values, 
                                        test_file_names=test_file_names)

      # Iterate over each directory in the directory paths
        for i, directory in enumerate(directory_paths):

            #  Ensure that i is within the bounds of the files_by_directory list and check if files_by_directory[i] is not empty
            if i < len(files_by_directory) and files_by_directory[i]:
                # Ensure that i is within the bounds of the instructions list and instructions list is not empty 
                if i < len(instructions) and instructions[i]:
                    # Run the aider_runner function
                    aider_runner(directory, files_by_directory[i], model, instructions[i])

            # Determine if any of the flags are True for the current directory
            # This check is necessary to decide if we need to run the scripts or test files
            record_output_flags = get_flag_value(organized_flags.get('record_output_flag', []), i, [False])
            run_tests_flags = get_flag_value(organized_flags.get('run_tests_flag', []), i, [False])
            record_test_output_values = get_flag_value(organized_flags.get('record_test_output_values', []), i, [False])

            # If at least one flag is True, invoke run_script_and_record_output
            if any(record_output_flags) or any(run_tests_flags) or any(record_test_output_values):
                # Check if files_by_directory exists and i is within bounds, and the specific files_by_directory[i] is not None or empty
                if files_by_directory and i < len(files_by_directory) and files_by_directory[i]:
                    for file, record_output_flag in zip(files_by_directory[i], record_output_flags):
                        # Construct the absolute path for the script
                        script_path = str(Path(directory) / file)
                        # Run script and record its output if record_output_flag is True
                        if record_output_flag:
                            if verbose:
                                # Print the action being performed if verbose is True
                                print(f"Running script: {script_path} with record_output_flag: {record_output_flag}")
                            # Call the function to run the script and record its output
                            script_output, _ = run_script_and_record_output(script_path=script_path, record_output=record_output_flag)
                            # Store the script output in the dictionary using the file name as the key
                            script_outputs[script_path] = script_output
                            if verbose:
                                # Print the script output if verbose is True
                                print(f"Script Output for {script_path}:\n{script_output}")

                # Iterate over each test file and its corresponding flags
                # Check if test_file_names exists and i is within bounds, and the specific test_file_names[i] is not None or empty
                if test_file_names and i < len(test_file_names) and test_file_names[i]:
                    for test_file, run_tests_flag, record_test_output_flag in zip(test_file_names[i], run_tests_flags, record_test_output_values):
                        # Construct the absolute path for the test file
                        test_file_path = str(Path(directory) / test_file)
                        # Run tests and record their output if run_tests_flag or record_test_output_flag is True
                        if run_tests_flag or record_test_output_flag:
                            if verbose:
                                # Print the action being performed if verbose is True
                                print(f"Running test file: {test_file_path} with run_tests_flag: {run_tests_flag} and record_test_output_flag: {record_test_output_flag}")
                            # Call the function to run the test file and record its output
                            _, test_output = run_script_and_record_output(test_file_path=test_file_path, record_test_output=record_test_output_flag, run_tests_values=run_tests_flag)
                            # Store the test output in the dictionary using the test file name as the key
                            test_outputs[test_file_path] = test_output
                            if verbose:
                                # Print the test output if verbose is True
                                print(f"Test Output for {test_file_path}:\n{test_output}")


        # Return the dictionaries containing the script and test outputs
        return {
            "script_outputs": script_outputs,
            "test_outputs": test_outputs
        }

    except Exception as e:
        if verbose:
            print(f"Error: {e}")
        raise  # Re-raise the exception after logging it if verbose
    
