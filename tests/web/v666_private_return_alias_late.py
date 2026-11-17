"""Original scalar-return regression with distinct native aliases."""
import pathlib,runpy,sys
import v666_private_return_alias_fixture as x
sys.modules["v666_private_scalar_return_fixture"]=x
runpy.run_path(str(pathlib.Path(__file__).with_name("v666_private_scalar_return_late.py")),run_name="__main__")
