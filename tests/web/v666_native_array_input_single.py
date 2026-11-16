"""The same explicit editor retains original native names for existing single value inputs."""
from pathlib import Path
import v666_native_array_input_fixture as x
x.multiple=False
path=Path(__file__).with_name('v666_native_array_input_ui.py')
exec(compile(path.read_text(),str(path),'exec'),{'__name__':'__main__','__file__':str(path)})
