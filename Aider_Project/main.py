from pathlib import Path
from typing import  List, Optional, Dict, Any, Tuple
from aider.coders import Coder
from aider.models import Model
from aider.io import InputOutput
from Aider_Project.utils import get_openrouter_api_key, list_files
from Aider_Project.runner import run_script_and_record_output
import os 

# Importing the helper functions from the execute_helper.py file
from Aider_Project.execute_helper import is_nested_empty_list, validate_lengths, check_nested_lists_and_flat_list

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
def execute(directory_paths: List[str], files_by_directory: List[List[str]], 
            model: Any, record_output: bool = True, run_tests: bool = False, test_file_names: Optional[List[List[str]]] = None,
            verbose: bool = False, instructions: Optional[List[str]] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    execute function to process the files in multiple directories.

    Args:
        directory_paths (List[str]): The directories to process.
        files_by_directory (List[List[str]]): The names of the files to process for each directory.
        model (Any): The model to use for processing.
        record_output (bool): Whether to record the script output. Defaults to True.
        run_tests (bool): Whether to run the test files. Defaults to False.
        test_file_names (List[List[str]], optional): The names of the test files to run for each directory. Defaults to None.
        verbose (bool): Whether to print the outputs to the console. Defaults to False.
        instructions (List[str], optional): The list of instructions to run on the files. Defaults to None.

    Raises:
        Exception: If there is an error in the processing or if model is not provided.

    Returns:
        Tuple[Dict[str, Any], Dict[str, Any]]: A tuple containing dictionaries of script and test outputs.
    """
    try:
        # Get API key
        get_openrouter_api_key()

        # Initialize dictionaries to store outputs
        script_outputs: Dict[str, Any] = {}
        test_outputs: Dict[str, Any] = {}
        
        # Process each directory and its corresponding files
        for dir_index, directory in enumerate(directory_paths):
            # List files in the directory
            list_files(directory)
            
            # Process the directory using the separate function
            aider_runner(directory, files_by_directory[dir_index], model, instructions)
            
            # Run the script and optionally record the output
            for file_name in files_by_directory[dir_index]:
                script_output, individual_test_outputs = run_script_and_record_output(
                    script_path=str(Path(directory) / file_name),  # Construct the full script path
                    record_output=record_output,  # Determine if the script's output should be recorded
                    test_file_paths=[str(Path(directory) / test_file_name) for test_file_name in test_file_names[dir_index]] if run_tests and test_file_names else None,  # List of test file paths, if applicable
                    record_test_output=run_tests  # Determine if test outputs should be recorded
                )
                # If recording the script's output is enabled
                if record_output:
                    script_outputs[f"{directory}-{file_name}"] = script_output  # Store the script's output with directory context
                    # Print the script's output to the console if verbose is True
                    if verbose:
                        print(f"Script Output for '{file_name}' in '{directory}':\nSTDOUT:\n{script_output['stdout']}\nSTDERR:\n{script_output['stderr']}")
                # If running tests and test file names are provided
                if run_tests and test_file_names:
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

    # Replace with the absolute paths of the directories you want to process
    # Pass the file names as a list of lists corresponding to each directory
    directory_paths = [r'C:\Users\maste\OneDrive\Desktop\Coding\aider\testing', r'C:\Users\maste\OneDrive\Desktop\Coding\aider\other_testing']
    files_by_directory = [['math_functions.py', 'test.py'], ['another_script.py', 'yet_another_test.py']]
    record_output_flag = [False, True, True, False]
    run_tests_flag = [True, True, True, True]
    record_test_output_values = [True, False, True, False]
    test_file_names = [['test.py', 'another_test.py'], ['other_test.py', 'more_tests.py']]
    verbose_flag = True
    model = Model("openrouter/deepseek/deepseek-coder")
    instructions = [
        "in test.py: make me a code about Fibonacci",
        "in math_functions.py: make me a code about some other function about math use test.py to import the function there",
        # Add more instructions as needed
    ]

    script_outputs, test_outputs = execute(directory_paths, files_by_directory, 
                                           record_output=record_output_flag, 
                                           run_tests=run_tests_flag, 
                                           record_test_output_values=record_test_output_values,
                                           test_file_names=test_file_names,
                                           verbose=verbose_flag,
                                           model=model,
                                           instructions=instructions)
