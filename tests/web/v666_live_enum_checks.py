"""Mapped enum fields over the existing caller-owned property editor and receipts."""
import copy,hashlib,json
import v666_async_property_checks as lifecycle

def configure(c):
 c['_interrupt_timeout_seconds']=120;c['_interrupt_observations']=[]
 c['async_mode']=c['sys'].argv[3]if len(c['sys'].argv)>3 else'normal';assert c['async_mode']in['normal','storage','conflict','loss','late'];n=c['n'];native='Confectory.Information.E'+hashlib.sha256(json.dumps(n[:-2]).encode()).hexdigest()[:24]+'.E'+hashlib.sha256(json.dumps(n+'Mood').encode()).hexdigest()[:24];c['_enum_type']=native
 members=[dict(id='ten',name='처음'),dict(id='twenty',name='중간'),dict(id='thirty',name='다음')];numbers=dict(ten=10,twenty=20,thirty=30)
 c['items']['Mood']=('enum','enum '+n+'Mood {value editorEnumProfile="nominal-members-native-v2";value editorEnumValues='+json.dumps(json.dumps(members,ensure_ascii=False))+';value editorEnumNumbers='+json.dumps(json.dumps(numbers))+';}')
 for name in ['Calc','CalcBody']:
  kind,text=c['items'][name];c['items'][name]=(kind,text.replace('long replacement',native+' replacement'))
 kind,text=c['items']['MainBody'];c['items']['MainBody']=(kind,text.replace('Calc (object,long)','Calc (object,'+native+')'))
 c['items']['Vitals']=('schema','schema '+n+'Vitals {field health single enum '+n+'Mood;}')
 prepared=c['metadata']('blueprintPrepareFeature',id=n+'Calc',text=c['items']['Calc'][1].replace('provide '+n+'Calc with '+n+'CalcBody;',''),implementation=n+'CalcBody',graphPath='Calc.graph.json',nodePath='combine.node.json');c['g']['contractHash']=prepared['graph']['contractHash']
 c['g']['nodes'][0]['signature']['return']=native
 next(node for node in c['g']['nodes']if node['id']=='first')['arguments']['value']={'node':'beforeNumber','output':'return'}
 next(node for node in c['g']['nodes']if node['id']=='write')['signature']['args'][1]['type']=native
 next(node for node in c['g']['nodes']if node['id']=='second')['arguments']['value']={'node':'afterNumber','output':'return'}
 def convert(id,value):return dict(id=id,kind='code',control='next',intent='명시 C# enum 숫자 읽기',signature=dict(args=[dict(name='value',type=native)],**{'return':'long'}),arguments=dict(value=value),implementation=id+'.node.json')
 c['g']['nodes']+=[convert('beforeNumber',{'node':'before','output':'return'}),convert('afterNumber',{'input':'replacement'})]
 c['g']['edges']=[dict(**{'from':a},port='next',to=b)for a,b in [('before','beforeNumber'),('beforeNumber','first'),('first','write'),('write','afterNumber'),('afterNumber','second'),('second','combine'),('combine','finish')]]

def complete_sources(c):
 for id in ['beforeNumber','afterNumber']:
  definition=next(row for row in c['defs']['nodes']if row['id']==id);c['sources'][id+'.node.json']=json.dumps(dict(schema=1,node=id,definitionHash=definition['definitionHash'],source='return (long)value; // explicit authored enum conversion'),ensure_ascii=False)
 c['sources']['Main.csbody']=c['sources']['Main.csbody'].replace('new object[]{10L}','new object[]{'+c['_enum_type']+'Ids.FromId("ten")}').replace('calls.Calc.Invoke(target,20)','calls.Calc.Invoke(target,'+c['_enum_type']+'Ids.FromId("twenty"))').replace('calls.Calc.Invoke(target,30)','calls.Calc.Invoke(target,'+c['_enum_type']+'Ids.FromId("thirty"))')

def begin(c):
 c['call']('select',{'id':c['n']+'Calc'});c['call']('saveDraft',{});data=c['current']();assert data['profile']=='sync-acyclic-property-set-v1';assert any(row['id']==c['n']+'Mood'for row in data['sources']),data['sources'];c['_checkpoint']=next(c['project'].glob('.confectory/edit-workspaces/*/draft.json'));c['checked']('mapped enum property sources bind the current enum declaration without reading a live object or changing source ownership')

def save(c,held):
 if c['async_mode']!='conflict':
  try:return lifecycle.save(c,held)
  except Exception:
   evidence=dict(traffic=c['traffic'],results=c['results'])
   try:evidence['state']=c['state']();evidence['pending']=c['pending']()
   except Exception as error:evidence['captureError']=str(error)
   (c['case']/'enum-save-failure.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2));raise
 path=c['project']/'Mood.celem';before=path.read_bytes();checkpoint=c['_checkpoint'];saved=checkpoint.read_bytes();peer=before+b'\n// enum peer before Save\n';path.write_bytes(peer);mark=len(c['traffic'])
 try:
  c['author']().locator('[data-bp-save]').click();failure=lifecycle.refused(c,mark);c['idle']();assert all(dict(c['pending']()).get(k)==v for k,v in held);assert checkpoint.read_bytes()==saved and path.read_bytes()==peer
 finally:path.write_bytes(before)
 c['unchanged']();c['checked']('a changed enum source rejects the complete property plan before Save without losing typed inputs or rewriting peer data');c['async_mode']='normal'
 try:return lifecycle.save(c,held)
 finally:c['async_mode']='conflict'

def review(c,first):
 try:return review_impl(c,first)
 except Exception:
  evidence=dict(traffic=c['traffic'],results=c['results'])
  try:evidence['state']=c['state']();evidence['pending']=c['pending']()
  except Exception as error:evidence['captureError']=str(error)
  (c['case']/'enum-review-failure.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2));raise

def review_impl(c,first):
 first.locator('[data-reject]').click();c['expect'](first).not_to_be_visible();c['unchanged']();current=lifecycle.review_ready(c)
 if c['async_mode']=='conflict':
  path=c['project']/'Mood.celem';before=path.read_bytes();checkpoint=c['_checkpoint'];saved=checkpoint.read_bytes();peer=before+b'\n// enum peer after Review\n';path.write_bytes(peer);mark=len(c['traffic'])
  try:
   current.locator('#confirm').click();failure=lifecycle.refused(c,mark);assert any(row.get('result',{}).get('sourceConfirmed')is False for row in failure),failure;c['idle']();assert path.read_bytes()==peer and checkpoint.read_bytes()==saved;assert all((c['project']/name).read_bytes()==raw for name,raw in c['original'].items()if name!='Mood.celem')
  finally:path.write_bytes(before)
  if current.is_visible():current.locator('[data-reject]').click()
  c['checked']('post-Review enum source drift rejects final CAS; exact restoration and a new explicit Review retain the same caller contract');current=lifecycle.review_ready(c)
 return current

def after_saved(c):lifecycle.after_saved(c)
def after_confirm(c):lifecycle.after_confirm(c)
