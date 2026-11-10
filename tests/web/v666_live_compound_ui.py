from pathlib import Path
import runpy,sys
sys.argv.append('--live-compound-properties')
runpy.run_path(str(Path(__file__).with_name('v536_property_set_ui.py')),run_name='__main__')
