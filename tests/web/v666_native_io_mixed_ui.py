"""Original explicit IO controls and C# editors with independent selected signatures."""
import sys,json
from pathlib import Path
import v666_native_io_mixed_fixture as x
sys.modules['v666_native_type_group_fixture']=x
path=Path(__file__).with_name('v666_native_type_group_ui.py');text=path.read_text()
anchor="field=p.locator('[data-signature-kind=inputs] .feature-io-row').first;pick(field,f.n+'Payload')";assert text.count(anchor)==2;text=text.replace(anchor,'choose(p,plan)')
choice="""def choose(p,plan):
 id=f.n+('Payload'if x.io_case=='value'else'Leaf');multiple=x.io_case!='value'
 if plan['signature']['args'][0]['type']!='int':pick(p.locator('[data-signature-kind=inputs] .feature-io-row').first,id,multiple)
 if plan['signature']['return']!='int':pick(p.locator('[data-signature-id=return]'),id,multiple)
"""
text=text.replace('def save(ok=True):',choice+'def save(ok=True):')
text=text.replace("p.locator('[data-native-type]').filter(has_text=id).click()","(p.locator('[data-native-type]').filter(has_text=id) if x.io_case=='value'else p.locator('[data-reference-type][title=\"'+id+'\"]')).click()")
original_checked=x.f.checked
def checked(message):return original_checked(message.replace('four selected C# bodies','three unique C# bodies from four explicit selections').replace('four authored body plans','four explicit selections for three unique sources'))
x.f.checked=checked
exec(compile(text,str(path),'exec'),{'__name__':'__main__','__file__':str(path)})
