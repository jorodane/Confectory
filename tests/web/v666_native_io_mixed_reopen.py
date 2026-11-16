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
text=text.replace('for fn,plan in zip(x.functions,planned):','for fn,plan in reversed(list(zip(x.functions,planned))):')
original_checked=x.f.checked
def checked(message):return original_checked(message.replace('four selected C# bodies','three unique C# bodies from four explicit selections').replace('four authored body plans','four explicit selections for three unique sources'))
x.f.checked=checked
anchor='  held=pending();assert len(held)==2'
insertion='  fn=x.second;original_pending=pending()\n  def open_retained():\n   row().locator(\'[data-function-write-direct],[data-function-edit]\').first.click();f.page.locator(\'[data-information-body="\'+x.bodies[x.first]+\'"]\').click();dialog=f.page.locator(\'.bp-script-dialog\');expect(dialog).to_be_visible();return dialog\n  dialog=open_retained();value=dialog.locator(\'[data-code-source]\').input_value();sig=planned[0][\'mapping\'][\'bodies\'][x.bodies[x.first]][\'signature\'];wanted=\'public \'+sig[\'return\']+\' Invoke(\'+sig[\'args\'][0][\'type\']+\' nativeAmount)\';(f.case/\'reopen-declaration.json\').write_text(json.dumps(dict(wanted=wanted,observed=value.split(\'\\\\n\',1)[0],source=x.bodies[x.first]),ensure_ascii=False,indent=2))\n  if mode==\'reproduce-reopen\':\n   assert wanted not in value and \'public int Invoke(int nativeAmount)\'in value;f.checked(\'reproduced stale retained caller declaration after reverse-order explicit nominal editing; no Save or original writes\');x.unchanged();f.browser.close();raise SystemExit(0)\n  assert wanted in value;dialog.locator(\'[data-code-cancel]\').click();assert pending()==original_pending;x.unchanged();dialog=open_retained();assert wanted in dialog.locator(\'[data-code-source]\').input_value();dialog.locator(\'[data-code-save]\').click();expect(dialog).to_have_count(0);f.idle();assert pending()!=original_pending\n  edits={v[\'id\']:v for _,v in pending()};assert edits[x.second][\'mapping\'][\'bodies\'][x.bodies[x.first]][\'signature\']==edits[x.first][\'mapping\'][\'bodies\'][x.bodies[x.first]][\'signature\'];f.checked(\'explicitly reopening B shows A authored current declaration; cancel preserves the old plan and explicit code Save accepts the matching declaration\')\n  held=pending();assert len(held)==2'
assert text.count(anchor)==1
exec(compile(text.replace(anchor,insertion),str(path),'exec'),{'__name__':'__main__','__file__':str(path)})
