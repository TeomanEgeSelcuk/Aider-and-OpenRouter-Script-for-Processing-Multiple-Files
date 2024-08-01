from pathlib import Path
from typing import  List, Optional, Dict, Any, Tuple, Union
from aider.coders import Coder
from aider.models import Model
from aider.io import InputOutput
import os
from Aider_Project.utils import get_openrouter_api_key, list_files
from Aider_Project.runner import run_script_and_record_output 
from Aider_Project.execute_helper import is_nested_empty_list, validate_lengths, check_nested_lists_and_flat_list, generate_and_count_lists

'''
main.py: Contains the execute function and the entry point.
utils.py: Contains utility functions such as get_openrouter_api_key and list_files.
runner.py: Contains the run_script_and_record_output function.
execute_helper.py: Contains helper functions for the execute function: is_nested_empty_list, validate_lengths, check_nested_lists_and_flat_list
'''

# Function to process a single directory and its corresponding files and make edits using Aider and chosen OpenRouter LLM
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
    coder.find_common_root()  # Ensure paths are correctly set
    
    # Disable auto commits
    coder.auto_commits = False

    # Run the prompts on the files
    for instruction in instructions:
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
        # If test_file_names is None, set run_tests_flag and record_test_output_values to lists of False
        if test_file_names is None:
            # If no test file names are provided
            run_tests_flag = [False] * len(directory_paths)  # Set run_tests_flag to False for all directories
            record_test_output_values = [False] * len(directory_paths)  # Set record_test_output_values to False for all directories

        # Validate input lengths for files_by_directory and record_output_flag
        if validate_lengths(files_by_directory, record_output_flag):
            raise ValueError("Mismatch in the lengths of files_by_directory and record_output_flag")

        # Validate the test file names and record test output values lengths if run_tests_flag and test_file_names are provided
        if run_tests_flag is not None and test_file_names is not None:
            if validate_lengths(test_file_names, run_tests_flag, record_test_output_values):
                raise ValueError("Mismatch in the lengths of test_file_names, run_tests_flag, or record_test_output_values")

        # Check for valid nested lists and flat list structure
        if check_nested_lists_and_flat_list(files_by_directory, test_file_names, directory_paths):
            raise ValueError("Invalid list structure or lengths between nested lists and directory_paths")

        # Ensure files_by_directory and test_file_names are not nested empty lists
        if is_nested_empty_list(files_by_directory) or (test_file_names is not None and is_nested_empty_list(test_file_names)):
            raise ValueError("Files by directory list or test file names list is a nested empty list")
        
        # Initialize dictionaries to store outputs
        script_outputs: Dict[str, Any] = {}
        test_outputs: Dict[str, Any] = {}

        # Process each directory and its corresponding files
        for dir_index, directory in enumerate(directory_paths):
            # List files in the directory
            list_files(directory)

            # Process the directory using the separate function
            aider_runner(directory, files_by_directory[dir_index], model, instructions)

            # Determine if we should run tests and record test output
            run_tests = run_tests_flag[dir_index]
            record_test_output = record_test_output_values[dir_index]
            test_files = test_file_names[dir_index]

            # Run the script and optionally record the output
            for file_name in files_by_directory[dir_index]:
                script_output, individual_test_outputs = run_script_and_record_output(
                    script_path=str(Path(directory) / file_name),  # Construct the full script path
                    record_output=record_output_flag[dir_index],  # Determine if the script's output should be recorded
                    test_file_paths=[str(Path(directory) / test_file_name) for test_file_name in test_files] if run_tests else None,  # List of test file paths, if applicable
                    record_test_output=record_test_output,  # Determine if test outputs should be recorded
                    run_tests_values=run_tests  # Determine if tests should be run
                )
                # If recording the script's output is enabled
                if record_output_flag[dir_index]:
                    script_outputs[f"{directory}-{file_name}"] = script_output  # Store the script's output with directory context
                    # Print the script's output to the console if verbose is True
                    if verbose:
                        print(f"Script Output for '{file_name}' in '{directory}':\nSTDOUT:\n{script_output['stdout']}\nSTDERR:\n{script_output['stderr']}")
                # If running tests and test file names are provided
                if run_tests and test_files:
                    for test_file_name, test_output in individual_test_outputs.items():
                        test_outputs[f"{directory}-{test_file_name}"] = test_output  # Store the test's output with directory context
                        # Print the test's output to the console if verbose is True
                        if verbose:
                            print(f"Test Output for '{test_file_name}' in '{directory}':\nSTDOUT:\n{test_output['stdout']}\nSTDERR:\n{test_output['stderr']}")

        # Optional: Process or return the collected outputs
        return script_outputs, test_outputs

    except Exception as e:
        if verbose:
            print(f"Error: {e}")
        raise  # Re-raise the exception after logging it if verbose
    
# Example usage
if __name__ == "__main__":

    # # Replace with the absolute paths of the directories you want to process
    # # Pass the file names as a list of lists corresponding to each directory
    # directory_paths = [r'C:\Users\maste\OneDrive\Desktop\Coding\aider\codetest', r'C:\Users\maste\OneDrive\Desktop\Coding\aider\codetest-2']
    # files_by_directory = [['math_functions.py', 'test.py'], ['another_script.py', 'yet_another_test.py']]
    # record_output_flag = [False, True, True, False]
    # run_tests_flag = [True, True, True, True]
    # record_test_output_values = [True, False, True, False]
    # test_file_names = [['test.py', 'another_test.py'], ['other_test.py', 'more_tests.py']]
    # verbose_flag = True
    # model = Model("openrouter/deepseek/deepseek-coder")
    # instructions = [
    #     "in test.py: make me a code about Fibonacci",
    #     "in math_functions.py: make me a code about some other function about math use test.py to import the function there",
    #     # Add more instructions as needed
    # ]

    # script_outputs, test_outputs = execute(directory_paths, files_by_directory, 
    #                                        record_output=record_output_flag, 
    #                                        run_tests=run_tests_flag, 
    #                                        record_test_output_values=record_test_output_values,
    #                                        test_file_names=test_file_names,
    #                                        verbose=verbose_flag,
    #                                        model=model,
    #                                        instructions=instructions)

    model = Model("openrouter/deepseek/deepseek-coder")

    # Example 1: Basic usage without tests
    directory_paths = [r'C:\Users\maste\OneDrive\Desktop\Coding\aider\codetest', r'C:\Users\maste\OneDrive\Desktop\Coding\aider\codetest-2']
    files_by_directory = [["file1.py", "file2.py"], ["file3.py"]]
    record_output_flag = [True, True, True]
    run_tests_flag = [False, False]
    test_file_names = [["test_file1.py"], ["test_file3.py"]]  # Optional argument set to empty lists
    record_test_output_values = [False, False]  # Optional argument set to False
    instructions = [
        "in file1.py: add a function to print 'Hello World'",
        "in file2.py: add a function to print 'Test File 2'",
        "in file3.py: add a function to print 'Test File 3'"
    ]
    print("Example 1 Output:")
    print(execute(directory_paths, files_by_directory, model, record_output_flag, run_tests_flag, test_file_names, record_test_output_values, verbose=True, instructions=instructions))

    # Example 2: Running scripts and tests with output recording
    directory_paths = [r'C:\Users\maste\OneDrive\Desktop\Coding\aider\codetest', r'C:\Users\maste\OneDrive\Desktop\Coding\aider\codetest-2']
    files_by_directory = [["file1.py"], ["file3.py"]]
    record_output_flag = [True, True]
    run_tests_flag = [True, True]
    test_file_names = [["test_file1.py"], ["test_file3.py"]]
    record_test_output_values = [True, True]
    instructions = [
        "in file1.py: add a function to print 'Running tests'",
        "in file3.py: add a function to print 'Running tests on file 3'"
    ]
    print("Example 2 Output:")
    print(execute(directory_paths, files_by_directory, model, record_output_flag, run_tests_flag, test_file_names, record_test_output_values, verbose=True, instructions=instructions))

    # Example 3: Running scripts without recording their output
    directory_paths = [r'C:\Users\maste\OneDrive\Desktop\Coding\aider\codetest']
    files_by_directory = [["file1.py"]]
    record_output_flag = [False]
    run_tests_flag = [False]
    test_file_names = [[]]  # Optional argument set to empty list
    record_test_output_values = [False]  # Optional argument set to False
    instructions = ["in file1.py: add a function to print 'No output recording'"]
    print("Example 3 Output:")
    print(execute(directory_paths, files_by_directory, model, record_output_flag, run_tests_flag, test_file_names, record_test_output_values, verbose=True, instructions=instructions))

    # Example 4: Complex case with mixed settings
    directory_paths = [r'C:\Users\maste\OneDrive\Desktop\Coding\aider\codetest', r'C:\Users\maste\OneDrive\Desktop\Coding\aider\codetest-2']
    files_by_directory = [["file1.py", "file2.py"], ["file3.py"]]
    record_output_flag = [True, False]
    run_tests_flag = [True, False]
    test_file_names = [["test_file1.py", "test_file2.py"], []]
    record_test_output_values = [True, False]
    instructions = [
        "in file1.py: add a function to print 'Complex case example 1'",
        "in file2.py: add a function to print 'Complex case example 2'",
        "in file3.py: add a function to print 'Complex case example 3'"
    ]
    print("Example 4 Output:")
    print(execute(directory_paths, files_by_directory, model, record_output_flag, run_tests_flag, test_file_names, record_test_output_values, verbose=True, instructions=instructions))

    # Example 5: Running scripts with optional test parameters not given
    directory_paths = [r'C:\Users\maste\OneDrive\Desktop\Coding\aider\codetest']
    files_by_directory = [["file1.py", "file2.py"]]
    record_output_flag = [True]
    run_tests_flag = [False]
    instructions = [
        "in file1.py: add a function to print 'No tests'",
        "in file2.py: add a function to print 'No tests'"
    ]
    print("Example 5 Output:")
    print(execute(directory_paths, files_by_directory, model, record_output_flag, run_tests_flag, verbose=True, instructions=instructions))
    