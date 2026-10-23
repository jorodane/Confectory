"""Pure wide same-owner candidate with real schema/reference validation; no source writes/accounts/run."""
import copy,json,pathlib,subprocess,sys,tempfile,os
repo=pathlib.Path(sys.argv[1]).resolve();dotnet=os.environ.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet');root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-wide-metadata-'));n='Owned.Wide::';owner=n+'Slime'
items={
 'Main':('function','function '+n+'Main () -> int {}'),
 'Details':('schema','schema '+n+'Details {field Power single general long;field Label single general string;}'),
 'Vitals':('schema','schema '+n+'Vitals {field HP single general long;field Combat single compound '+n+'Details;field Counts multiple general long;field Target single reference '+n+'Details;field Targets multiple reference '+n+'Details;}'),
 'Unit':('object','object '+n+'Unit {use schema '+n+'Vitals;data HP=100;data Combat={Power=1;Label="부모";};data Counts=[1,2];}'),
 'Target':('object','object '+n+'Target {use schema '+n+'Details;data Power=2;data Label="참조";}'),
 'Wrong':('object','object '+n+'Wrong {}'),
 'Monster':('object','object '+n+'Monster extends '+n+'Unit {}'),
 'Alternate':('object','object '+n+'Alternate extends '+n+'Monster {data HP=200;}'),
 'Slime':('object','object '+owner+' extends '+n+'Monster {data HP=101;data Target='+n+'Target;data Targets=['+n+'Target];}'),
 'Extra':('module','module '+n+'Extra {}')}
manifest='project Owned.Wide version "1" {standalone true;entry '+n+'Main;'+''.join('element '+name+' '+kind+' "'+name+'.celem";' for name,(kind,text) in items.items())+'}'
project=root/'project.cproj';project.write_text(manifest)
for name,(kind,text) in items.items():(root/(name+'.celem')).write_text(text)
drafts=[{'id':n+name,'text':text} for name,(kind,text) in items.items() if name!='Slime'];original={p:p.read_bytes() for p in root.iterdir()}
def call(changes,ok=True):
 data={'operation':'mixedOwnerCopyEdits','project':str(project),'manifest':manifest,'id':owner,'text':items['Slime'][1],'drafts':drafts,'changes':changes};p=subprocess.run([dotnet,str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(data),text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert v['ok']==ok,v;assert all(p.read_bytes()==v for p,v in original.items());return v['result'] if ok else v
shape=lambda kind,cardinality,type:dict(kind=kind,cardinality=cardinality,type=type)
changes=[{'type':'description','text':'모두 함께 한글'}, {'type':'data','path':['Combat'],'contract':shape('compound','single',n+'Details'),'valueJson':'{"Power":9223372036854775805,"Label":"원문 한글"}'}, {'type':'data','path':['Counts'],'contract':shape('general','multiple','long'),'valueJson':'[9223372036854775806,3,2]'}, {'type':'data','path':['Target'],'contract':shape('reference','single',n+'Details'),'valueJson':json.dumps({'$ref':n+'Target'})}, {'type':'data','path':['Targets'],'contract':shape('reference','multiple',n+'Details'),'valueJson':json.dumps([{'$ref':n+'Target'}])}, {'type':'unset','path':['HP'],'contract':shape('general','single','long')}, {'type':'parent','value':n+'Alternate'}, {'type':'modules','ids':[n+'Extra']}, {'type':'definition','name':'Bonus','nativeType':'long','valueJson':'9007199254740993'}, {'type':'definition','name':'Note','nativeType':'string','valueJson':'"새 속성 한글"'}]
result=call(changes);assert '9223372036854775805' in result['text'] and '[9223372036854775806, 3, 2]' in result['text'] and 'data HP' not in result['text'];assert 'extends '+n+'Alternate' in result['text'];assert len(result['additions'])==1 and result['additions'][0]['id'].startswith(owner+'_Properties_');assert 'field Bonus single general long;' in result['additions'][0]['text'];assert result==call(copy.deepcopy(changes));print('PASS one deterministic pure candidate preserves exact long/array order/Korean/ref and combines parent/modules/local reset/new schema without source writes')
for boundary in ['duplicate','overlap','type','reference','foreign-parent','cycle','new-name','new-type','unknown','raw-owner','referenced-owner','unset-missing']:
 bad=copy.deepcopy(changes)
 if boundary=='duplicate':bad.append(bad[0])
 elif boundary=='overlap':bad.append({'type':'data','path':['Combat','Power'],'contract':shape('general','single','long'),'valueJson':'5'})
 elif boundary=='type':bad[1]['contract']['type']=n+'OtherSchema'
 elif boundary=='reference':bad[3]['valueJson']=json.dumps({'$ref':n+'Wrong'})
 elif boundary=='foreign-parent':bad[6]['value']='Lib::Parent'
 elif boundary=='cycle':bad[6]['value']=owner
 elif boundary=='new-name':bad[8]['name']='HP'
 elif boundary=='new-type':bad[8]['nativeType']='decimal'
 elif boundary=='unknown':bad.append({'type':'schema','text':'schema other'})
 elif boundary=='raw-owner':bad[0]['ownerText']='object other {}'
 elif boundary=='referenced-owner':bad[3]['path'].append('Power');bad[3]['contract']=shape('general','single','long');bad[3]['valueJson']='1'
 else:bad[5]['path']=['Combat'];bad[5]['contract']=shape('compound','single',n+'Details')
 call(bad,False)
print('PASS twelve duplicate/overlap/schema/ref/parent/identity/new-definition/foreign-owner boundaries reject the whole candidate without source mutation')
print(json.dumps({'pureMetadata':True,'actualEngine':False,'renderer':False,'nativeWindows':False,'accountOrInference':False,'evidence':str(root)}))
