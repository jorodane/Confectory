"""Original single private/native body plans validate; grouped candidate is missing."""
import copy,json,subprocess
import v666_private_selected_import_fixture as x
f=x.f
def prepare(r,ok=True):
 p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationDefinitions',**r)),env=f.env,text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,v;return v
try:
 r=x.request();(f.case/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
 for row in r['changes']:one=copy.deepcopy(r);one['changes']=[row];prepare(one)
 x.unchanged();x.execute(40,'original-whole-native');f.checked('original private/helper and native single plans independently validate and original program executes40')
 if x.mode=='reproduce':
  reply=prepare(r,False);(f.case/'group-rejection.json').write_text(json.dumps(reply,ensure_ascii=False,indent=2));x.unchanged();f.checked('published group alone rejects the two valid exact-contract explicit body plans, preserving every original')
 else:
  for fault in ['stale-body','stale-graph','different-native','different-public','extra-scope','invalid-last-body','changed-frame','changed-helpers-boundary','unknown-helper']:
   bad=copy.deepcopy(r);first=bad['changes'][0];plan=next(iter(first['mapping']['bodies'].values()))
   if fault=='stale-body':plan['hash']='0'*64
   elif fault=='stale-graph':plan['whole']['hash']='0'*64
   elif fault=='different-native':plan['signature']['args'][0]['name']='implicitNewName'
   elif fault=='different-public':first['signature']['args'][0]['name']='implicitNewName'
   elif fault=='extra-scope':first['mapping']['unknownSourcePlan']={}
   elif fault=='changed-frame':plan['beforeSignature']=copy.deepcopy(x.native)
   elif fault=='changed-helpers-boundary':plan['helpers']='} class Escape { static void X(){'
   elif fault=='unknown-helper':plan['helpers']='static long Wrong(long value){return value;}'
   elif fault=='invalid-last-body':next(iter(bad['changes'][1]['mapping']['bodies'].values()))['text']='return MissingWholeValue;'
   prepare(bad,False);x.unchanged()
  f.checked('stale source/flow, implicit public/native changes, unknown plan and invalid last CSharp reject atomically')
  for fault in ['selected-contract','selected-body-context','root-alias','root-contract','root-no-call','root-call-contract','root-storage']:
   bad=copy.deepcopy(r);a,b=bad['changes'];header=bad['units'][x.whole_implementation];flow=bad['units'][x.whole_graph]
   if fault=='selected-contract':b['signature']['return']='double'
   elif fault=='selected-body-context':next(iter(b['mapping']['bodies'].values()))['whole']={}
   elif fault=='root-alias':header['draft']=header['draft'].replace(x.root_alias,'OtherAlias')
   elif fault=='root-contract':header['draft']=header['draft'].replace('(long,long) -> long','(long,long) -> double')
   else:
    graph=json.loads(flow['draft']);node=next(n for n in graph['nodes']if n['id']==x.root_call)
    if fault=='root-no-call':graph['nodes'].remove(node);graph['edges']=[e for e in graph['edges']if e['from']!=x.root_call];next(e for e in graph['edges']if e['from']=='inner')['to']='exit:return';graph['exits']={'return':{'node':'inner'}}
    elif fault=='root-call-contract':node['signature']['return']='double'
    elif fault=='root-storage':node['forwardCallerStorage']=True
    flow['draft']=json.dumps(graph,ensure_ascii=False,indent=2)+'\r\n'
   prepare(bad,False);x.unchanged();f.checked(fault+' rejects missing or changed selected call contracts without inferring import/graph edits')
  result=prepare(r)['result'];(f.case/'candidate.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));rows=result['updates']+result['linkedUpdates'];x.verify_rows({v['id']:dict(draft=v['text'])for v in rows});reverse=copy.deepcopy(r);reverse['changes'].reverse();other=prepare(reverse)['result'];assert{v['id']:v['text']for v in rows}=={v['id']:v['text']for v in other['updates']+other['linkedUpdates']};x.unchanged();f.checked('one order-independent private/native candidate preserves original hashes, graph/native/public contracts, original CSharp and shared callers')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
