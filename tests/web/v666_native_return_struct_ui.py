"""Original return type picker and explicit C# editors; no automatic source conversion."""
import sys,json
from pathlib import Path
import v666_native_return_struct_fixture as x
sys.modules['v666_native_type_group_fixture']=x
path=Path(__file__).with_name('v666_native_type_group_ui.py');text=path.read_text();assert text.count('[data-signature-kind=inputs] .feature-io-row')==2;text=text.replace('[data-signature-kind=inputs] .feature-io-row','[data-signature-id=return]')
if len(sys.argv)>3 and sys.argv[3]=='alias-reproduce':
 anchor="source=dialog.locator('[data-code-source]');old=x.sources[id]"
 replacement="source=dialog.locator('[data-code-source]');value=source.input_value();wanted='public '+plan['signature']['return']+' Invoke(int nativeAmount)';(f.case/'alias-declaration.json').write_text(json.dumps(dict(wanted=wanted,observed=value.split('\\n',1)[0]),ensure_ascii=False,indent=2));assert wanted not in value and ' Invoke(int amount)'in value;f.checked('reproduced unchanged native argument alias replaced in a nominal return editor declaration before Save; original data unchanged');x.unchanged();f.browser.close();raise SystemExit(0);old=x.sources[id]"
 assert text.count(anchor)==1;text=text.replace(anchor,replacement)
original_checked=x.f.checked
def checked(message):return original_checked(message.replace('four selected C# bodies','three unique C# bodies from four explicit selections').replace('four authored body plans','four explicit selections for three unique sources'))
x.f.checked=checked
exec(compile(text,str(path),'exec'),{'__name__':'__main__','__file__':str(path)})
