"""Reuse the existing real editor lifecycle over the composed schema fixture."""
from pathlib import Path
import runpy,sys
import v666_information_compound_fixture
kind='api'if'--api'in sys.argv else'ui'
runpy.run_path(str(Path(__file__).with_name('v666_information_struct_'+kind+'.py')),run_name='__main__')
