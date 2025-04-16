"""
This script version controls a prompt by producing a prompt YAML under `prompts` based on the one in `sandbox`

Refer to `prompt_builder/docs` to understand the appropriate structure of the prompt YAML.

To run this script, make sure `sandbox` contains the updated prompt and run the following command in the terminal:
    python builder_script.py
"""
import os
import sys
import yaml

from constants import PROMPT_PATH, PROMPT_HISTORY_PATH
import serializer
import utils

def get_metadata_from_yaml(prompt_dict):
    """
    Retrieves prompt metadata used to version control from the loaded YAML dictionary.

    Parameters:
        prompt_dict (dict)
            The prompt dictionary from a YAML.
    
    Returns:
        experiment_name (str)
            The name of the experiment for the prompt.
        prompt_description (str)
            The description of the prompt.
        prompt_version (str)
            The version of the prompt.
    
    Raises:
        NotImplementedError
            If the prompt version is not supported.
    """
    version = prompt_dict["version"]
    if version == "1.0.0":
        experiment_name = prompt_dict["experiment_name"]
        prompt_description = prompt_dict["prompt_description"]
        prompt_version = prompt_dict["prompt_version"]
    else:
        raise NotImplementedError("Prompt parsing version not supported.")
    return experiment_name, prompt_description, prompt_version

def save_prompt():
    """Saves the prompt to the version control directory.

    Side Effects:
        - Writes the prompt YAML to the version control directory.
    """
    experiment_name, prompt_description, prompt_version = get_metadata_from_yaml(prompt_dict)
    experiment_directory = utils.get_experiment_directory(PROMPT_HISTORY_PATH, experiment_name)
    os.makedirs(experiment_directory, exist_ok=True) # Create directory if it doesn't exist

    # Write prompt YAML to version control directory
    versioned_prompt_path = utils.get_prompt_path(PROMPT_HISTORY_PATH, experiment_name, prompt_description, prompt_version)
    os.system("cp {} {}".format(PROMPT_PATH, versioned_prompt_path))

if __name__ == "__main__":
    # 1) Read prompt information from YAML
    print("Reading from YAML file...")
    with open(PROMPT_PATH, "r") as f:
        prompt_dict = yaml.safe_load(f)
    
    # 1.1) Check if prompt already exists
    experiment_name, prompt_description, prompt_version = get_metadata_from_yaml(prompt_dict)
    if utils.check_if_prompt_exists(PROMPT_HISTORY_PATH, experiment_name, prompt_description, prompt_version):
        if input("Prompt already exists. Do you want to overwrite it? (y/n) ") != "y":
            sys.exit()
    
    # 2) Validate prompt YAML
    print("Validating prompt YAML...")
    major, minor, patch = prompt_version.split(".")
    if major == "1": # e.g. 1.0.0
        serializer.prompt_validator_v1(prompt_dict)
    else:
        raise NotImplementedError("Prompt parsing version not supported.")

    # 3) Write prompt YAML to directory
    print("Version controlling prompt YAML...")
    save_prompt()