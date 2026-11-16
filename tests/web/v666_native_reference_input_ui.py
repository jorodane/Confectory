"""Original multiple input type picker and explicit C# editors; no automatic source conversion."""
import sys,json
from pathlib import Path
import v666_native_reference_input_fixture as x
sys.modules['v666_native_type_group_fixture']=x
path=Path(__file__).with_name('v666_native_type_group_ui.py');text=path.read_text();assert text.count("pick(field,f.n+'Payload')")==2;text=text.replace("pick(field,f.n+'Payload')","pick(field,f.n+'Leaf',x.multiple)").replace("p.locator('[data-native-type]')","p.locator('[data-reference-type]')")
text=text.replace("p.locator('[data-reference-type]').filter(has_text=id).click()","p.locator('[data-reference-type][title=\"'+id+'\"]').click()")
original_checked=x.f.checked
def checked(message):return original_checked(message.replace('four selected C# bodies','three unique C# bodies from four explicit selections').replace('four authored body plans','four explicit selections for three unique sources'))
x.f.checked=checked
exec(compile(text,str(path),'exec'),{'__name__':'__main__','__file__':str(path)})
