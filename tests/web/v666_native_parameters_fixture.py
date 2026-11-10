"""Observed nominal root or owned private code, stable original function contract."""
import copy,json,sys
import v666_retained_native_code_fixture as c
f,x,e=c.f,c.x,c.e
payload=c.payload;private='private'in sys.argv[4:];graph_id=c.graph_id;frame_id=graph_id+('/graph:private'if private else'');code_id=graph_id+('/node:private'if private else'')+'/node:transform';code_path=c.code_path
old=copy.deepcopy(c.old);old['return']=payload
mood,rules=c.b.native(f.n+'Mood'),c.b.native(f.n+'NativeRules');old['args']+=[dict(name='choice',type=mood),dict(name='services',type=rules)]
for path in [e.path,f.project/c.impl_path]:
 text=path.read_text();text=text.replace(' -> int',' -> '+payload).replace('(int amount,'+payload+' data)','(int amount,'+payload+' data,'+mood+' choice,'+rules+' services)');path.write_text(text)
(f.project/'MainBody.celem').write_text((f.project/'MainBody.celem').read_text().replace(' -> int;',' -> '+payload+';').replace('(int,'+payload+')','(int,'+payload+','+mood+','+rules+')'))
(f.project/c.body_path).write_bytes(('var data=calls.Connected.Invoke(30,new '+payload+' {Value=new '+c.b.leaf+' {Count=30}},default,null!);int result=checked((int)data.Value.Count);Console.WriteLine(result);return result; // 보존하는 원래 호출자\r\n').encode())
graph=copy.deepcopy(c.graph);graph['contractHash']=c.b.fingerprint(old)
writer=graph['nodes'][1];writer['signature']['args'][0]['type']=payload;writer['arguments']['value']={'node':'private'if private else'transform','output':'return'}
if private:
 code=graph['nodes'][0];child=dict(schema=1,profile='sync-acyclic-methods-v1',entry='transform',nodes=[code],edges=[{'from':'transform','port':'next','to':'exit:return'}],exits={'return':{'node':'transform','output':'return'}},locals=[dict(id='kept',name='원래 지역값',type='long',initial={'constant':9223372036854775806})]);parent=dict(id='private',kind='graph',control='next',intent='직접 소유 내부 문맥',signature=copy.deepcopy(code['signature']),arguments={'data':{'input':'data'}},graph=child,x=128,y=104);graph['nodes'][0]=parent;graph['entry']='private';graph['edges'][0]['from']='private'
if private:
 path=f.project/'FreeInfo.celem';path.write_text(path.read_text().replace('contain function '+c.fn+';','').replace('provide '+c.fn+' with '+c.fn+'Body;',''))
(f.project/c.graph_path).write_text(json.dumps(graph,ensure_ascii=False));defs=f.metadata('blueprintDescribeOwned',project=str(f.manifest),id=c.fn+'Body',text=(f.project/c.impl_path).read_text(),bodyTarget='common',graph=graph,definitionsOnly=True);assert defs['state']=='node-definitions',defs
record=copy.deepcopy(c.record);record['definitionHash']=next(n['definitionHash']for n in defs['nestedNodes'if private else'nodes']if n['id']==('private/'if private else'')+'transform');raw=(json.dumps(record,ensure_ascii=False,indent=2)+'\r\n').encode();(f.project/code_path).write_bytes(raw)
original={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts};x.original=original
body='var result=received;result.Value.Count=checked(result.Value.Count+input1.Value.Count);return Increment(result); // 명시 본문 · 😀\r\n'

def verify(checkpoint,intent=None):
 rows={row['id']:row for row in json.loads(checkpoint.read_text())['changes']};actual=json.loads(rows[graph_id]['draft']);target=actual['nodes'][0]['graph']if private else actual;node=target['nodes'][0];expected=copy.deepcopy(graph);selected=expected['nodes'][0]['graph']if private else expected
 selected['nodes'][0]['signature']['args']=[dict(name='received',type=payload),dict(name='input1',type=payload)];selected['nodes'][0]['arguments']={'received':{'input':'data'},'input1':{'input':'data'}}
 if intent is not None:selected['nodes'][0]['intent']=intent
 assert actual==expected,(actual,expected)
 changed=json.loads(rows[code_id]['draft']);assert changed['helpers']==record['helpers'] and changed['source'].replace('\r\n','\n').strip()==body.replace('\r\n','\n').strip();assert set(row['id']for row in rows.values()if row['kind']in['blueprint','blueprint-node'])=={graph_id,code_id}
 group=rows[graph_id].get('atomicEditGroup',[graph_id,code_id]);assert set(group)==({graph_id,code_id}if private else{c.owner,c.fn,c.fn+'Body',graph_id,code_id});return group
def unchanged(except_names=()):
 assert all((f.project/p).read_bytes()==raw for p,raw in original.items()if p not in except_names);assert all(p.read_bytes()==raw for p,raw in x.external_original.items())
execute=c.execute
