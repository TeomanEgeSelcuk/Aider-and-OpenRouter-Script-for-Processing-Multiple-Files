from typing import Any, Union, Tuple, List, Optional, Dict
import random

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

def check_nested_lists_and_flat_list(list1: Any, list2: Optional[Any], flat_list: Any) -> bool:
    """
    Checks if the first two lists are nested lists of depth two (if list2 is provided),
    the third list has no nested elements, and the number of nested lists in the first two lists
    is not greater than the number of elements in the flat list.

    Purpose: This function checks if the first two lists are nested lists (files_by_directory, test_file_names)
    of depth two (if list2 is provided), the third list (directory_paths) has no nested elements in the execute function.
    Ensures that there is a directory for each file and test file. If the number of nested lists in the first two lists is greater
    than directory_paths, the to be processed files will not be able to be found. 

    Used in: The execute function.

    directory_paths = [r'path\\to\\testing', r'path\\to\\other_testing']
    files_by_directory = [['math_functions.py', 'test.py'], ['another_script.py', 'yet_another_test.py']]
    test_file_names = [['test.py', 'another_test.py'], ['other_test.py', 'more_tests.py']]

    Args:
        list1 (Any): The first list to check.
        list2 (Optional[Any]): The second list to check (can be None).
        flat_list (Any): The third list to check.

    Returns:
        bool: True if the first two lists are nested lists of depth two (if list2 is provided), the third list has no nested elements,
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

        >>> check_nested_lists_and_flat_list([[], []], None, ['a', 'b', 'c'])
        True  # Only list1 is checked, and flat_list has enough elements.

        >>> check_nested_lists_and_flat_list([[], ['a']], None, ['a', 'b'])
        True  # Only list1 is checked, and flat_list has enough elements.

        >>> check_nested_lists_and_flat_list([[], []], None, ['a'])
        False  # flat_list does not have enough elements.
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
    nested_count_list2 = sum(isinstance(sublist, list) for sublist in list2) if list2 is not None else 0

    # Return True if all conditions are met, otherwise False
    return (is_nested_list_of_depth_two(list1) and 
            (list2 is None or is_nested_list_of_depth_two(list2)) and 
            is_flat_list(flat_list) and 
            nested_count_list1 <= len(flat_list) and 
            nested_count_list2 <= len(flat_list))


def generate_and_count_lists(
    files_by_directory_values: List[List[str]], 
    test_file_names_values: List[List[str]],
    record_output_values: Union[str, bool], 
    record_test_output_values: Union[str, bool], 
    run_tests_values: Union[str, bool]
) -> Tuple[List[Union[bool]], List[Union[bool]], List[Union[bool]]]:
    """
    Generate record lists based on provided flags and count elements in nested lists.

    Purpose: This function creates lists of True/False values for testing, based on flags and the 
    number of files in nested lists. It ensures these lists are the right length to match 
    the input data.

    Used in: Helps test the behavior of the `execute` function with different settings. 
    Found in the `test_generate_and_count_lists` and `test_execute_combined` test cases.

    Parameters:
    - files_by_directory_values: Lists of file names by directory.
    - test_file_names_values: Lists of test file names.
    - record_output_values: Flag to generate the record output list ("Mix", True, or False).
    - record_test_output_values: Flag to generate the record test output list ("Mix", True, or False).
    - run_tests_values: Flag to generate the run tests list ("Mix", True, or False).

    Returns:
    - Tuple with:
        - List based on record_output_values.
        - List based on record_test_output_values.
        - List based on run_tests_values.

    Raises:
    - ValueError: If any flag is invalid or nested lists are empty.

    Example Usage:
        >>> # Generates lists of True values.
        >>> generate_and_count_lists(
        ...     [['file1.py', 'file2.py'], ['file3.py']],
        ...     [['test1.py'], ['test2.py']],
        ...     True, True, True
        ... )
        ([True, True, True], [True, True], [True, True])

        >>> # Generates lists of False values.
        >>> generate_and_count_lists(
        ...     [['file1.py', 'file2.py'], ['file3.py']],
        ...     [['test1.py'], ['test2.py']],
        ...     False, False, False
        ... )
        ([False, False, False], [False, False], [False, False])

        >>> # Generates mixed lists of True and False values.
        >>> generate_and_count_lists(
        ...     [['file1.py', 'file2.py'], ['file3.py']],
        ...     [['test1.py'], ['test2.py']],
        ...     "Mix", "Mix", "Mix"
        ... )
        ([True, False, True], [False, True], [True, False])

        >>> # Raises ValueError for empty nested lists.
        >>> try:
        .        directory_paths_1 = [
            r'path\to\codetest', 
            r'path\to\codetest-2'
        ]ain empty lists"

        >>> # Raises ValueError for invalid flag.
        >>> try:
        ...     generate_and_count_lists(
        ...         [['file.py']], [['test.py']], "Invalid", True, True
        ...     )
        ... except ValueError as e:
        ...     print(e)
        "Invalid value for record flag"
    """

    # Function to count elements in nested lists
    def count_elements(nested_list: List[List[str]]) -> int:
        count = 0  # Initialize count to zero
        for sublist in nested_list:  # Iterate over each sublist
            if not isinstance(sublist, list):  # Check if sublist is a list
                raise ValueError("Invalid nested list structure")  # Raise error if not
            count += len(sublist)  # Add the length of each sublist to the count
        return count  # Return the total count
    
    # Validate input lists
    if not files_by_directory_values or is_nested_empty_list(files_by_directory_values):  # Check if files_by_directory_values is empty or contains empty lists
        raise ValueError("files_by_directory_values cannot be empty or contain empty lists")  # Raise error
    if not test_file_names_values or is_nested_empty_list(test_file_names_values):  # Check if test_file_names_values is empty or contains empty lists
        raise ValueError("test_file_names_values cannot be empty or contain empty lists")  # Raise error

    # Calculate the number of elements in provided values
    files_by_directory_count = count_elements(files_by_directory_values)  # Count elements in files_by_directory_values
    test_file_names_count = count_elements(test_file_names_values)  # Count elements in test_file_names_values

    # Generate lists based on record_output_values, record_test_output_values, and run_tests_values
    def generate_record_list(values: Union[str, bool], count: int) -> List[Union[bool]]:
        if values == "Mix":  # If the flag is "Mix"
            return [random.choice([True, False]) for _ in range(count)]  # Generate a mixed list of True and False
        elif values is True:  # If the flag is True
            return [True] * count  # Generate a list of True values
        elif values is False:  # If the flag is False
            return [False] * count  # Generate a list of False values
        else:  # If the flag is invalid
            raise ValueError("Invalid value for record flag")  # Raise an error for invalid values

    # Generate the output lists based on the provided flags
    record_output_list = generate_record_list(record_output_values, files_by_directory_count)  # Generate record output list
    record_test_output_list = generate_record_list(record_test_output_values, test_file_names_count)  # Generate record test output list
    run_tests_list = generate_record_list(run_tests_values, test_file_names_count)  # Generate run tests list

    # Return the generated lists
    return record_output_list, record_test_output_list, run_tests_list


def organize_flags(directory_paths: Optional[List[str]] = None, 
                   files_by_directory: Optional[List[List[str]]] = None, 
                   record_output_flag: Optional[List[bool]] = None, 
                   run_tests_flag: Optional[List[bool]] = None, 
                   record_test_output_values: Optional[List[bool]] = None,
                   test_file_names: Optional[List[List[str]]] = None) -> Dict[str, Any]:
    """
    The function organizes the flags based on the input structure of directories and files. 
    Each flag (record_output_flag, run_tests_flag, record_test_output_values) is converted from a flat list 
    to a nested list that mirrors the structure of `files_by_directory` and `test_file_names`.
    
    - `record_output_flag` is dependent on the total number of files in `files_by_directory`. 
      It is sliced according to the number of files in each directory.
    
    - `run_tests_flag` and `record_test_output_values` are dependent on the number of test files in `test_file_names`. 
      They are sliced according to the number of test files in each directory.
    
    The function first validates that the lengths of these flags match the expected number of files and test files. 
    It then iterates through each directory and slices the flags accordingly, creating nested lists that 
    correctly correspond to the structure of `files_by_directory` and `test_file_names`.

    Furthermore it ensures:
    - Ensures that if files_by_directory is None, record_output_flag must also be None, and vice versa.
    - Ensures that if test_file_names is None, both run_tests_flag and record_test_output_values must also be None, and vice versa.
    - Ensures that at least one variable from both groups is not None.
    
    Args:
        directory_paths (Optional[List[str]]): List of directory paths.
        files_by_directory (Optional[List[List[str]]]): Nested list where each sublist contains files for a directory.
        record_output_flag (Optional[List[bool]]): Flat list of record output flags for each file.
        run_tests_flag (Optional[List[bool]]): Flat list of run tests flags for each file.
        record_test_output_values (Optional[List[bool]]): Flat list of record test output values for each file.
        test_file_names (Optional[List[List[str]]]): Nested list of test files for each directory.
    
    Returns:
        Dict[str, Any]: A dictionary containing the organized flags.
    
    Raises:
        ValueError: If the lengths of run_tests_flag or record_test_output_values do not match the number of test files
                    or if the length of record_output_flag does not match the number of files.
    
    Examples:
        Test Case 1:
        ```
        # Define the input arguments for the function
        directory_paths_1 = [
            r'path\to\codetest', 
            r'path\to\codetest-2'
        ]
        files_by_directory_1 = [
            ["file1.py", "file2.py"], 
            ["file3.py"]
        ]
        test_file_names_1 = [
            ["test_file1.py"], 
            ["test_file3.py"]
        ]
        record_output_flag_1 = [True, True, False]
        run_tests_flag_1 = [False, False]
        record_test_output_values_1 = [False, False]
    
        # Call the function to organize the flags for test case 1
        organized_flags_1 = organize_flags(
            directory_paths_1, 
            files_by_directory_1, 
            record_output_flag_1, 
            run_tests_flag_1, 
            record_test_output_values_1,
            test_file_names_1
        )
    
        # Print the organized flags for test case 1
        print("Test Case 1 Output:")
        print(organized_flags_1)
        ```
    
        Expected Output for Test Case 1:
        ```
        {
            'record_output_flag': [[True, True], [False]], 
            'run_tests_flag': [[False], [False]], 
            'record_test_output_values': [[False], [False]]
        }
        ```
    
        Explanation:
        - The first directory has two regular files and one test file.
        - The second directory has one regular file and one test file.
        - `record_output_flag` is split into `[[True, True], [False]]` because there are 3 files in total, 2 in the first and one in the last directory.
        - `run_tests_flag` is split into `[[False], [False]]` because there are 2 test files in total, 1 in each directory.
        - `record_test_output_values` is split into `[[False], [False]]` because there are 2 test files in total, 1 in each directory.
    
        Test Case 2:
        ```
        # Define the input arguments for the function
        directory_paths_1 = [
            r'path\to\codetest', 
            r'path\to\codetest-2'
        ]
        files_by_directory_2 = [
            ["file1.py", "file3.py"], 
            ["test_file1.py", "test_file3.py"]
        ]
        test_file_names_2 = [
            [], 
            ["test_file1.py", "test_file3.py"]
        ]
        record_output_flag_2 = [True, True, False, False]
        run_tests_flag_2 = [True, True]
        record_test_output_values_2 = [True, True]
    
        # Call the function to organize the flags for test case 2
        organized_flags_2 = organize_flags(
            directory_paths_2, 
            files_by_directory_2, 
            record_output_flag_2, 
            run_tests_flag_2, 
            record_test_output_values_2,
            test_file_names_2
        )
    
        # Print the organized flags for test case 2
        print("Test Case 2 Output:")
        print(organized_flags_2)
        ```
    
        Expected Output for Test Case 2:
        ```
        {
            'record_output_flag': [[True, True], [False, False]], 
            'run_tests_flag': [[], [True, True]], 
            'record_test_output_values': [[], [True, True]]
        }
        ```
    
        Explanation:
        - The first directory has two regular files and no test files.
        - The second directory has no regular files and two test files.
        - `record_output_flag` is split into `[[True, True], [False, False]]` because there are 4 files in total, 2 in each directory.
        - `run_tests_flag` is split into `[[], [True, True]]` because there are 2 test files in total, only in the second directory.
        - `record_test_output_values` is split into `[[], [True, True]]` because there are 2 test files in total, only in the second directory.
    
    """

    # Check if both flag groups (group 1: files_by_directory and record_output_flag,
    # group 2: run_tests_flag, record_test_output_values, and test_file_names) are None
    # If files_by_directory is None, record_output_flag must be None
    if files_by_directory is None and record_output_flag is not None:
        raise ValueError("record_output_flag must be None if files_by_directory is None.")

    # If files_by_directory is not None, record_output_flag must not be None
    if files_by_directory is not None and record_output_flag is None:
        raise ValueError("record_output_flag must be provided if files_by_directory is not None.")

    # If test_file_names is None, run_tests_flag and record_test_output_values must be None
    if test_file_names is None and (run_tests_flag is not None or record_test_output_values is not None):
        raise ValueError("run_tests_flag and record_test_output_values must be None if test_file_names are None.")

    # If test_file_names is not None, run_tests_flag and record_test_output_values must not be None
    if test_file_names is not None:
        if run_tests_flag is None:
            raise ValueError("run_tests_flag must be provided if test_file_names are not None.")
        if record_test_output_values is None:
            raise ValueError("record_test_output_values must be provided if test_file_names are not None.")

    # Ensure at least one variable from both groups is not None
    if (files_by_directory is None and record_output_flag is None) and \
       (test_file_names is None and run_tests_flag is None and record_test_output_values is None):
        raise ValueError("At least one variable from both groups must not be None.")

    # Calculate the total number of files in all directories, considering if files_by_directory is not None
    total_files = sum(len(files) for files in files_by_directory) if files_by_directory is not None else 0

    # Calculate the total number of test files in all directories, considering if test_file_names is not None
    total_test_files = sum(len(tests) for tests in test_file_names) if test_file_names is not None else 0

    # If record_output_flag is not None, check if its length matches the total number of files
    if record_output_flag is not None and len(record_output_flag) != total_files:
        raise ValueError("Length of record_output_flag must match the total number of files.")
    
    # If run_tests_flag is not None, check if its length matches the total number of test files
    if run_tests_flag is not None and len(run_tests_flag) != total_test_files:
        raise ValueError("Length of run_tests_flag must match the total number of test files.")
    
    # If record_test_output_values is not None, check if its length matches the total number of test files
    if record_test_output_values is not None and len(record_test_output_values) != total_test_files:
        raise ValueError("Length of record_test_output_values must match the total number of test files.")

    # Initialize nested lists to store the organized flags
    nested_record_output_flag = []
    nested_run_tests_flag = []
    nested_record_test_output_values = []

    # Initialize index trackers for the flags to keep track of the current position in the flat lists
    file_index = 0
    test_file_index = 0

    # Iterate over each directory and its corresponding files to organize the flags into nested lists
    for i, files in enumerate(files_by_directory or []):
        # Number of regular files in the current directory
        num_files = len(files)
        
        # Number of test files in the current directory
        num_test_files = len(test_file_names[i] if test_file_names else [])

        # Slice the record_output_flag list to get flags for the current directory
        if record_output_flag is not None:
            nested_record_output_flag.append(record_output_flag[file_index:file_index + num_files])
        
        # Slice the run_tests_flag list to get flags for the current directory
        if run_tests_flag is not None:
            nested_run_tests_flag.append(run_tests_flag[test_file_index:test_file_index + num_test_files])
        
        # Slice the record_test_output_values list to get flags for the current directory
        if record_test_output_values is not None:
            nested_record_test_output_values.append(record_test_output_values[test_file_index:test_file_index + num_test_files])

        # Update the indices to the next position in the flat lists
        file_index += num_files
        test_file_index += num_test_files

    # Return a dictionary containing the organized flags as nested lists
    return {
        "record_output_flag": nested_record_output_flag if record_output_flag is not None else None,
        "run_tests_flag": nested_run_tests_flag if run_tests_flag is not None else None,
        "record_test_output_values": nested_record_test_output_values if record_test_output_values is not None else None
    }
