import os
from pathlib import Path
from typing import List

def get_openrouter_api_key() -> str:
    """
    Get the OPENROUTER_API_KEY from environment variables.

    Raises:
        ValueError: If the OPENROUTER_API_KEY environment variable is not set.

    Returns:
        str: The OPENROUTER_API_KEY.
    """
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set.")
    return api_key

def list_files(directory: str, print_files: bool = False) -> List[str]:
    """
    List all files in the given directory.

    Args:
        directory (str): The directory to list files from.
        print_files (bool): Whether to print the files. Defaults to False.

    Raises:
        ValueError: If the provided directory is not valid.

    Returns:
        List[str]: A list of file names in the directory.
    """
    # Create a Path object for the specified directory
    p = Path(directory)
    # Check if the path does not represent a directory
    if not p.is_dir():
        # If not, raise an error indicating the problem
        raise ValueError(f"{directory} is not a valid directory.")
    # List all files in the directory and its subdirectories
    files = [str(file.name) for file in p.rglob('*') if file.is_file()]
    
    if print_files:
        print(f"Directory: {Path(directory).resolve()}")
        print("Files in the directory:")
        for file in files:
            print(f"    {file}")
    
    return files
