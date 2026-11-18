"""Existing role/source DOM checks with original opaque-caller metadata.

Metadata is controlled; actual engine, compiler and transaction checks run separately.
"""
from pathlib import Path
path=Path(__file__).with_name('v666_private_callee_value_out_renderer.py')
source=path.read_text();marker="privateCaller:{sourceKind:'scoped-code-csharp',caller:true,name:'원래 private caller'}";assert source.count(marker)==1
source=source.replace(marker,"privateCaller:{sourceKind:'whole-caller-csharp',caller:true,name:'원래 opaque caller'}")
exec(compile(source,str(path),'exec'),dict(__name__='__main__',__file__=str(path)))
