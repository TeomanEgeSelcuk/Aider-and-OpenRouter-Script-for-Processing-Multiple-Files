
from typing import Any

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
