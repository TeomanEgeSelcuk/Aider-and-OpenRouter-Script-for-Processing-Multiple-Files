from Aider_Project.execute_helper import is_nested_empty_list, validate_lengths, check_nested_lists_and_flat_list # Import helper functions
import pytest 

# Parameterized data for is_nested_empty_list function
@pytest.mark.parametrize("lst, expected", [
    ([], True),                     # An empty list, which should return True
    ([[]], True),                   # A list containing an empty list, which should return True
    ([[[]]], True),                 # A list containing a list that contains an empty list, which should return True
    ([[[], [[]]]], True),           # A list containing an empty list and a list containing an empty list, which should return True
    ([1, [], [[]]], False),         # A list with a non-empty element, an empty list, and a nested empty list, which should return False
    ([[], [1]], False),             # A list containing an empty list and a list with a non-empty element, which should return False
    ([1, 2, 3], False),             # A list with non-empty elements, which should return False
    ("not a list", False)           # A string, which should return False since it's not a list
])
def test_is_nested_empty_list(lst, expected):
    """
    Tests the is_nested_empty_list function with various inputs.
    
    Args:
        lst: The list to check.
        expected: The expected result.
    """
    # Assert that the function's output matches the expected result
    assert is_nested_empty_list(lst) == expected


# Parameterized data for validate_lengths function
@pytest.mark.parametrize("nested_list, list1, list2, expected", [
    ([["file1", "file2"], ["file3", "file4"]], [True, False, True, False, True], [False, True, False, True, False], True), # Test case where the lengths of lists do not match
    ([["file1", 2], ["file3", "file4", "file5"]], [True, False, True, False, True], [False, True, False, True, False], True), # Test case with non-string value in nested list
    ([["file1", "file2"], ["file3", "file4", "file5"]], [True, False, "True", False, True], [False, True, False, True, False], True), # Test case with non-boolean value in list1
    ([["file1", "file2"], ["file3", "file4", "file5"]], [True, False, True, False], [False, True, False, True, False], True), # Test case where list1 length does not match nested list count
    ([["file1", "file2"], ["file3", "file4", "file5"]], [True, False, True, False, True], [False, True, False, True], True), # Test case where list2 length does not match nested list count
    ([[]], [], [], False), # Test case with empty nested list and empty boolean lists
    ([["file1", "file2"]], [True, False], [False, True], False), # Test case where nested list and boolean lists have matching lengths
    ([["file1", "file2"], ["file3", "file4", "file5"]], [True, False, True, False, True], None, False), # Test case without list2, only checks list1 length
    ([["file1", "file2"], ["file3", "file4"]], [True, False, True, False, True], None, True) # Test case without list2, lengths do not match
])
def test_validate_lengths(nested_list, list1, list2, expected):
    """
    Tests the validate_lengths function with various inputs.
    
    Args:
        nested_list: The nested list of strings.
        list1: The first flat list of booleans.
        list2: The second flat list of booleans.
        expected: The expected result.
    """
    # Assert that the function's output matches the expected result
    assert validate_lengths(nested_list, list1, list2) == expected


@pytest.mark.parametrize("list1, list2, flat_list, expected", [
    ([[], []], [[], []], ['a', 'b', 'c'], True),  # Both list1 and list2 are nested lists of depth two, flat_list has enough elements
    ([[], []], [[], [], []], ['a', 'b', 'c'], True),  # list2 has more sublists, flat_list has enough elements
    ([[], []], [[], [], [[]]], ['a', 'b', 'c'], False),  # list2 contains a nested list deeper than depth two
    ([[[]]], [[], []], ['a', 'b', 'c'], False),  # list1 contains a nested list deeper than depth two
    ([[], []], [[], []], [['a'], 'b', 'c'], False),  # flat_list contains nested elements
    ([[], []], [[], []], ['a'], False),  # flat_list does not have enough elements
    ([[], []], [[], []], ['a', 'b', 'c'], True),  # Both list1 and list2 are nested lists of depth two, flat_list has enough elements
    ([['a'], ['b', 'bb', 'B']], [['c'], ['d']], ['a', 'b', 'c', 'd'], True),  # Nested lists with values, flat_list has enough elements
    ([['a'], ['b']], [['c'], ['d'], ['e']], ['a', 'b', 'c'], True),  # Similar to above, but list2 has more sublists
    ([['a'], ['b']], [['c'], ['d']], ['a'], False),  # flat_list does not have enough elements
    ([[], [], []], [[], []], ['a', 'b', 'c', 'd', 'e'], True),  # list1 and list2 both have three sublists, flat_list has enough elements
    ([[], [], []], [[], [], []], ['a', 'b'], False),  # flat_list does not have enough elements
    ([[], ['a']], [[], ['b']], ['c', 'd', 'e'], True),  # Nested lists with values, flat_list has enough elements
    ([[], []], [[], ['a']], ['a', 'b', 'c', 'd'], True),  # list1 and list2 both have sublists, flat_list has enough elements
])
def test_check_nested_lists_and_flat_list(list1, list2, flat_list, expected):
    """
    Tests the check_nested_lists_and_flat_list function with various inputs.

    Args:
        list1: The first list to check.
        list2: The second list to check.
        flat_list: The flat list to check.
        expected: The expected result.
    """
    assert check_nested_lists_and_flat_list(list1, list2, flat_list) == expected