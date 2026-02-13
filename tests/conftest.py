from pathlib import Path
import sys

# Make project root importable so tests can `from src ...`
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
