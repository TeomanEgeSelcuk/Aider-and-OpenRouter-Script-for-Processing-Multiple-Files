from Aider_Project.execute_helper import is_nested_empty_list, validate_lengths, check_nested_lists_and_flat_list, generate_and_count_lists, organize_flags # Import helper functions
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
    ([[], []], None, ['a', 'b', 'c'], True),  # Only list1 is checked, and flat_list has enough elements
    ([[], ['a']], None, ['a', 'b'], True),  # Only list1 is checked, and flat_list has enough elements
    ([[], []], None, ['a'], False),  # flat_list does not have enough elements
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

@pytest.mark.parametrize(
    "files_by_directory_values, test_file_names_values, record_output_values, record_test_output_values, run_tests_values, expected_output, raises_exception",
    [
        # Test with all True flags: This test case checks if the function correctly generates lists of True values
        # when all the flags are set to True.
        (
            [['math_functions.py', 'test.py'], ['another_script.py', 'yet_another_test.py']],
            [['test.py'], ['yet_another_test.py']],
            True, True, True,
            ([True, True, True, True], [True, True], [True, True]),  # Expected output lists of True values
            False  # No exception should be raised
        ),
        # Test with all False flags: This test case checks if the function correctly generates lists of False values
        # when all the flags are set to False.
        (
            [['math_functions.py', 'test.py'], ['another_script.py', 'yet_another_test.py']],
            [['test.py'], ['yet_another_test.py']],
            False, False, False,
            ([False, False, False, False], [False, False], [False, False]),  # Expected output lists of False values
            False  # No exception should be raised
        ),
        # Test with Mix flags: This test case checks if the function generates mixed lists of True and False values
        # when the flags are set to "Mix". The exact output cannot be predicted, so we do not provide expected lists.
        (
            [['math_functions.py', 'test.py'], ['another_script.py', 'yet_another_test.py']],
            [['test.py'], ['yet_another_test.py']],
            "Mix", "Mix", "Mix",
            None,  # Output values will be checked separately as they are randomly generated
            False  # No exception should be raised
        ),
        # Test with empty nested lists: This test case checks if the function raises a ValueError when provided with
        # empty nested lists, which are considered invalid inputs.
        (
            [[]],  # Empty nested list for files_by_directory_values
            [[]],  # Empty nested list for test_file_names_values
            True, True, True,
            None,  # Output values expected to raise an error
            True  # A ValueError should be raised
        ),
        # Test with nested empty lists: This test case checks if the function raises a ValueError when provided with
        # nested empty lists (i.e., lists containing empty lists), which are also considered invalid inputs.
        (
            [[[]]],  # Nested empty list for files_by_directory_values
            [[[]]],  # Nested empty list for test_file_names_values
            False, False, False,
            None,  # Output values expected to raise an error
            True  # A ValueError should be raised
        ),
        # Test with non-matching counts: This test case checks if the function correctly handles input lists where the
        # number of files by directory does not match the number of test file names, but both have valid values.
        (
            [['math_functions.py'], ['another_script.py', 'yet_another_test.py']],
            [['test.py'], ['yet_another_test.py']],
            True, True, True,
            ([True, True, True], [True, True], [True, True]),  # Expected output lists of True values
            False  # No exception should be raised
        ),
        # Test with invalid flags: This test case checks if the function raises a ValueError when provided with
        # invalid flag values that are neither "Mix", True, nor False.
        (
            [['math_functions.py', 'test.py'], ['another_script.py', 'yet_another_test.py']],
            [['test.py'], ['yet_another_test.py']],
            "Invalid", "Invalid", "Invalid",
            None,  # Output values expected to raise an error
            True  # A ValueError should be raised
        ),
        # Test with empty input lists: This test case checks if the function raises a ValueError when provided with
        # completely empty input lists, which are invalid inputs.
        (
            [],  # Empty list for files_by_directory_values
            [],  # Empty list for test_file_names_values
            True, True, True,
            None,  # Output values expected to raise an error
            True  # A ValueError should be raised
        ),
        # Test with invalid flag values: This test case checks if the function raises a ValueError when one of the
        # flags is invalid while the others are valid, ensuring robust validation of input flags.
        (
            [['file.py']],  # Valid list for files_by_directory_values
            [['test.py']],  # Valid list for test_file_names_values
            "Invalid", True, True,
            None,  # Output values expected to raise an error
            True  # A ValueError should be raised
        ),
        # Test with mismatched counts of files by directory and test file names: This test case checks if the function
        # can handle cases where the number of directories does not match the number of test file name lists,
        # ensuring correct list generation.
        (
            [['file1.py', 'file2.py'], ['file3.py']],
            [['test1.py'], ['test2.py', 'test3.py']],
            True, False, "Mix",
            None,  # Output values will be checked separately
            False  # No exception should be raised
        ),
    ]
)
def test_generate_and_count_lists(files_by_directory_values, test_file_names_values, record_output_values, record_test_output_values, run_tests_values, expected_output, raises_exception):
    """
    Combined test for generate_and_count_lists function.

    Args:
        files_by_directory_values: List of lists containing file names by directory.
        test_file_names_values: List of lists containing test file names.
        record_output_values: Flag to determine how to generate the record output list. Can be "Mix", True, or False.
        record_test_output_values: Flag to determine how to generate the record test output list. Can be "Mix", True, or False.
        run_tests_values: Flag to determine how to generate the run tests list. Can be "Mix", True, or False.
        expected_output: Expected output of the function.
        raises_exception: Whether the function is expected to raise an exception.
    """
    # Check if we expect an exception to be raised
    if raises_exception:
        with pytest.raises(ValueError):
            # Call the function and expect it to raise ValueError
            generate_and_count_lists(
                files_by_directory_values, test_file_names_values,
                record_output_values, record_test_output_values, run_tests_values
            )
    else:
        # Call the function and store the result
        result = generate_and_count_lists(
            files_by_directory_values, test_file_names_values,
            record_output_values, record_test_output_values, run_tests_values
        )

        # List of input flags and corresponding results to check
        flags_and_results = [
            (record_output_values, result[0], expected_output[0] if expected_output else None),
            (record_test_output_values, result[1], expected_output[1] if expected_output else None),
            (run_tests_values, result[2], expected_output[2] if expected_output else None)
        ]

        # Iterate over each flag and its corresponding result list
        for flag, res_list, expected_list in flags_and_results:
            # If the flag is "Mix", check if all elements are booleans
            if flag == "Mix":
                assert all(isinstance(x, bool) for x in res_list)
            # If the flag is True, check if all elements are True
            elif flag is True:
                assert all(x is True for x in res_list)
            # If the flag is False, check if all elements are False
            elif flag is False:
                assert all(x is False for x in res_list)
            # Verify the output list matches the expected list when flag is True or False
            else:
                assert res_list == expected_list


@pytest.mark.parametrize("directory_paths, files_by_directory, test_file_names, record_output_flag, run_tests_flag, record_test_output_values, expected", [
    # Test Case 1: Regular and test files distributed across two directories
    (
        [r'path\to\codetest', r'path\to\codetest-2'],
        [["file1.py", "file2.py"], ["file3.py"]],
        [["test_file1.py"], ["test_file3.py"]],
        [True, True, False],
        [False, False],
        [False, False],
        {
            'record_output_flag': [[True, True], [False]], 
            'run_tests_flag': [[False], [False]], 
            'record_test_output_values': [[False], [False]]
        }
    ),
    # Test Case 2: Regular files in the first directory and test files in the second
    (
        [r'path\to\codetest', r'path\to\codetest-2'],
        [["file1.py", "file3.py"], ["test_file1.py", "test_file3.py"]],
        [[], ["test_file1.py", "test_file3.py"]],
        [True, True, False, False],
        [True, True],
        [True, True],
        {
            'record_output_flag': [[True, True], [False, False]], 
            'run_tests_flag': [[], [True, True]], 
            'record_test_output_values': [[], [True, True]]
        }
    ),
    # Test Case 3: No test files
    (
        [r'path\to\codetest'],
        [["file1.py", "file2.py"]],
        [[]],
        [True, False],
        [],
        [],
        {
            'record_output_flag': [[True, False]], 
            'run_tests_flag': [[]], 
            'record_test_output_values': [[]]
        }
    ),
    # Test Case 4: Mismatched lengths for record_output_flag
    (
        [r'path\to\codetest', r'path\to\codetest-2'],
        [["file1.py", "file2.py"], ["file3.py"]],
        [["test_file1.py"], ["test_file3.py"]],
        [True, True],  # Incorrect length
        [False, False],
        [False, False],
        "error"
    ),
    # Test Case 5: Mismatched lengths for run_tests_flag and record_test_output_values
    (
        [r'path\to\codetest', r'path\to\codetest-2'],
        [["file1.py", "file2.py"], ["file3.py"]],
        [["test_file1.py"], ["test_file3.py"]],
        [True, True, False],
        [False],  # Incorrect length
        [False, False],
        "error"
    ),
])
def test_organize_flags(directory_paths, files_by_directory, test_file_names, record_output_flag, run_tests_flag, record_test_output_values, expected):
    """
    Test function for `organize_flags`.
    
    This test covers various cases including:
    - Correct organization of flags with different numbers of regular and test files.
    - Validation for mismatched lengths of input lists.
    
    The function uses pytest parameterization to run multiple test cases with different inputs.
    """
    if expected == "error":
        with pytest.raises(ValueError):
            organize_flags(directory_paths, files_by_directory, record_output_flag, run_tests_flag, record_test_output_values, test_file_names)
    else:
        result = organize_flags(directory_paths, files_by_directory, record_output_flag, run_tests_flag, record_test_output_values, test_file_names)
        # Assert the results match the expected values
        assert result == expected