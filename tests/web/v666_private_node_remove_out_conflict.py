"""Stable owned helper beside explicit private out-deletion/source plans."""
import pathlib,runpy,sys
import v666_private_node_remove_out_fixture as x
sys.modules["v666_private_scalar_return_fixture"]=x
runpy.run_path(str(pathlib.Path(__file__).with_name("v666_private_scalar_return_conflict.py")),run_name="__main__")
