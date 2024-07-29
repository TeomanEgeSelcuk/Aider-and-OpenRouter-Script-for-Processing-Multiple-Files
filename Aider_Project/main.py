from pathlib import Path
from typing import  List, Optional, Dict, Any, Tuple
from aider.coders import Coder
from aider.models import Model
from aider.io import InputOutput
from Aider_Project.utils import get_openrouter_api_key, list_files
from Aider_Project.runner import run_script_and_record_output
import os 

'''
main.py: Contains the execute function and the entry point.
utils.py: Contains utility functions such as get_openrouter_api_key and list_files.
runner.py: Contains the run_script_and_record_output function.
'''

def is_nested_empty_list(lst: Any) -> bool:
    """
    Checks if the given list is a nested empty list.

    Purpose: This function determines if a list is either empty or consists of nested empty lists. If empty
    filenames and test filenames are passed, the execute function and aider won't be able to modify and update the files.
    As well as running the files and recording their respective outputs.

    Used in: Used in the execute function 

    Args:
        lst (Any): The list to check.

    Returns:
        bool: True if the list is a nested empty list, False otherwise.

    Example Usage:
        >>> is_nested_empty_list([])
        True
        >>> is_nested_empty_list([[], [[]]])
        True
        >>> is_nested_empty_list([1, [], [[]]])
        False
    """
    return isinstance(lst, list) and (not lst or all(is_nested_empty_list(item) for item in lst))

def validate_lengths(nested_list: list[list[str]], list1: list[bool], list2: list[bool] = None) -> bool:
    """
    Validates if the number of values in a nested list of depth 2 matches the lengths of two other flat boolean lists.
    Also checks if all values in the boolean lists are bool and the nested list contains only strings.

    Purpose: This function checks that the lengths of the nested lists (files_by_directory, test_file_names) 
    match the lengths of the corresponding boolean lists (record_output_flag for files_by_directory and run_tests_flag,
    record_test_output_values for test_file_names). It ensures that all values are of the correct type. 
    This validation is important to avoid confusion about which files to process and which outputs to record.

    Used in: The execute function.

    Args:
        nested_list (list[list[str]]): A nested list of depth 2 containing strings.
        list1 (list[bool]): A flat list of booleans.
        list2 (list[bool], optional): Another flat list of booleans. Default is None.

    Returns:
        bool: False if the lengths match and all values are correct types, True otherwise.

    Example:
        # Example 1: All checks pass
        nested_list = [["file1", "file2"], ["file3", "file4", "file5"]]
        list1 = [True, False, True, False, True]
        list2 = [False, True, False, True, False]
        result = validate_lengths(nested_list, list1, list2)
        print(result)  # Should print False

        # Example 2: Lengths do not match
        nested_list = [["file1", "file2"], ["file3", "file4"]]
        list1 = [True, False, True, False, True
        list2 = [False, True, False, True, False]
        result = validate_lengths(nested_list, list1, list2)
        print(result)  # Should print True

        # Example 3: Nested list contains non-string values
        nested_list = [["file1", 2], ["file3", "file4", "file5"]]
        list1 = [True, False, True, False, True]
        list2 = [False, True, False, True, False]
        result = validate_lengths(nested_list, list1, list2)
        print(result)  # Should print True

        # Example 4: Boolean lists contain non-boolean values
        nested_list = [["file1", "file2"], ["file3", "file4", "file5"]]
        list1 = [True, False, "True", False, True]
        list2 = [False, True, False, True, False]
        result = validate_lengths(nested_list, list1, list2)
        print(result)  # Should print True

        # Example 5: Only list1 is passed
        nested_list = [["file1", "file2"], ["file3", "file4", "file5"]]
        list1 = [True, False, True, False, True]
        result = validate_lengths(nested_list, list1)
        print(result)  # Should print False
    """
    # Flatten the nested list and get the count of values
    flat_list = [item for sublist in nested_list for item in sublist]
    nested_list_count = len(flat_list)  # Count of all items in the flattened nested list

    # Check if all values in the nested list are strings
    if not all(isinstance(item, str) for item in flat_list):
        return True  # Return True if any item in the nested list is not a string

    # Check if all values in list1 are booleans
    if not all(isinstance(item, bool) for item in list1):
        return True  # Return True if any item in list1 is not a boolean

    # If list2 is provided, check if all values in list2 are booleans
    if list2 is not None:
        if not all(isinstance(item, bool) for item in list2):
            return True  # Return True if any item in list2 is not a boolean
        # Check if the lengths of list1 and list2 match the count of values in the nested list
        if len(list1) != nested_list_count or len(list2) != nested_list_count:
            return True  # Return True if lengths do not match

    # Check if the length of list1 matches the count of values in the nested list
    return len(list1) != nested_list_count


def check_nested_lists_and_flat_list(list1: Any, list2: Any, flat_list: Any) -> bool:
    """
    Checks if the first two lists are nested lists of depth two, the third list has no nested elements,
    and the number of nested lists in the first two lists is not greater than the number of elements in the flat list.

    Purpose: This function checks if the first two lists are nested lists (files_by_directory, test_file_names) of depth two,
    the third list (directory_paths) has no nested elements in the execute function. Ensures that there is a directory for each 
    file and test file. If the number of nested lists in the first two lists is greater than directory_paths, the to be processed
    files will not be able to be found. 

    Used in: The execute function.

    directory_paths = [r'path\\to\\testing', r'path\\to\\other_testing']
    files_by_directory = [['math_functions.py', 'test.py'], ['another_script.py', 'yet_another_test.py']]
    test_file_names = [['test.py', 'another_test.py'], ['other_test.py', 'more_tests.py']]

    Args:
        list1 (Any): The first list to check.
        list2 (Any): The second list to check.
        flat_list (Any): The third list to check.

    Returns:
        bool: True if the first two lists are nested lists of depth two, the third list has no nested elements,
            and the number of nested lists in the first two lists is not greater than the number of elements in the flat list. 
            False otherwise.

    Example Usage:
        >>> check_nested_lists_and_flat_list([[], []], [[], []], ['a', 'b', 'c'])
        True  # Both list1 and list2 are nested lists of depth two, and flat_list is a flat list with enough elements.

        >>> check_nested_lists_and_flat_list([[], []], [[], [], []], ['a', 'b', 'c'])
        True  # Similar to above, but list2 has more sublists.

        >>> check_nested_lists_and_flat_list([[], []], [[], [], [[]]], ['a', 'b', 'c'])
        False  # list2 contains a nested list deeper than depth two.

        >>> check_nested_lists_and_flat_list([[[]]], [[], []], ['a', 'b', 'c'])
        False  # list1 contains a nested list deeper than depth two.

        >>> check_nested_lists_and_flat_list([[], []], [[], []], [['a'], 'b', 'c'])
        False  # flat_list contains nested elements.

        >>> check_nested_lists_and_flat_list([[], []], [[], []], ['a'])
        False  # flat_list does not have enough elements.

        >>> check_nested_lists_and_flat_list([[], []], [[], []], ['a', 'b', 'c'])
        True  # Both list1 and list2 are nested lists of depth two, and flat_list is a flat list with enough elements.

        >>> check_nested_lists_and_flat_list([['a'], ['b','bb','B']], [['c'], ['d']], ['a', 'b', 'c', 'd'])
        True  # Both list1 and list2 are nested lists of depth two with values, and flat_list is a flat list with enough elements.

        >>> check_nested_lists_and_flat_list([['a'], ['b']], [['c'], ['d'], ['e']], ['a', 'b', 'c'])
        True  # Similar to above, but list2 has more sublists.

        >>> check_nested_lists_and_flat_list([['a'], ['b']], [['c'], ['d']], ['a'])
        False  # flat_list does not have enough elements.

        >>> check_nested_lists_and_flat_list([[], [], []], [[], []], ['a', 'b', 'c', 'd', 'e'])
        True  # list1 and list2 both have three sublists, flat_list has enough elements.

        >>> check_nested_lists_and_flat_list([[], [], []], [[], [], []], ['a', 'b'])
        False  # flat_list does not have enough elements.

        >>> check_nested_lists_and_flat_list([[], ['a']], [[], ['b']], ['c', 'd', 'e'])
        True  # Both list1 and list2 are nested lists of depth two with values, flat_list has enough elements.

        >>> check_nested_lists_and_flat_list([[], []], [[], ['a']], ['a', 'b', 'c', 'd'])
        True  # list1 and list2 both have sublists, and flat_list has enough elements.
    """

    def is_nested_list_of_depth_two(lst: Any) -> bool:
        # Check if lst is a list and each element is a list of lists
        return (isinstance(lst, list) and all(isinstance(sublist, list) and 
                all(not isinstance(item, list) for item in sublist) for sublist in lst))

    def is_flat_list(lst: Any) -> bool:
        # Check if lst is a list and none of the elements are lists
        return isinstance(lst, list) and all(not isinstance(item, list) for item in lst)

    # Count the number of sublists in list1 and list2
    nested_count_list1 = sum(isinstance(sublist, list) for sublist in list1)
    nested_count_list2 = sum(isinstance(sublist, list) for sublist in list2)

    # Return True if all conditions are met, otherwise False
    return (is_nested_list_of_depth_two(list1) and is_nested_list_of_depth_two(list2) and 
            is_flat_list(flat_list) and 
            nested_count_list1 <= len(flat_list) and nested_count_list2 <= len(flat_list))

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
