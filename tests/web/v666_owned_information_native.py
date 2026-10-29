"""Pure candidates for directly owned nested definitions; original files stay byte-exact."""
import pathlib,sys,os,tempfile,json,hashlib,subprocess,copy
repo=pathlib.Path(sys.argv[1]).resolve();sdk=os.environ.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet');root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-owned-information-'));ns='Owned.Nested::';owner=ns+'Info'
items={'Main':('function','function '+ns+'Main () -> int {}'),'Info':('schema','// 원문 보존\nschema '+owner+' {field Keep single general long;value editorInformationDefaults="typed-json-v1";value editorFieldDefault_Keep="9223372036854775805";}'),'Shared':('schema','schema '+ns+'Shared {field Existing single general string;}'),'Local':('schema','schema '+ns+'Local {field Keep single general long;}'),'Item':('object','object '+ns+'Item {use schema '+ns+'Local;data Keep=9223372036854775804;}')}
manifest='// 등록 원문\nproject Owned.Nested version "1" {standalone true;entry '+ns+'Main;'+''.join('element '+k+' '+kind+' "'+k+'.celem";' for k,(kind,_) in items.items())+'}'
project=root/'project.cproj';project.write_text(manifest)
for k,(_,text) in items.items():(root/(k+'.celem')).write_text(text)
original={p:p.read_bytes() for p in root.iterdir()};checks=[]
def check(t):checks.append(t);print('PASS '+t,flush=True)
def rpc(operation,request,ok=True):
 r=subprocess.run([sdk,str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':operation,**request}),text=True,capture_output=True,check=True);v=json.loads(r.stdout);assert v['ok']==ok,v;assert all(p.read_bytes()==b for p,b in original.items());return v.get('result')
def base(id=owner,text=None,m=manifest,drafts=None):return {'project':str(project),'manifest':m,'id':id,'text':text or items[id.split('::')[1]][1],'drafts':drafts if drafts is not None else [{'id':ns+k,'text':t} for k,(_,t) in items.items() if ns+k!=id]}
def leaf(key,type='string',name=None):return dict(key=key,name=name or key,icon='',definition=dict(kind='general',cardinality='single',type=type),sources=None)
change=dict(type='owned-definition',name='Stats',displayName='자체 복합',icon='☆',cardinality='single',contract=None,schema=None,schemaHash=None,tree={'fields':[leaf('Power','long','힘'),dict(key='Inner',name='내부',icon='♣',definition=dict(kind='owned',cardinality='single'),sources=None,children={'fields':[leaf('Title',name='제목')]})]},sources={},valueJson='{"Power":9223372036854775806,"Inner":{"Title":"한글"}}')
def prepare(c,request=None,ok=True):
 request=request or base();return rpc('informationDefinitions' if request['id']==owner else 'mixedOwnerCopyEdits',{**request,'changes':c},ok)
def overlay(v,request=None):
 request=copy.deepcopy(request or base());request['text']=v['text'];request['manifest']=v['manifest'];rows={r['id']:r for r in request['drafts']}
 for row in v['additions']+v['updates']:rows[row['id']]={'id':row['id'],'text':row['text']}
 request['drafts']=list(rows.values());return request
v=prepare([change,{'type':'description','text':'한 후보'}]);assert len(v['additions'])==2 and '9223372036854775805' in v['text'] and v['text'].startswith('// 원문 보존');assert v['manifest'].startswith('// 등록 원문');q=overlay(v);view=rpc('effective',{**q,'schemaView':True});owned=view['schemaModel']['ownedDefinitions']['Stats'];assert owned['tree']==change['tree'];assert len(owned['sources'])==2;check('new own nested schemas use stable qualified IDs, exact values, original comments and one candidate')
row={**change,'contract':dict(kind='compound',cardinality='single',type=view['schemaModel']['fields']['Stats']['type']),'schema':owner,'schemaHash':view['schemaModel']['fields']['Stats']['schemaHash'],'sources':owned['sources'],'tree':owned['tree']}
edit=copy.deepcopy(row);edit['tree']['fields'][0]['name']='힘 한글';edit['tree']['fields'][0]['icon']='★';edit['tree']['fields'][1]['children']['fields'].append(leaf('Flag','bool','상태'));edit['valueJson']='{"Power":9223372036854775806,"Inner":{"Title":"한글","Flag":true}}';v2=prepare([edit],q);assert len(v2['updates'])==2 and not v2['additions'];q2=overlay(v2,q);after=rpc('effective',{**q2,'schemaView':True});assert after['schemaModel']['ownedDefinitions']['Stats']['tree']==edit['tree'];check('saved nested add/name/icon edits preserve native keys and original data through metadata reconstruction')
for addition in v['additions']:
 proof=dict(owner=owner,ownerText=q['text'],id=addition['id'],text=addition['text'],path=addition['path'])
 assert rpc('ownedDefinitionOwnership',proof)['owned'] is True
 for key,value in [('owner','Foreign::Info'),('path','elements/elsewhere.celem'),('id',ns+'Shared')]:rpc('ownedDefinitionOwnership',{**proof,key:value},False)
assert rpc('ownedDefinitionOwnership',dict(owner=owner,ownerText=q['text'],id=ns+'Shared',text=items['Shared'][1],path='Shared.celem'))['owned'] is False
check('cold creation proof requires exact marker, owner, qualified identity and locator; ordinary named information stays on its legacy rules')
many=copy.deepcopy(row);many['cardinality']='multiple';many['valueJson']='['+many['valueJson']+']';many_result=prepare([many],q);many_view=rpc('effective',{**overlay(many_result,q),'schemaView':True})['schemaModel'];assert many_view['fields']['Stats']['cardinality']=='multiple' and many_view['ownedDefinitions']['Stats']['tree']==row['tree'];check('explicit root cardinality preserves the complete exact aggregate and the same child identities')
hidden=copy.deepcopy(q);child_id=row['contract']['type'];child=next(d for d in hidden['drafts'] if d['id']==child_id);child['text']=child['text'].rstrip()[:-1]+'value editorInformationDefaults="typed-json-v1";value editorFieldDefault_Power="9223372036854775806";}'
hidden_view=rpc('effective',{**hidden,'schemaView':True})['schemaModel'];hidden_edit=copy.deepcopy(edit);hidden_edit['sources']=hidden_view['ownedDefinitions']['Stats']['sources'];hidden_result=prepare([hidden_edit],hidden);assert 'editorFieldDefault_Power' in next(u['text'] for u in hidden_result['updates'] if u['id']==child_id);check('existing child default metadata survives unrelated nested definition edits')
ordinary=copy.deepcopy(q);shared_source=next(d for d in ordinary['drafts'] if d['id']==ns+'Shared');shared_source['text']=shared_source['text'].rstrip()[:-1]+'value editorOwnedDefinition="ordinary-user-value";}'
choices=rpc('effective',{**ordinary,'schemaView':True,'definitionTypes':True})['definitionTypes'];assert any(c['id']==ns+'Shared' and c['available'] for c in choices);check('an unrelated same-named metadata value cannot hide an ordinary named information choice')
for mutate in ['child-hash','root-hash','foreign','named','duplicate','bad-value','partial']:
 bad=copy.deepcopy(edit);request=copy.deepcopy(q)
 if mutate=='child-hash':bad['sources'][next(iter(bad['sources']))]='0'*64
 elif mutate=='root-hash':bad['schemaHash']='0'*64
 elif mutate=='foreign':bad['schema']='External::Info'
 elif mutate=='named':bad['contract']['type']=ns+'Shared'
 elif mutate=='duplicate':bad['tree']['fields'].append(copy.deepcopy(bad['tree']['fields'][0]))
 elif mutate=='bad-value':bad['valueJson']='{"Power":true,"Inner":{"Title":"한글","Flag":true}}'
 else:bad['tree']['fields'][0]['definition']['type']='bool'
 prepare([bad,{'type':'description','text':'일부 적용 금지'}],request,False)
check('stale/root/foreign/reused claims, duplicate IDs and incompatible values reject the entire candidate')
shared=copy.deepcopy(q);shared['drafts'].append({'id':ns+'Consumer','text':'schema '+ns+'Consumer {field Alias single compound '+row['contract']['type']+';}' });shared['manifest']=shared['manifest'].replace('entry '+ns+'Main;','entry '+ns+'Main;element Consumer schema "Consumer.celem";');(root/'Consumer.celem').write_text(shared['drafts'][-1]['text']);original[root/'Consumer.celem']=(root/'Consumer.celem').read_bytes();prepare([edit],shared,False);check('a child reused by a second declaration cannot be mutated through an ownership marker')
obj=base(ns+'Item');ov=prepare([change],obj);oq=overlay(ov,obj);model=rpc('effective',{**oq,'schemaView':True})['schemaModel'];assert model['ownedDefinitions']['Stats']['tree']==change['tree'] and '9223372036854775804' in ov['text'];assert len(ov['additions'])==3;check('object-owned root schema plus nested children preserve original applied schema and exact object values')
print(json.dumps({'checks':checks,'evidence':str(root),'sourceWritten':False,'actualEngine':False,'actualWindows':False},ensure_ascii=False))
