from pathlib import Path
import v666_native_io_mixed_fixture as x
x.io_case='both'
path=Path(__file__).with_name("v666_native_io_mixed_ui.py")
exec(compile(path.read_text(),str(path),"exec"),{"__name__":"__main__","__file__":str(path)})
