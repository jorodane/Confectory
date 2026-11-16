"""Original return type picker and explicit C# editors; no automatic source conversion."""
import sys,json
from pathlib import Path
import v666_native_reference_return_fixture as x
sys.modules['v666_native_type_group_fixture']=x
path=Path(__file__).with_name('v666_native_type_group_ui.py');text=path.read_text().replace("pick(field,f.n+'Payload')","pick(field,f.n+'Leaf',x.multiple)");assert text.count('[data-signature-kind=inputs] .feature-io-row')==2;text=text.replace('[data-signature-kind=inputs] .feature-io-row','[data-signature-id=return]')
text=text.replace("p.locator('[data-native-type]').filter(has_text=id).click()","p.locator('[data-reference-type][title=\"'+id+'\"]').click()")
original_checked=x.f.checked
def checked(message):return original_checked(message.replace('four selected C# bodies','three unique C# bodies from four explicit selections').replace('four authored body plans','four explicit selections for three unique sources'))
x.f.checked=checked
exec(compile(text,str(path),'exec'),{'__name__':'__main__','__file__':str(path)})
