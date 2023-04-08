# Import Libraries
import os
import importlib

# Get the current directory.
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get all files in the current directory.
views = [f for f in os.listdir(current_dir) if f.endswith(".py") and f != "__init__.py"]

# Import all files from modules folder.
for view in views:
    # Get the parent folder name.
    parent_folder = os.path.split(current_dir)[-1]

    # Create the module name by removing the '.py' extension from the file name.
    module_name = view[:-3]

    # Import the module using the parent folder and module name.
    importlib.import_module(f"{parent_folder}.{module_name}")
