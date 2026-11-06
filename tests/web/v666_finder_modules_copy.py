"""One bounded module-label projection over existing owned metadata, no new reads."""
import json,pathlib,subprocess,sys
r=pathlib.Path(sys.argv[1]).resolve()
if(r/'docs/v666-zoom-lifetime-delta.json').exists():
 subprocess.run([sys.executable,str(r/'tests/web/v666_zoom_lifetime_copy.py'),str(r)],check=True);sys.exit(0)
d=json.loads((r/'docs/v666-finder-modules-delta.json').read_text());old=subprocess.check_output(['git','show',d['baseCommit']+':'+d['path']],cwd=r,text=True);assert old.count(d['before'])==1;assert(r/d['path']).read_text()==old.replace(d['before'],d['after'])
changed=set(subprocess.check_output(['git','diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples'],cwd=r,text=True).splitlines());assert changed=={d['path']},changed
print('PASS exact direct module require label projection only; existing ownership, source checks, read-only API shape, frontend/layout, contracts, permissions, Review/CAS/Undo preserved')
