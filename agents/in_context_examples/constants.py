"""
This module contains the directory paths for
1) where examples are located
2) where the editable prompt YAML is located
"""
import os

absolute_dir_path = os.path.dirname(os.path.abspath(__file__))

# The path to the in-context examples
EXAMPLES_PATH = os.path.join(absolute_dir_path, "data")
