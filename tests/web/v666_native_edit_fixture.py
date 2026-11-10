"""Existing physical, unused owned function; original bodies stay untouched."""
import copy,json
import v666_function_types_fixture as x
f,owner=x.f,x.owner
fn=owner+'_Function_'+'e'*32
local=fn.split('::')[1];path=f.project/('elements/'+local+'.celem');path.parent.mkdir(exist_ok=True)
path.write_bytes(('function '+fn+' (int amount) -> int {value editorName="타입 전환";}\r\n').encode())
p=f.project/'FreeInfo.celem';p.write_text(p.read_text().replace('{','{contain function '+fn+';',1))
f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element '+local+' function "elements/'+local+'.celem";registry Confectory.Build.DotNet',1))
(f.project/'Consumer.celem').write_text('module '+f.n+'Consumer {}')
f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element Consumer module "Consumer.celem";registry Confectory.Build.DotNet',1))
x.original={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()}
def catalog():
 f.invoke('schema',dict(id=owner));s=f.state()['schema'];return f.invoke('blueprint',dict(action='readOwnerEdits',id=owner,hash=s['textHash'],includeNativeTypes=True,nativeFunction=fn))['result']['result']
def request(c=None):
 c=c or catalog();req=x.request(c);row=req['declaration']['changes'][0];method=next(m for m in f.state()['schema']['ownFunctions']if m['id']==fn);row.update(type='function-edit',id=fn,hash=method['hash'],mapping=dict(before=dict(args=[dict(name='amount',type='int')],**{'return':'int'}),args=dict(amount=None)));row['nativeTypes']['$function:'+fn]=copy.deepcopy(c['nativeFunctionEdit']['proof']);return req
def verify(checkpoint,signature):
 ids=x.verify(checkpoint,fn,signature);rows={r['id']:r for r in json.loads(checkpoint.read_text())['changes']};assert '$function:'+fn in rows[owner]['slotSaveReceipt']['nativeTypeProofs'];assert 'elements/'+local+'.celem'in rows[owner]['slotSaveReceipt']['readGuards'];return ids
