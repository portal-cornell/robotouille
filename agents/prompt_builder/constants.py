"""
This module contains the directory paths for
1) where prompts are version-controlled
2) where the editable prompt YAML is located
"""
import os

absolute_dir_path = os.path.dirname(os.path.abspath(__file__))

# The path to the version-controlled prompts
PROMPT_HISTORY_PATH = os.path.join(absolute_dir_path, "prompts")

# The path to the sandbox directory containing the prompt.yml
SANDBOX_DIR_PATH = os.path.join(absolute_dir_path, "sandbox")

# The path to the prompt YAML
PROMPT_PATH = os.path.join(SANDBOX_DIR_PATH, "prompt.yml")
