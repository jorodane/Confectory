"""Saved property observation identity, partial Review and restore boundaries."""
import copy,hashlib,json,os,pathlib,runpy,subprocess,sys
repo=pathlib.Path(sys.argv[1]);fixture=runpy.run_path(str(repo/'tests/web/v536_property_plan.py'),run_name='property_guard_fixture');ns=fixture['n'].removesuffix('::');gid=fixture['n']+'CalcBody/body:common';units={}
def add(id,kind,path):
    text=(fixture['project']/path).read_text();units[id]=dict(kind=kind,path=path,original=text,draft=text,baseline=hashlib.sha256(text.encode()).hexdigest())
for name in ['Calc','CalcBody','Monster','Vitals']:add(fixture['n']+name,fixture['items'][name][0],name+'.celem')
add(gid,'blueprint','Calc.graph.json');add(gid+'/node:combine','blueprint-node','combine.node.json');add(fixture['n']+'ProjectManifest','project','project.cproj')
proof={id:{k:u[k]for k in ['path','kind']}|dict(hash=hashlib.sha256(u['draft'].encode()).hexdigest())for id,u in units.items()};units[gid]['propertyObservations']=dict(version=1,graph=gid,sources=proof)
def query(value,ok=True,**extra):
    run=subprocess.run([os.environ['CONFECTORY_DOTNET'],str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='blueprintPropertyObservations',namespace=ns,units=value,**extra)),capture_output=True,text=True,check=True);reply=json.loads(run.stdout);assert reply['ok']==ok,reply;return reply.get('result')
checks=query(units)['checks'];assert len(checks)==len(units)and all('text'not in r for r in checks);assert query(units,selected=list(units))['checks']==checks;print('PASS exact owned property/manifest/code observations produce readonly CAS checks',flush=True)
for name,mutate in [
    ('missing project',lambda u:u[gid]['propertyObservations']['sources'].pop(fixture['n']+'ProjectManifest')),
    ('missing source',lambda u:u.pop(fixture['n']+'Vitals')),
    ('omitted schema receipt',lambda u:u[gid]['propertyObservations']['sources'].pop(fixture['n']+'Vitals')),
    ('omitted owner receipt',lambda u:u[gid]['propertyObservations']['sources'].pop(fixture['n']+'Monster')),
    ('omitted code receipt',lambda u:u[gid]['propertyObservations']['sources'].pop(gid+'/node:combine')),
    ('changed receipt path',lambda u:u[gid]['propertyObservations']['sources'][fixture['n']+'Vitals'].update(path='other.celem')),
    ('changed receipt hash',lambda u:u[gid]['propertyObservations']['sources'][fixture['n']+'Vitals'].update(hash='0'*64)),
    ('changed original',lambda u:u[fixture['n']+'Vitals'].update(original='changed')),
    ('foreign source',lambda u:u[gid]['propertyObservations']['sources'].update({'External.Hidden::Secret':dict(path='secret',kind='schema',hash='0'*64)})),
]:
    bad=copy.deepcopy(units);mutate(bad);query(bad,False);print('PASS reject '+name+' without granting another source',flush=True)
query(units,False,selected=[gid]);print('PASS partial property Review is rejected',flush=True)
bad=copy.deepcopy(units);id=fixture['n']+'Vitals';donor=bad[fixture['n']+'Monster']
for key in ['path','original','draft','baseline']:bad[id][key]=donor[key]
bad[gid]['propertyObservations']['sources'][id].update(path=donor['path'],hash=donor['baseline']);query(bad,False);print('PASS distinct observation identities cannot alias another source path',flush=True)
bad=copy.deepcopy(units);id=fixture['n']+'Vitals';bad[id]['path']='../outside';bad[gid]['propertyObservations']['sources'][id]['path']='../outside';query(bad,False);print('PASS source path traversal is rejected',flush=True)
lazy=copy.deepcopy(units);lazy[id]['draft']=None;query(lazy,False);members=query(lazy,action='members')['ids'];assert set(members)==set(units);lazy[id]=copy.deepcopy(units[id]);lazy[ns+'::Dormant/body:common']=dict(kind='blueprint',path='unused.json',draft=None);assert query(lazy)['checks']==checks;print('PASS cold restore loads known receipt IDs and leaves unrelated locators lazy',flush=True)
print('PROPERTY_GUARD_FIXTURE '+str(fixture['case']),flush=True)

# Editing candidate bytes does not rebase the physical read guard. The Save ACK
# may be stale after a later edit; it is not the source-observation authority.
edited=copy.deepcopy(units);cid=gid+'/node:combine';body=json.loads(edited[cid]['draft']);body['source']+='\n// explicit subsequent edit';edited[cid]['draft']=json.dumps(body);edited[gid]['authorSaveReceipt']=dict(version=1,sources={});assert query(edited)['checks']==checks;query(edited,False,selected=[cid]);print('PASS later C# candidate edits retain immutable physical read guards',flush=True)
created=copy.deepcopy(edited);created[cid].update(original='',baseline='missing');created[gid]['propertyObservations']['sources'][cid]['hash']='missing';assert any(r['path']=='combine.node.json'and r['hash']=='missing'for r in query(created)['checks']);print('PASS server-known new source keeps expected-missing CAS without granting a path',flush=True)
created[cid]['original']='not empty';query(created,False);print('PASS missing source cannot disguise an existing physical baseline',flush=True)
legacy=copy.deepcopy(units);legacy[gid].pop('propertyObservations');assert query(legacy)['checks']==[];print('PASS legacy acknowledgements are not silently reinterpreted as physical read baselines',flush=True)
