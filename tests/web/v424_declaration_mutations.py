"""Pure ordinary host syntax transforms; final source acceptance stays with workspace/compiler CAS."""
import json,subprocess,sys
exe,host=sys.argv[1:]
def edit(source,action,ok=True,**fields):
 reply=subprocess.run([exe,host],input=json.dumps(dict(operation='editDeclaration',text=source,edit=dict(action=action,**fields))),capture_output=True,text=True,timeout=15);assert reply.returncode==0,reply.stderr;result=json.loads(reply.stdout);assert result['ok']==ok,result;return result.get('result')
fn='function Demo::Fn () -> int {description "contract";}'
changed=edit(fn,'signature',value={'args':[{'type':'long','name':'amount'},{'type':'string[]','name':'labels'}],'return':'bool[]'});assert '(long amount, string[] labels) -> bool[]' in changed and 'description "contract";' in changed
for value in [{'args':[{'type':'void','name':'input'}],'return':'int'},{'args':[],'return':'void[]'},{'args':[{'type':'int','name':'calls'}],'return':'int'},{'args':[{'type':'Demo::FakeType','name':'input'}],'return':'int'}]:edit(fn,'signature',False,value=value)
module='module Demo::Module {}'
changed=edit(module,'relations',role='require',entries=[{'id':'Demo::Fn','signature':{'args':[{'type':'int'}],'return':'bool'}}]);assert 'require Demo::Fn (int) -> bool;' in changed
changed=edit(changed,'relations',role='default',entries=[{'function':'Demo::Fn','id':'Demo::Impl'}]);assert 'default Demo::Fn with Demo::Impl;' in changed
changed=edit(changed,'relations',role='provide',entries=[{'function':'Demo::Fn','id':'Demo::Impl'}]);assert 'provide Demo::Fn with Demo::Impl;' in changed
changed=edit(changed,'relations',role='include',entries=[{'id':'Demo::Other'}]);assert 'include Demo::Other;' in changed
changed=edit(changed,'relations',role='require',entries=[]);assert 'require Demo::Fn' not in changed and 'provide Demo::Fn' in changed
edit(module,'relations',False,role='default',entries=[{'function':'Demo::Fn','id':'Demo::Impl'},{'function':'Demo::Fn','id':'Demo::Other'}])
edit(module,'relations',False,role='include',entries=[{'id':'Demo::Other; include Demo::Injected'}])
changed=edit('object Demo::Obj extends Demo::Base {value count = 3; description "note";}','parent',value=None);assert 'extends' not in changed and 'value count = 3;' in changed
changed=edit(changed,'unset-description');assert 'description' not in changed
changed=edit(changed,'unset-value',field='count');assert 'value count' not in changed
edit('object Demo::Obj {}','unset-value',False,field='inherited')
schema='schema Demo::Schema {field one single general int;field two single general bool;}'
changed=edit(schema,'field-order',order=['two','one']);assert changed.index('field two')<changed.index('field one');changed=edit(changed,'remove-field',field='one');assert 'field one' not in changed and 'field two' in changed
edit(schema,'field-order',False,order=['two','two']);edit('object Demo::Obj {}','remove-field',False,field='one')
obj='object Demo::Obj {data ticks = [0, 1, 2];data nested = { enabled = false; note = ""; };}'
changed=edit(obj,'move-data',path=['ticks'],**{'from':2,'to':0});assert 'data ticks = [2, 0, 1];' in changed
changed=edit(changed,'unset-data',path=['nested','enabled']);assert 'enabled =' not in changed and 'note = "";' in changed
changed=edit(changed,'unset-data',path=['ticks',1]);assert 'data ticks = [2, 1];' in changed
edit('object Demo::Child extends Demo::Base {}','unset-data',False,path=['inherited','field']);edit(obj,'move-data',False,path=['ticks'],**{'from':3,'to':0});edit(fn,'rename',False,id='Demo::Other')
changed=edit('implementation Demo::Impl for Demo::Fn () -> int {body common "code.csbody";}','signature',value={'args':[],'return':'void'});assert '() -> void' in changed and 'body common "code.csbody";' in changed
changed=edit(changed,'relations',role='import',entries=[{'id':'Demo::Other','alias':'Other','scope':None,'signature':{'args':[],'return':'int'}}]);assert 'import Demo::Other as Other () -> int;' in changed
changed=edit(fn,'properties',values={'displayName':'이름','icon':'◇','description':'내용','parent':None});assert 'editorName =' in changed and 'description' in changed and 'Demo::Fn' in changed
print('PASS declaration mutation host: real signature/relations/parent/reset/order/array transforms; type/ID/inherited/scope/unsupported edits refused')
