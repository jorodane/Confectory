"""Existing authored property UI over real enum fields; no synthetic UI controls."""
from pathlib import Path
import runpy,sys
sys.argv.append('--live-enum-properties')
runpy.run_path(str(Path(__file__).with_name('v536_property_set_ui.py')),run_name='__main__')
