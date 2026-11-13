"""Original owner hotkeys keep rejection separate from browser/native text history."""
import pathlib,runpy,sys
check=next((a.removeprefix('--check=')for a in sys.argv if a.startswith('--check=')),'ui')
runpy.run_path(str(pathlib.Path(__file__).with_name('v666_owner_history_'+check+'.py')),run_name='__main__')
