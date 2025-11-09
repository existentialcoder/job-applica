import os
import sys
from pathlib import Path
from importlib import import_module

from ..db.base_class import Base 

current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

for file in os.listdir(current_dir):
    if file.endswith('.py') and file != '__init__.py':
        module_name = file[:-3]  # remove .py
        import_module(f".{module_name}", package="src.models")
