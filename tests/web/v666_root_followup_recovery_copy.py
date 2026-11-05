"""Only retain the validated closure of already-retained author receipts."""
import json,pathlib,re,subprocess,sys
r=pathlib.Path(sys.argv[1]).resolve();plan=json.loads((r/'docs/v666-root-followup-recovery-delta.json').read_text());path='packs/edit-workspace/Export.csbody';assert len(plan['deltas'])==1;v=plan['deltas'][0];assert v['path']==path and v['count']==1
original=subprocess.check_output(['git','show',plan['baseCommit']+':'+path],cwd=r,text=True);assert original==v['before'] and(r/path).read_text()==v['after']
changed=set(subprocess.check_output(['git','diff','--name-only',plan['baseCommit'],'--','src','targets','packs','examples'],cwd=r,text=True).splitlines());assert changed=={path},changed
flags=lambda text:set(re.findall(r'authorSaveReceipt"\]\?\["(owned\w+)"',text));assert flags(original)==flags(v['after']) and len(flags(original))==11
assert v['after'].count('RetainAuthor(')==3 and 'RetainAuthor(member,id!.ToString())'in v['after'] and 'RetainAuthor(unit,entry.Key)'in v['after']
for name in ['packs/edit-workspace/Restore.csbody','packs/edit-workspace/ValidateReviewSelection.csbody','packs/pack-workspace/Blueprint.csbody','examples/editor-home/ui/feature-authoring.js','examples/editor-home/WebBundle.csbody']:
 assert(r/name).read_text()==subprocess.check_output(['git','show',plan['baseCommit']+':'+name],cwd=r,text=True)
print('PASS exact retained-root-closure delta only; same 11 durable receipt flags and graph binding; restore/permissions/ABI/source/UI/layout unchanged')
