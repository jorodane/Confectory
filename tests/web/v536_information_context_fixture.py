"""Owned whole-body caller, unchanged own ABI, explicitly edited import call text."""
import copy,json,re
import v536_information_whole_contract_fixture as b
f,d,n,owner,fn,caller,mode=b.f,b.d,b.n,b.owner,b.fn,b.caller,b.mode
scenario,chain=b.scenario,b.chain
old,new,selected,remap,edited=b.old,b.new,b.selected,b.remap,b.edited
body_id,body_path=b.body_id,b.body_path
path=f.project/'CallerBody.celem';original_impl=path.read_text();alias=re.search(r'\bas (\w+)\s*\(',original_impl)[1]
cpp=original_impl.replace('blueprint common "caller.graph.json";','body common "whole-caller.csbody";')
path.write_text(cpp);original_caller='return calls.'+alias+'.Invoke(first,out long total); // 원래 caller ABI·본문 보존\r\n';(f.project/'whole-caller.csbody').write_bytes(original_caller.encode())
converted=f.metadata('blueprintConversion',project=str(f.manifest),id=caller+'Body',text=cpp,target='common',graphPath='caller.graph.json',nodePath='caller-context.node.json')
path.write_text(converted['implementation']);(f.project/'caller.graph.json').write_text(json.dumps(converted['graph']));(f.project/'caller-context.node.json').write_text(json.dumps(converted['node']))
caller_id=caller+'Body/body:common/node:body';caller_signature=n.canonical(f.metadata('inspect',text=path.read_text())['signature'])
caller_text='bool active=calls.'+alias+'.Invoke("명시한 문자열",out long total,first);return total; // 직접 고친 호출자 😀\r\n'
snapshot={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}

def selections(preview):
    plan=b.selections(preview);row=preview['functionBodies'][caller_id];assert row['sourceKind']=='whole-caller-csharp' and row['signature']==caller_signature
    plan['bodies'][caller_id]={k:row[k] for k in ['hash','path','whole']}|{'beforeSignature':caller_signature,'signature':caller_signature,'contract':new,'text':caller_text}
    return plan

def request():
    r=n.request(new,remap);p={key:f.metadata(op,id=owner,function=fn,includeBlueprintTargets=True,units=r['units']) for key,op in [('functionInputs','informationFunctionInputs'),('functionBodies','informationFunctionBodies')]};r['changes'][0]['mapping']=selections(p);return r

def verify(checkpoint):
    rows={r['id']:r for r in json.loads(checkpoint.read_text())['changes']}
    assert json.loads(rows[body_id]['draft'])['source']==edited
    assert json.loads(rows[caller_id]['draft'])['source']==caller_text
    assert n.canonical(f.metadata('inspect',text=rows[caller+'Body']['draft'])['signature'])==caller_signature
    g=json.loads(rows[caller+'Body/body:common']['draft']);node=g['nodes'][0];assert node['signature']==caller_signature and node['implementationContext']['signature']==caller_signature
    current=f.metadata('inspect',text=rows[caller+'Body']['draft']);assert g['edges']==converted['graph']['edges'] and node['arguments']==converted['graph']['nodes'][0]['arguments']
    assert all((f.project/p).read_bytes()==v for p,v in snapshot.items())
    ids=rows[owner]['atomicEditGroup'];assert {owner,fn,fn+'Body',body_id,caller+'Body',caller_id,caller+'Body/body:common'}<=set(ids)
    return ids
