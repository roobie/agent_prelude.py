import sys
from pathlib import Path

# Ensure project src/ is on sys.path so tests can import the installed package during development
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
# Also keep project root for legacy imports
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
