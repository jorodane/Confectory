"""Explicit common/linux C# edits share one owner Save and unchanged ABI."""
import copy,hashlib,json,subprocess,sys,time
_requested=sys.argv[3]if len(sys.argv)>3 else'normal'
if len(sys.argv)>3:sys.argv[3]='leaf'
import v666_body_imports_fixture as _prior
if len(sys.argv)>3:sys.argv[3]=_requested
for _key in dir(_prior):
 if not _key.startswith('_'):globals()[_key]=getattr(_prior,_key)
mode=_requested;_prior._base.mode=mode
targets=['common','linux'];undo_steps=2;body_paths={};body_sources={};body_edits={}
for fn in functions:
 header=f.project/(fn.split('::')[1]+'Body.celem');linux=paths[fn].replace('.csbody','-linux.csbody');header.write_text(header.read_text().replace('body common','body linux "'+linux+'";body common',1))
 for target,path in [('common',paths[fn]),('linux',linux)]:
  key=fn+'Body/body:'+target;body_paths[key]=path
  body_sources[key]=sources[fn]if target=='common'else sources[fn].replace('nativeCount)','nativeCount+2)')
  body_edits[key]=selected[fn]if target=='common'else selected[fn].replace('nativeCount)','nativeCount+2)')
  (f.project/path).write_bytes(body_sources[key].encode())
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};_prior._base.snapshot=snapshot
retained_header=functions[0].split('::')[1]+'Body.celem';retained_file='Main.csbody';retained_graph='caller.graph.json';original_result=40;edited_result=20

def request():
 r=n.request(copy.deepcopy(old),{'amount':'amount','count':'count'});fn=functions[1]
 r['changes'].append({'type':'function-edit','id':fn,'hash':hashlib.sha256(r['units'][fn]['draft'].encode()).hexdigest(),'name':labels[1],'description':'','signature':copy.deepcopy(old),'mapping':{'before':copy.deepcopy(old),'args':{'amount':'amount','count':'count'}}})
 for index,row in enumerate(r['changes']):
  row.update(name=labels[index],description='');args={k:r[k]for k in ['project','manifest','id','units']};bodies=f.metadata('informationFunctionBodies',**args,function=row['id'],includeBlueprintTargets=True);rows={key:body for key,body in bodies.items()if not body['caller']};assert set(rows)=={row['id']+'Body/body:'+target for target in targets},rows
  row['mapping']['bodies']={key:{k:body[k]for k in ['hash','path']}|{'beforeSignature':copy.deepcopy(native),'signature':copy.deepcopy(native),'contract':copy.deepcopy(old),'text':body_edits[key]}for key,body in rows.items()}
 return r

_base_verify_rows=_prior._base.verify_rows
def verify_rows(rows):
 _base_verify_rows(rows)
 merged={row['id']:{'draft':(f.project/row['path']).read_text()}for row in f.metadata('describe',project=str(f.manifest))['units']}|rows
 for key,text in body_edits.items():assert merged[key]['draft']==text,key
_prior._base.verify_rows=verify_rows
def verify(checkpoint):
 group=_prior._base.verify(checkpoint);assert set(body_edits)<=set(group);return group
def execute_both(edited,name):
 for target,expected in [('portable',20 if edited else 40),('linux',24 if edited else 44)]:
  built=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(f.manifest),target],env=f.env,text=True,capture_output=True);(f.case/(name+'-'+target+'-build.log')).write_text(built.stdout+built.stderr);assert built.returncode==0,built.stdout[-2500:]+built.stderr[-1000:];report=json.loads(built.stdout);run=subprocess.run(report['run'],env=f.env,text=True,capture_output=True);(f.case/(name+'-'+target+'-run.json')).write_text(json.dumps(dict(exit=run.returncode,stdout=run.stdout,stderr=run.stderr)));assert(run.returncode,run.stdout.strip())==(expected,str(expected)),(target,run.returncode,run.stdout,run.stderr)
def verify_live():
 verify_rows({})
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description
 allowed=set(body_paths.values())|{'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{str(n.a.info.relative_to(f.project))}
 for path,raw in snapshot.items():
  if path not in allowed:assert(f.project/path).read_bytes()==raw,path
 execute_both(True,'explicit-platform-bodies');f.checked('actual portable/common20 and Linux24 execute all four explicit C# bodies with unchanged caller, headers, contracts and target selection')

def after_contract(index):
 from playwright.sync_api import expect
 selector='[data-inline-method="'+functions[index]+'"] [data-function-edit], [data-inline-method="'+functions[index]+'"] [data-function-write-direct]'
 for target in targets:
  key=functions[index]+'Body/body:'+target;held=d.pending()
  def open_editor():
   f.owner().locator(selector).click();chooser=f.page.get_by_role('dialog',name='구현 선택',exact=True);expect(chooser).to_be_visible()
   for platform in targets:expect(chooser.locator('[data-information-body="'+functions[index]+'Body/body:'+platform+'"]')).to_be_visible()
   chooser.locator('[data-information-body="'+key+'"]').click();expect(chooser).to_have_count(0);dialog=f.page.locator('[role=dialog]:has([data-code-source])');expect(dialog).to_be_visible();return dialog
  def fill(dialog):
   field=dialog.locator('[data-code-source]');assert body_sources[key]in field.input_value();field.evaluate('(el,text)=>{el.focus();const i=el.value.indexOf(text);if(i<0)throw Error("Original target body absent");el.setSelectionRange(i,i+text.length);}',body_sources[key]);f.page.keyboard.insert_text(body_edits[key]);f.idle()
  dialog=open_editor();fill(dialog);dialog.locator('[data-code-cancel]').click();assert d.pending()==held
  dialog=open_editor();fill(dialog);f.page.screenshot(path=str(f.case/('explicit-target-'+str(index)+'-'+target+'.png')));dialog.locator('[data-code-save]').click();expect(dialog).to_have_count(0);f.idle();saved=d.pending();f.owner().locator('[data-own-functions-toggle]').press('Control+z');assert d.pending()==held;f.owner().locator('[data-own-functions-toggle]').press('Control+y');assert d.pending()==saved
 if index==1 and mode=='reproduce-ui':
  checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes();mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+60
  while time.monotonic()<deadline:
   ids={row['invoke']['requestId']for row in f.traffic[mark:]if row.get('invoke',{}).get('endpoint')=='blueprint'and row['invoke']['input'].get('action')=='applySlots'};replies=[row['result']for row in f.traffic[mark:]if row.get('result',{}).get('requestId')in ids]
   if replies:assert replies[-1]['ok']is False;break
   f.page.wait_for_timeout(20)
  else:raise AssertionError('No observed applySlots result')
  assert d.pending()==saved and checkpoint.read_bytes()==baseline;unchanged();f.checked('authored target chooser explicitly edits four bodies but published grouped Save alone rejects, preserving input and checkpoint');f.browser.close();raise SystemExit(0)
