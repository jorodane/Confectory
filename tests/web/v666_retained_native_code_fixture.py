"""An existing nominal C# node retained across an explicit root ABI edit."""
import copy,json
import v666_blueprint_entry_fixture as b
x,f,e,owner,fn=b.x,b.f,b.e,b.owner,b.fn
payload=b.payload;old=dict(args=[dict(name='amount',type='int'),dict(name='data',type=payload)],**{'return':'int'});new=dict(args=[dict(name='amount',type=payload)],**{'return':payload})
graph_id,graph_path,body_id,body_path,impl_path=b.graph_id,b.graph_path,b.body_id,b.body_path,b.impl_path
code_id=graph_id+'/node:transform';code_path='retained.node.json';use_exit=b.use_exit
for path in [e.path,f.project/impl_path]:path.write_text(path.read_text().replace('(int amount)','(int amount,'+payload+' data)'))
(f.project/'MainBody.celem').write_text((f.project/'MainBody.celem').read_text().replace('(int) -> int','(int,'+payload+') -> int'))
original='int result=calls.Connected.Invoke(30,new '+payload+' {Value=new '+b.leaf+' {Count=30}});Console.WriteLine(result);return result; // 원래 호출자 · 😀\r\n'
selected='var value=calls.Connected.Invoke(new '+payload+' {Value=new '+b.leaf+' {Count=30}});int result=checked((int)value.Value.Count);Console.WriteLine(result);return result; // 명시 호출자 대응 · 😀\r\n';(f.project/body_path).write_bytes(original.encode())
code_source='return Increment(data); // 보존하는 원래 C# · 😀\r\n';code_helpers='static '+payload+' Increment('+payload+' value) {value.Value.Count=checked(value.Value.Count+1);return value;} // 원래 helpers\r\n'
code=dict(id='transform',kind='code',control='next',intent='보존하는 정보 값 계산',signature=dict(args=[dict(name='data',type=payload)],**{'return':payload}),arguments=dict(data=dict(input='data')),implementation=code_path,x=128,y=104)
graph=copy.deepcopy(b.graph);graph.update(profile='sync-acyclic-methods-v1',contractHash=b.fingerprint(old),entry='transform',nodes=[code]+([]if use_exit else[b.graph['nodes'][0]]),edges=[{'from':'transform','port':'next','to':'exit:return'if use_exit else'publish'}]);(f.project/graph_path).write_text(json.dumps(graph,ensure_ascii=False))
defs=f.metadata('featureBlueprintNodes',featureSource=e.path.read_text(),graph=graph);assert defs['state']=='node-definitions',defs
record=dict(schema=1,node='transform',definitionHash=next(row['definitionHash']for row in defs['nodes']if row['id']=='transform'),source=code_source,helpers=code_helpers);code_bytes=(json.dumps(record,ensure_ascii=False,indent=2)+'\r\n').encode();(f.project/code_path).write_bytes(code_bytes)
x.original={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts};changes_allowed=b.changes_allowed
catalog=b.catalog;execute=b.execute

def request(c=None):
 c=c or catalog();request=b.request(c);edit=request['declaration']['changes'][0];edit.update(signature=new);edit['mapping']['before']=old;edit['mapping']['args']=dict(amount=None,data=None);body=c['functionBodies'][body_id];edit['mapping']['bodies'][body_id].update(text=selected,contract=new)
 for key,t in c['functionOutputs'].items():edit['mapping']['outputs'][key].update(source=dict(node='transform',output='return'))
 plans={key:{k:t[k]for k in ['graph','node','argument','hash','before']}|dict(value=dict(input='amount'))for key,t in c['functionInputUses'].items()if t['node']=='transform'and t['argument']=='data'};assert len(plans)==1;edit['mapping']['implementations']=plans;return request

def verify(checkpoint,signature=None):
 d=json.loads(checkpoint.read_text());rows={r['id']:r for r in d['changes']};assert d['version']==2;assert rows[body_id]['draft'].replace('\r\n','\n').strip()==selected.replace('\r\n','\n').strip();actual=json.loads(rows[graph_id]['draft']);expected=copy.deepcopy(graph);expected['contractHash']=b.fingerprint(new);expected['nodes'][0]['arguments']['data']={'input':'amount'}
 if use_exit:expected['exits']['return']={'node':'transform','output':'return'}
 else:expected['nodes'][1]['signature']['args'][0]['type']=payload;expected['nodes'][1]['arguments']['value']={'node':'transform','output':'return'}
 assert actual==expected,(actual,expected);assert code_id not in rows and(f.project/code_path).read_bytes()==code_bytes;receipt=rows[owner]['slotSaveReceipt'];assert '$function:'+fn in receipt['nativeTypeProofs'];assert code_path in receipt['readGuards']or any(row['path']==str(f.project/code_path)for row in receipt.get('nativeTypeReads',[]));return rows[owner]['atomicEditGroup']
