"""Explicit names and native text retain already owned local import sources."""
import json,sys
_added='--imports-boundary'not in sys.argv
if _added:sys.argv.append('--imports-boundary')
import v666_named_body_group_fixture as _named
if _added:sys.argv.remove('--imports-boundary')
for _key in dir(_named):
 if not _key.startswith('_'):globals()[_key]=getattr(_named,_key)
helper_header='StableBodyHelperBody.celem';retained_header='CallerBody.celem';retained_file=helper_body;retained_graph='caller.graph.json'
def verify_live():
 verify_rows({})
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description
 allowed=changed_source_paths|{'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{str(n.a.info.relative_to(f.project)),retained_graph}
 for path,raw in snapshot.items():
  if path not in allowed:assert(f.project/path).read_bytes()==raw,path
 execute(edited_result,'named-owned-imports');f.checked('actual program26 uses the explicit public name and selected native bodies; original helper code/contracts/alias, native declarations, IDs/routes and other C# stay exact')
