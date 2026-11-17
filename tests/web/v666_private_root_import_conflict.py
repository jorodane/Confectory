"""Stable owned helper beside explicit private/scalar-return plans."""
import pathlib,runpy,sys
import v666_private_root_import_fixture as x
sys.modules["v666_private_scalar_return_fixture"]=x
runpy.run_path(str(pathlib.Path(__file__).with_name("v666_private_scalar_return_conflict.py")),run_name="__main__")
