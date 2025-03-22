"""
This module contains utilities for constructing file names and retrieving file paths for prompts.
"""
import os

def get_prompt_file_name(prompt_version, prompt_description):
    """Constructs the prompt file name.

    Parameters:
        prompt_version (str)
            The version of the prompt.
        prompt_description (str)
            The description of the prompt.
    
    Returns:
        str: The prompt file name.
    """
    return f"{prompt_version}-{prompt_description}.yml"

def get_experiment_directory(prompt_history_path, experiment_name):
    """Constructs the experiment directory.

    Parameters:
        prompt_history_path (str)
            The path to the prompt history.
        experiment_name (str)
            The name of the experiment for the prompt.
    
    Returns:
        str: The experiment directory.
    """
    return os.path.join(prompt_history_path, experiment_name)

def get_prompt_path(prompt_history_path, experiment_name, prompt_description, prompt_version):
    """Constructs the prompt path.

    Parameters:
        prompt_history_path (str)
            The path to the prompt history.
        experiment_name (str)
            The name of the experiment for the prompt.
        prompt_description (str)
            The description of the prompt.
        prompt_version (str)
            The version of the prompt.

    Returns:
        str: The prompt path.
    """
    experiment_directory = get_experiment_directory(prompt_history_path, experiment_name)
    prompt_file_name = get_prompt_file_name(prompt_version, prompt_description)
    return os.path.join(experiment_directory, prompt_file_name)

def check_if_prompt_exists(prompt_history_path, experiment_name, prompt_description, prompt_version):
    """Checks if a prompt already exists.

    Parameters:
        prompt_history_path (str)
            The path to the prompt history.
        experiment_name (str)
            The name of the experiment for the prompt.
        prompt_description (str)
            The description of the prompt.
        prompt_version (str)
            The version of the prompt.

    Returns:
        bool: True if the prompt exists, False otherwise.
    """
    prompt_path = get_prompt_path(prompt_history_path, experiment_name, prompt_description, prompt_version)
    return os.path.exists(prompt_path)