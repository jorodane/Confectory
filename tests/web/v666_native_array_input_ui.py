"""Original multiple input type picker and explicit C# editors; no automatic source conversion."""
import sys,json
from pathlib import Path
import v666_native_array_input_fixture as x
sys.modules['v666_native_type_group_fixture']=x
path=Path(__file__).with_name('v666_native_type_group_ui.py');text=path.read_text();assert text.count("pick(field,f.n+'Payload')")==2;text=text.replace("pick(field,f.n+'Payload')","pick(field,f.n+'Payload',x.multiple)")
if len(sys.argv)>3 and sys.argv[3]=='alias-reproduce':
 anchor="source=dialog.locator('[data-code-source]');old=x.sources[id]"
 replacement="source=dialog.locator('[data-code-source]');value=source.input_value();sig=plan['mapping']['bodies'][id]['signature'];wanted='public '+sig['return']+' Invoke('+sig['args'][0]['type']+' '+sig['args'][0]['name']+')';(f.case/'alias-declaration.json').write_text(json.dumps(dict(wanted=wanted,observed=value.split('\\n',1)[0]),ensure_ascii=False,indent=2));assert wanted not in value and (' Invoke('+sig['args'][0]['type']+' amount)')in value;assert checkpoint.read_bytes()==before;f.checked('reproduced nominal input declaration using public name instead of original native alias before Save; checkpoint and source unchanged');x.unchanged();f.browser.close();raise SystemExit(0);old=x.sources[id]"
 assert text.count(anchor)==1;text=text.replace(anchor,replacement)
original_checked=x.f.checked
def checked(message):return original_checked(message.replace('four selected C# bodies','three unique C# bodies from four explicit selections').replace('four authored body plans','four explicit selections for three unique sources'))
x.f.checked=checked
exec(compile(text,str(path),'exec'),{'__name__':'__main__','__file__':str(path)})
