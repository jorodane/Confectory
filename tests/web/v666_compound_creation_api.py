"""The saved full owner plan keeps the same existing final source lease."""
import pathlib,runpy,sys
import v666_compound_creation_fixture as x
sys.modules['v666_field_contracts_fixture']=x
runpy.run_path(str(pathlib.Path(__file__).with_name('v666_field_contracts_api.py')),run_name='__main__')
