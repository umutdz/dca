import sys
from pathlib import Path

# Get the project root directory
project_root = str(Path(__file__).parent.parent)

# Add the project root directory to the Python path
sys.path.insert(0, project_root)
