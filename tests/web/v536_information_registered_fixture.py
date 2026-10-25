"""Read-only registered contracts in an owned information-function candidate."""
import copy
import json
import v536_information_context_fixture as b

f,d,n,owner,fn,caller,mode=b.f,b.d,b.n,b.owner,b.fn,b.caller,b.mode
old,new,remap=b.old,b.new,b.remap
selected,edited,body_id,body_path,caller_signature,scenario,chain=b.selected,b.edited,b.body_id,b.body_path,b.caller_signature,b.scenario,b.chain
registered=f.project/'registered'
foreign='External.Fields::Echo'
foreign_source='function '+foreign+' (long input) -> long {provide '+foreign+' with '+foreign+'Body;}'
pack=registered/'pack.cpack'
pack.write_text(pack.read_text().replace('}', 'element Echo function "Echo.celem";element EchoBody implementation "EchoBody.celem";}'))
(registered/'Echo.celem').write_text(foreign_source)
(registered/'EchoBody.celem').write_text('implementation '+foreign+'Body for '+foreign+' (long input) -> long {body common "Echo.csbody";}')
(registered/'Echo.csbody').write_text('return checked(input+1); // 외부 원문 · 9223372036854775806')
cpp=b.cpp.replace('{','{import '+foreign+' as Registered (long) -> long;',1)
original=b.original_caller.replace('return calls.', 'long held=calls.Registered.Invoke(second);return held+calls.',1)
caller_text=b.caller_text.replace('return total;', 'return checked(total+calls.Registered.Invoke(second));')
path=f.project/'CallerBody.celem';path.write_text(cpp)
(f.project/'whole-caller.csbody').write_bytes(original.encode())
converted=f.metadata('blueprintConversion',project=str(f.manifest),id=caller+'Body',text=cpp,target='common',graphPath='caller.graph.json',nodePath='caller-context.node.json')
path.write_text(converted['implementation'])
(f.project/'caller.graph.json').write_text(json.dumps(converted['graph']))
(f.project/'caller-context.node.json').write_text(json.dumps(converted['node']))
caller_id=b.caller_id
snapshot={str(p.relative_to(f.project)):p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}

def selections(preview):
    plan=b.selections(preview)
    plan['bodies'][caller_id]['text']=caller_text
    plan['dependencies']=copy.deepcopy(preview['functionDependencies'])
    assert list(plan['dependencies'])==[caller+'Body']
    return plan

def request():
    r=n.request(new,remap)
    preview={key:f.metadata(op,id=owner,function=fn,project=str(f.manifest),manifest=f.manifest.read_text(),includeBlueprintTargets=True,units=r['units']) for key,op in [('functionInputs','informationFunctionInputs'),('functionBodies','informationFunctionBodies'),('functionDependencies','informationFunctionDependencies')]}
    r['changes'][0]['mapping']=selections(preview)
    return r

def unchanged():
    assert all((f.project/p).read_bytes()==v for p,v in snapshot.items())

def verify(checkpoint):
    rows={row['id']:row for row in json.loads(checkpoint.read_text())['changes']}
    assert json.loads(rows[caller_id]['draft'])['source']==caller_text
    assert json.loads(rows[body_id]['draft'])['source']==edited
    assert n.canonical(f.metadata('inspect',text=rows[caller+'Body']['draft'])['signature'])==b.caller_signature
    assert foreign+' as Registered (long) -> long;' in rows[caller+'Body']['draft']
    unchanged()
    ids=rows[owner]['atomicEditGroup']
    assert caller_id in ids and not any(id.startswith('External.Fields::') for id in ids)
    return ids
