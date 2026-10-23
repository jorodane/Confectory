"""Controlled transport admission faults for the runtime's actual projection-read helper."""
from pathlib import Path
import json,subprocess,sys,tempfile
repo=Path(sys.argv[1]).resolve();s=(repo/'examples/editor-home/ui/v508-runtime.js').read_text();start=s.index('async function readCurrentView(');end=s.index('\nconst operationFailures=',start);source=s[start:end]
harness='''let attempts=0,updates=0,alive=true,errors=[],checks=[];
const view={update:async()=>{updates++},call:async()=>{attempts++;if(errors.length)throw Error(errors.shift());return 'ready'}};
const reset=(list=[])=>{attempts=updates=0;alive=true;errors=[...list]};
const assert=(value,why)=>{if(!value)throw Error(why)};
const rejected=async(fn,message)=>{try{await fn()}catch(e){assert(e.message===message,e.message);return}throw Error('expected rejection '+message)};
reset(['stale_revision','stale_revision']);assert(await readCurrentView('schema',{},()=>alive)==='ready');assert(attempts===3&&updates===3,'bounded retry');checks.push('two unexecuted stale admissions retry the same projection, then succeed');
reset(['stale_revision','stale_revision','stale_revision']);await rejected(()=>readCurrentView('relationsMap',{},()=>alive),'stale_revision');assert(attempts===3,'retry limit');checks.push('third stale admission fails, no indefinite loop');
for(const endpoint of ['editObjectStructure','editField','saveDraft','confirmGroup']){reset();await rejected(()=>readCurrentView(endpoint,{}),'projection_read_required');assert(attempts===0&&updates===0,'mutation reached transport');}checks.push('mutation/save/Confirm endpoints are rejected before update or call');
for(const code of ['source_revision_conflict','consumer_error','timeout','connection_lost']){reset([code]);await rejected(()=>readCurrentView('schema',{}),code);assert(attempts===1,'unexpected execution retry');}checks.push('source CAS conflict, consumer failure and uncertain timeout/connection failures never retry');
reset();view.update=async()=>{updates++;alive=false};await rejected(()=>readCurrentView('localInventory',{},()=>alive),'scope_changed');assert(attempts===0,'stale scope called');checks.push('scope change during update stops before transport');
console.log(JSON.stringify({checks,controlledTransport:true,liveBackend:false},null,2));'''
r=subprocess.run(['node','--input-type=module','-e',source+'\n'+harness],text=True,capture_output=True);print(r.stdout);print(r.stderr,end='');raise SystemExit(r.returncode)
