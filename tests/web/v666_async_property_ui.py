"""Run the shared real property UI flow with an explicit Task fixture."""
import pathlib,runpy,sys
sys.argv.append('--async-properties')
runpy.run_path(str(pathlib.Path(__file__).with_name('v536_property_set_ui.py')),run_name='__main__')
