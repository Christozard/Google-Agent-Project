import sys
import os

# Add project root to path for all imports
# When run from any subdirectory, this ensures src is importable
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _project_root)