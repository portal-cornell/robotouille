import sys
import os
file_path = os.path.dirname(os.path.abspath(__file__))
if file_path not in sys.path:
   sys.path.append(file_path)