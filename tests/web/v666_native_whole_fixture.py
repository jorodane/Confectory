"""Explicit whole-body nominal ABI; original source file is never rewritten."""
import copy,json
import v666_blueprint_entry_fixture as b
x,f,e,owner,fn=b.x,b.f,b.e,b.owner,b.fn
payload=b.payload;old=b.old;new=b.new;graph_id,graph_path,impl_path=b.graph_id,b.graph_path,b.impl_path
body_id,body_path=b.body_id,b.body_path;original=b.original
selected='var value=calls.Connected.Invoke(new '+payload+' {Value=new '+b.leaf+' {Count=30}});int result=checked((int)value.Value.Count);Console.WriteLine(result);return result; // 명시 호출자 대응 · 😀\r\n'
# Restore exactly the original direct C# caller before the explicit plan.
(f.project/body_path).write_bytes(original.encode())
native=dict(args=[dict(name='nativeAmount',type='int')],**{'return':'int'});chosen=dict(args=[dict(name='nativeAmount',type=payload)],**{'return':payload});code_original='return nativeAmount; // 원래 전체 본문 · 😀\r\n';code_selected='nativeAmount.Value.Count=checked(nativeAmount.Value.Count+1);return nativeAmount; // 명시 구조체 전체 본문 · 😀\r\n';native_path='whole-original.csbody';code_path='whole.node.json';(f.project/native_path).write_bytes(code_original.encode())
cpp='implementation '+fn+'Body for '+fn+' (int nativeAmount) -> int {body common "'+native_path+'";}'
(f.project/impl_path).write_text(cpp);converted=f.metadata('blueprintConversion',project=str(f.manifest),id=fn+'Body',text=cpp,target='common',graphPath=graph_path,nodePath=code_path);assert 'graph'in converted and'node'in converted,converted
(f.project/impl_path).write_text(converted['implementation']);graph=converted['graph'];(f.project/graph_path).write_text(json.dumps(graph,ensure_ascii=False));record=converted['node'];(f.project/code_path).write_text(json.dumps(record,ensure_ascii=False));node=next(v for v in graph['nodes']if v['kind']=='code');code_id=graph_id+'/node:'+node['id'];code_bytes=(f.project/code_path).read_bytes();writer=next(v for v in graph['nodes']if v['kind']=='export')
x.original={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.parts};changes_allowed=b.changes_allowed|{code_path};catalog=b.catalog;execute=b.execute

def request(c=None):
 c=c or catalog();r=b.request(c);edit=r['declaration']['changes'][0];m=edit['mapping'];m['outputs']={};row=c['functionBodies'][code_id];assert row['sourceKind']=='whole-csharp';m['bodies'][body_id]['text']=selected;m['bodies'][code_id]={k:row[k]for k in ['hash','path','whole']}|dict(beforeSignature=native,signature=chosen,contract=new,text=code_selected);return r

def verify(checkpoint,signature=None):
 d=json.loads(checkpoint.read_text());rows={v['id']:v for v in d['changes']};assert d['version']==2;assert rows[body_id]['draft'].replace('\r\n','\n').strip()==selected.replace('\r\n','\n').strip();new_record=json.loads(rows[code_id]['draft']);assert new_record['source'].replace('\r\n','\n').strip()==code_selected.replace('\r\n','\n').strip();g=json.loads(rows[graph_id]['draft']);code=next(v for v in g['nodes']if v['id']==node['id']);assert code['signature']==chosen and code['implementationContext']['signature']==chosen and code['arguments']=={'nativeAmount':{'input':'amount'}};assert g['entry']==graph['entry']and g['edges']==graph['edges'];ret=next(v for v in g['nodes']if v['id']==writer['id']);assert ret['signature']['args'][0]['type']==payload and ret['arguments']==writer['arguments'];assert all(code.get(k)==node.get(k)for k in ['id','x','y','intent','implementation']);assert(f.project/native_path).read_bytes()==code_original.encode();receipt=rows[owner]['slotSaveReceipt'];assert '$function:'+fn in receipt['nativeTypeProofs'];assert code_path in receipt['readGuards']or any(v['path']==str(f.project/code_path)for v in receipt['nativeTypeReads']);return rows[owner]['atomicEditGroup']
