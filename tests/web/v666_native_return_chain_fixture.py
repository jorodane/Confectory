"""Two explicitly retyped returns compose an actual owned CSharp import call."""
import copy,json,re,hashlib
import v666_native_returns_fixture as _base
for _key in dir(_base):
 if not _key.startswith('_'):globals()[_key]=getattr(_base,_key)
first,second=functions;header=first.split('::')[1]+'Body.celem';p=f.project/header;p.write_text(p.read_text().replace('{','{import '+second+' as Second (long,double,out long) -> long;',1))
sources[first]='long observed;var value=calls.Second.Invoke(nativeAmount,nativeReal,out observed);nativeCount=checked(observed+1);return checked(value+2); // 原래 return import 😀\n'
selected[first]='long observed;var value=calls.Second.Invoke(amount,real,out observed);count=checked(observed+4);return value+0.5; // 직접 작성한 double 호출 😀\n'
(f.project/paths[first]).write_bytes(sources[first].encode());original_result=52;edited_result=42
(f.project/'Main.csbody').write_text('''// Fixture-only actual public/native return ABI and value probe; unchanged through Save.
var binding=calls.SharedCaller.GetType();
var importsType=binding.Assembly.GetType(binding.FullName+"Imports")!;
var imports=global::System.Activator.CreateInstance(importsType,true)!;
var properties=importsType.GetProperties();
if(properties.Length!=2)throw new global::System.Exception("two original native imports required");
bool changed=global::System.Environment.GetEnvironmentVariable("CONFECTORY_RETURN_PROBE")=="double";
var observed=new global::System.Collections.Generic.HashSet<long>();
var returns=new global::System.Collections.Generic.HashSet<double>();
foreach(var property in properties){
 var invoke=property.PropertyType.GetMethod("Invoke")!;
 if(invoke.ReturnType!=(changed?typeof(double):typeof(long))||invoke.GetParameters()[2].ParameterType!=typeof(long).MakeByRefType())throw new global::System.Exception("wrong runtime return/out ABI");
 object?[] arguments={30L,1.25,0L};
 object resultValue=invoke.Invoke(property.GetValue(imports),arguments)!;
 returns.Add(changed?(double)resultValue:(long)resultValue);
 observed.Add((long)arguments[2]!);
}
if(!returns.SetEquals(changed?new double[]{1.75,1.25}:new double[]{42,40})||!observed.SetEquals(changed?new long[]{38,34}:new long[]{35,34}))throw new global::System.Exception("wrong native return/out values");
int result=checked((int)calls.SharedCaller.Invoke(30,5));global::System.Console.WriteLine(result);return result;
''')
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};_base.snapshot=snapshot

def request():return _base.request()
def unchanged():assert all((f.project/path).read_bytes()==raw for path,raw in snapshot.items())
def verify_rows(rows):
 _base.verify_rows(rows);merged={v['id']:dict(draft=(f.project/v['path']).read_bytes().decode('utf-8-sig'))for v in f.metadata('describe',project=str(f.manifest))['units']}|rows
 for index,fn in enumerate(functions):
  before=snapshot[fn.split('::')[1]+'Body.celem'].decode().split('{',1)[1];after=merged[fn+'Body']['draft'].split('{',1)[1]
  if index==0:
   before=re.sub(r'import [^;]+ as Second \([^;]+;','',before);after=re.sub(r'import [^;]+ as Second \([^;]+;','',after);assert re.search(r'as Second \([^;]+\) -> double;',merged[fn+'Body']['draft'])
  assert before==after,(before,after)

def verify(checkpoint):
 rows={row['id']:row for row in json.loads(checkpoint.read_text())['changes']};verify_rows(rows);unchanged();ids=rows[owner]['atomicEditGroup'];assert set(functions+[fn+'Body'for fn in functions]+[fn+'Body/body:common'for fn in functions]+[owner,n.caller+'Body',n.caller+'Body/body:common'])<=set(ids);return ids

def verify_live():
 verify_rows({})
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description
 allowed=set(paths.values())|{'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{fn.split('::')[1]+'Body.celem'for fn in functions}|{str(n.a.info.relative_to(f.project)),'CallerBody.celem','caller.graph.json'}
 for path,raw in snapshot.items():
  if path not in allowed:assert(f.project/path).read_bytes()==raw,path
 execute(edited_result,'native-return-chain');f.checked('actual native returns double1.75/1.25 and out38/34; explicitly remapped shared caller executes42 with original helper bytes and input/out identities')

def after_contract(index):
 from playwright.sync_api import expect
 mapping=f.page.get_by_role('dialog',name='호출 계약 갱신',exact=True);expect(mapping).to_be_visible();mapping.locator('[data-abi-output=return]').select_option('count');mapping.locator('[data-abi-remap-accept]').click();expect(mapping).to_have_count(0);f.idle();held=d.pending();dialog=f.page.locator('[role=dialog]:has([data-code-source])');selector='[data-inline-method="'+functions[index]+'"] [data-function-edit], [data-inline-method="'+functions[index]+'"] [data-function-write-direct]'
 def open_editor():
  f.owner().locator(selector).click();expect(f.page.locator('[role=dialog]:has([data-code-source]), [role=dialog]:has([data-information-body])')).to_be_visible();choice=f.page.locator('[data-information-body="'+functions[index]+'Body/body:common"]')
  if choice.count():choice.click()
  expect(dialog).to_be_visible();field=dialog.locator('[data-code-source]');assert sources[functions[index]]in field.input_value();field.evaluate('(el,text)=>{el.focus();const p=el.value.indexOf(text);el.setSelectionRange(p,p+text.length);}',sources[functions[index]]);f.page.keyboard.insert_text(selected[functions[index]]);f.idle()
 open_editor();dialog.locator('[data-code-cancel]').click();assert d.pending()==held;open_editor();dialog.locator('[data-code-save]').click();expect(dialog).to_have_count(0);f.idle();saved=d.pending();f.owner().locator('[data-own-functions-toggle]').press('Control+z');assert d.pending()==held;f.owner().locator('[data-own-functions-toggle]').press('Control+y');assert d.pending()==saved
 if mode=='prior-ui'and index==1:
  import time
  checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));saved=checkpoint.read_bytes();pending=d.pending();mark=len(f.traffic);button=f.owner().locator('[data-element-action=save]');accepted=None
  if not button.is_disabled():
   button.click();deadline=time.monotonic()+90
   while time.monotonic()<deadline:
    ids={v['invoke']['requestId']for v in f.traffic[mark:]if v.get('invoke',{}).get('endpoint')=='blueprint'and v['invoke'].get('input',{}).get('action')=='applySlots'};answers=[v['result']for v in f.traffic[mark:]if v.get('result',{}).get('requestId')in ids and v['result'].get('error',{}).get('code')!='stale_revision']
    if answers:accepted=answers[-1];assert not accepted['ok'],accepted;break
    f.page.wait_for_timeout(20)
   assert accepted is not None
  assert d.pending()==pending and checkpoint.read_bytes()==saved;unchanged();(f.case/'prior-ui-rejection.json').write_text(json.dumps(dict(reply=accepted,saveDisabled=button.is_disabled(),pendingRetained=True,checkpointRetained=True,traffic=f.traffic[-25:]),ensure_ascii=False,indent=2));f.checked('prior UI rejects the coupled input/import Save and preserves both explicit inputs, original checkpoint, external sources and modes');f.browser.close();raise SystemExit(0)

