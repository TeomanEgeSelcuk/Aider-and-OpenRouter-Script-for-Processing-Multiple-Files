# Aider LLM File Editor

**A script-based tool for sequentially editing files, running scripts and their tests, and recording outputs, including errors and exceptions, directly from the terminal.**

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Using Conda](#using-conda)
  - [Using Poetry](#using-poetry)
- [Setup](#setup)
  - [Environment Variables](#environment-variables)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

## Overview

Aider LLM File Editor is a powerful tool designed to automate the process of editing Python files, executing scripts, running associated tests, and recording their outputs. Leveraging OpenRouter models with `aider-chat`, this tool streamlines your workflow by handling multiple directories and files efficiently. Whether you're developing, testing, or debugging, Aider LLM File Editor simplifies your tasks directly from the terminal.

## Features

- **Automated File Editing**: Sequentially edit multiple Python files based on provided instructions.
- **Script Execution**: Run Python scripts across various directories and capture their outputs.
- **Test Management**: Execute test files using `pytest` and record their results.
- **Output Recording**: Log standard outputs and error messages from both scripts and tests.
- **Cross-Platform Support**: Compatible with Mac, Linux, and Windows operating systems.
- **Environment Management**: Supports both Conda and Poetry for dependency management.

## Prerequisites

Before setting up the project, ensure you have the following installed on your system:

- **Python**: Version 3.12.x
- **Conda** (optional, for environment management)
- **Poetry** (optional, for dependency management)

## Installation

### Using Conda

1. **Clone the Repository**

   ```bash
   git clone https://github.com/TeomanEgeSelcuk/Aider-and-OpenRouter-Script-for-Processing-Multiple-Files.git
   cd Aider-and-OpenRouter-Script-for-Processing-Multiple-Files
   ```

2. **Create and Activate the Conda Environment**

   ```bash
   conda env create -f environment.yml
   conda activate openrouter-aider-env
   ```

3. **Install Dependencies**

   ```bash
   pip install poetry
   poetry install
   ```

### Using Poetry

1. **Clone the Repository**

   ```bash
   git clone https://github.com/TeomanEgeSelcuk/Aider-and-OpenRouter-Script-for-Processing-Multiple-Files.git
   cd Aider-and-OpenRouter-Script-for-Processing-Multiple-Files
   ```

2. **Install Poetry**

   If you don't have Poetry installed, you can install it using pip:

   ```bash
   pip install poetry
   ```

3. **Install Dependencies**

   ```bash
   poetry install
   ```

4. **Activate the Poetry Environment**

   ```bash
   poetry shell
   ```

## Setup

### Environment Variables

The project relies on the `OPENROUTER_API_KEY` for authenticating with OpenRouter models. Follow these steps to set it up:

1. **Obtain Your OpenRouter API Key**

   Register or log in to [OpenRouter](https://openrouter.ai/) to obtain your API key.

2. **Set the Environment Variable**

   - **Mac/Linux**

     Add the following line to your `~/.bashrc`, `~/.zshrc`, or corresponding shell configuration file:

     ```bash
     export OPENROUTER_API_KEY='your-api-key-here'
     ```

     Then, reload the shell configuration:

     ```bash
     source ~/.bashrc
     # or
     source ~/.zshrc
     ```

   - **Windows**

     Set the environment variable using Command Prompt:

     ```cmd
     setx OPENROUTER_API_KEY "your-api-key-here"
     ```

     Or using PowerShell:

     ```powershell
     [System.Environment]::SetEnvironmentVariable('OPENROUTER_API_KEY', 'your-api-key-here', 'User')
     ```

## Usage

After setting up the environment and installing dependencies, you can start using the Aider LLM File Editor.

1. **Prepare Your Directories and Files**

   Organize the directories and Python files you wish to edit and test.

2. **Run the Execute Function**

   You can run the `execute` function from `main.py` with the appropriate arguments. Here's a basic example:

   ```bash
   python main.py
   ```

   **Example Usage in Python:**

   ```python
   from Aider_Project.main import execute

   directory_paths = ["dir1", "dir2"]
   files_by_directory = [["file1.py", "file2.py"], ["file3.py"]]
   model = "your-openrouter-model"
   record_output_flag = [True, True]
   run_tests_flag = [False, False]

   execute(
       directory_paths=directory_paths,
       files_by_directory=files_by_directory,
       model=model,
       record_output_flag=record_output_flag,
       run_tests_flag=run_tests_flag
   )
   ```

3. **Verbose Mode**

   For detailed logs, enable the `verbose` flag:

   ```python
   execute(
       directory_paths=directory_paths,
       files_by_directory=files_by_directory,
       model=model,
       record_output_flag=record_output_flag,
       run_tests_flag=run_tests_flag,
       verbose=True
   )
   ```

## Project Structure

```
Aider-and-OpenRouter-Script-for-Processing-Multiple-Files/
├── Aider_Project/
│   ├── __init__.py
│   ├── execute_helper.py
│   ├── main.py
│   ├── runner.py
│   ├── utils.py
├── tests/
│   ├── __init__.py
│   ├── test_execute_helper.py
│   ├── test_main.py
│   ├── test_runner.py
│   ├── test_utils.py
├── .gitignore
├── environment.yml
├── poetry.lock
├── pyproject.toml
├── pytest.ini
└── README.md
```

- **Aider_Project/**: Contains the main source code.
  - **main.py**: Entry point with the `execute` function.
  - **utils.py**: Utility functions like `get_openrouter_api_key` and `list_files`.
  - **execute_helper.py**: Helper functions for validation and flag organization.
  - **runner.py**: Functions to run scripts and record outputs.
- **tests/**: Contains test cases for the project.
- **pyproject.toml**: Poetry configuration file managing dependencies.
- **environment.yml**: Conda environment configuration.
- **README.md**: Project documentation.
- **.gitignore**: Specifies files and directories to ignore in git.

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Repository**

2. **Create a New Branch**

   ```bash
   git checkout -b feature/YourFeature
   ```

3. **Commit Your Changes**

   ```bash
   git commit -m "Add your feature"
   ```

4. **Push to the Branch**

   ```bash
   git push origin feature/YourFeature
   ```

5. **Open a Pull Request**

   Describe your changes and submit the pull request for review.

---

**Author**: Teoman Selcuk  
**Email**: [teomanege.selcuk@gmail.com](mailto:teomanege.selcuk@gmail.com)

---
