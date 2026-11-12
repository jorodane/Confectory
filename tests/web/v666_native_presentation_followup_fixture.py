"""Four metadata rows edit only the already captured native function/source set."""
import copy,hashlib,json
import v666_native_header_contracts_fixture as _initial
for _key in dir(_initial):
 if not _key.startswith('_'):globals()[_key]=getattr(_initial,_key)
_native=_initial._prior
initial_guards=None;initial_request=None;initialized=False
followup_description='여러 기능 설명과 함께 저장하는 후속 정보 설명 😀';followup_icon='★'
function_descriptions={fn:'캡처한 기능의 후속 설명 '+str(index)+' 😀'for index,fn in enumerate(functions)}
undo_steps=1
original_start=f.start

def rpc(action,ok=True,**body):return f.invoke('blueprint',dict(action=action,**body),ok)['result'].get('result')
def start(index):
 global initialized,initial_request,initial_guards
 original_start(index)
 if initialized:return
 f.invoke('select',dict(id=owner));f.invoke('saveDraft',{});initial_request=_initial.request();f.invoke('schema',dict(id=owner));sc=f.state()['schema'];basis=rpc('readOwnerEdits',id=owner,hash=sc['textHash']);reply=rpc('applySlots',id=owner,rows=[],basis=basis['basis'],declaration=dict(id=owner,hash=sc['textHash'],changes=initial_request['changes']));assert reply['atomic']and reply['checkpointSaved'];checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));_initial.verify(checkpoint);initial_guards=copy.deepcopy(next(row for row in json.loads(checkpoint.read_text())['changes']if row['id']==owner)['slotSaveReceipt']['readGuards']);assert initial_guards and retained_file in initial_guards;initialized=True
 f.checked('initial explicit native ABI/body/caller group is saved once with its complete original dependency scope; source remains unconfirmed')
f.start=start

def request():
 checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));rows={row['id']:row for row in json.loads(checkpoint.read_text())['changes']};r=copy.deepcopy(initial_request);r['units'].update(copy.deepcopy(rows));changes=[dict(type='description',text=followup_description),dict(type='icon',text=followup_icon)]
 for index,fn in enumerate(functions):changes.append(dict(type='function-edit',id=fn,hash=hashlib.sha256(rows[fn]['draft'].encode()).hexdigest(),name=labels[index],description=function_descriptions[fn],signature=copy.deepcopy(nexts[index])))
 r['changes']=changes;return r

def verify_presentation(text):
 info=f.metadata('inspect',text=text);assert info['description']==globals().get('accepted_description',followup_description)and info['values']['editorIcon']==followup_icon,info

def verify_rows(rows):
 _native.verify_rows(rows)
 if owner in rows:verify_presentation(rows[owner]['draft'])
 for fn in functions:
  if fn in rows:assert f.metadata('inspect',text=rows[fn]['draft'])['description']==function_descriptions[fn]

def verify(checkpoint):
 ids=_native.verify(checkpoint);rows={row['id']:row for row in json.loads(checkpoint.read_text())['changes']};verify_presentation(rows[owner]['draft'])
 for fn in functions:assert f.metadata('inspect',text=rows[fn]['draft'])['description']==function_descriptions[fn]
 assert rows[owner]['slotSaveReceipt']['readGuards']==initial_guards
 return ids

def verify_live():
 _native.verify_live();path=next(row['path']for row in f.metadata('describe',project=str(f.manifest))['units']if row['id']==owner);verify_presentation((f.project/path).read_text())
 for fn in functions:assert f.metadata('inspect',text=(f.project/('elements/'+fn.split('::')[1]+'.celem')).read_text())['description']==function_descriptions[fn]
 f.checked('four metadata inputs Confirm with the original native ABI/body/caller group and unchanged dependency guards; source ownership and runtime40 retained')

def edit_contract(popover,index):popover.locator('[data-detail-description]').fill(function_descriptions[functions[index]])
def has_mapping_dialog(index):return False

def after_contract(index):
 if index!=0:return
 from playwright.sync_api import expect
 f.owner().locator('.object-title-description').fill(followup_description);f.idle();held=d.pending();assert len(held)==2
 f.owner().locator('.object-icon-edit').click();dialog=f.page.locator('.object-icon-popover');expect(dialog).to_be_visible();dialog.locator('[data-icon-choice="'+followup_icon+'"]').click();dialog.locator('[type=submit]').click();expect(dialog).to_have_count(0);f.idle();saved=d.pending();assert len(saved)==3
 f.owner().locator('.object-icon-edit').press('Control+z');assert d.pending()==held
 f.owner().locator('.object-icon-edit').press('Control+y');assert d.pending()==saved;f.checked('existing owner description/icon and function descriptions form four metadata inputs; original ABI and CSharp text stay selected')
