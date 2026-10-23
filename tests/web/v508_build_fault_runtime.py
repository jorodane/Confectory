"""Build an isolated fault-injected copy, never a deployed engine fault interface.
Arguments: repository, current generated editor source directory, output configuration JSON.
Only named /tmp copies of Save/FileStream providers are changed. Tests use fresh owned projects.
"""
from pathlib import Path
import os,json,shutil,subprocess,tempfile,sys
r=Path(sys.argv[1]).resolve();base=Path(sys.argv[2]).resolve();config=Path(sys.argv[3]).resolve();case=Path(tempfile.mkdtemp(prefix='confectory-slot-boundary-runtime-'));control=case/'fault-mode';control.write_text('off');ready=case/'fault-reached';app=case/'editor';shutil.copytree(base,app,ignore=shutil.ignore_patterns('.confectory','.build','bin','obj'))
for name in ['save','file-stream']:shutil.copytree(r/'packs'/name,case/name)
project=app/'project.cpack';s=project.read_text()
for name in ['save','file-stream']:s=s.replace(str(r/'packs'/name/'pack.cpack'),str(case/name/'pack.cpack'))
project.write_text(s)
# Include the current UI, not an older generated staging copy; pin only this owned test runtime.
shutil.copytree(r/'examples/editor-home/ui',app/'ui',dirs_exist_ok=True)
import re,hashlib
bundle=(r/'examples/editor-home/WebBundle.csbody').read_text();m=re.search(r'\n(\{.*\})\n',bundle,re.S);pins=json.loads(m[1])
for row in pins.values():
 if 'canonicalSha256' in row:
  data=(app/'ui'/row['file']).read_bytes().replace(b'\r\n',b'\n');row['canonicalSize']=len(data);row['canonicalSha256']=hashlib.sha256(data).hexdigest()
(app/'WebBundle.csbody').write_text(bundle[:m.start(1)]+json.dumps(pins,separators=(',',':'),ensure_ascii=False)+bundle[m.end(1):])

q=json.dumps(str(control));proof=json.dumps(str(ready));p=case/'file-stream/WriteAtomic.csbody';s=p.read_text();prefix='''string fixtureMode=System.IO.File.ReadAllText(CONTROL).Trim();bool fixtureCheckpoint=path.EndsWith("draft.json",StringComparison.Ordinal)&&text.Contains("slotSaveReceipt",StringComparison.Ordinal);bool fixtureActivity=path.Contains("project-activity",StringComparison.Ordinal);
'''.replace('CONTROL',q);s=prefix+s
partial='System.IO.File.WriteAllText(temporary,text,new System.Text.UTF8Encoding(false));'
s=s.replace(partial,'''if(fixtureCheckpoint&&fixtureMode=="write"){System.IO.File.WriteAllText(temporary,text[..(text.Length/2)],new System.Text.UTF8Encoding(false));System.IO.File.WriteAllText(CONTROL,"off");System.IO.File.WriteAllText(PROOF,"partial-temporary-checkpoint");throw new System.IO.IOException("Owned fixture partial temporary checkpoint failure");}'''.replace('CONTROL',q).replace('PROOF',proof)+partial)
needle='System.IO.File.Move(temporary,path,true);';s=s.replace(needle,'''if(fixtureCheckpoint&&fixtureMode=="write"){System.IO.File.WriteAllText(CONTROL,"off");System.IO.File.WriteAllText(PROOF,"before-checkpoint-rename");throw new System.IO.IOException("Owned fixture checkpoint write failure");}
if(fixtureActivity&&fixtureMode=="rollback-after-checkpoint"){System.IO.File.WriteAllText(CONTROL,"off");System.IO.File.WriteAllText(PROOF,"during-activity-write-after-checkpoint");throw new System.IO.IOException("Owned fixture second-file write failure");}
System.IO.File.Move(temporary,path,true);if(fixtureCheckpoint&&fixtureMode=="rollback")System.IO.File.WriteAllText(CONTROL,"rollback-after-checkpoint");'''.replace('CONTROL',q).replace('PROOF',proof));p.write_text(s)
p=case/'save/WriteChecked.csbody';s=p.read_text();needle='return path;';assert needle in s;s=s.replace(needle,'''if(saved.Contains("slotSaveReceipt",StringComparison.Ordinal)&&System.IO.File.ReadAllText(CONTROL).Trim()=="uncertain"){System.IO.File.WriteAllText(CONTROL,"off");System.IO.File.WriteAllText(PROOF,"after-successful-commit-before-return");throw new System.IO.IOException("Owned fixture uncertain post-commit result");}return path;'''.replace('CONTROL',q).replace('PROOF',proof));p.write_text(s)
p=case/'save/ApplySlots.csbody';s=p.read_text();needle='  if(ReferenceEquals(AppDomain.CurrentDomain.GetData(key),state))';assert needle in s;s=s.replace(needle,'''  if(System.IO.File.ReadAllText(CONTROL).Trim()=="pre-live"){System.IO.File.WriteAllText(CONTROL,"off");System.IO.File.WriteAllText(PROOF,"checkpoint-written-before-live-units-copy");System.Diagnostics.Process.GetCurrentProcess().Kill();}
'''.replace('CONTROL',q).replace('PROOF',proof)+needle);p.write_text(s)
env=os.environ.copy();env.update(DOTNET_CLI_HOME='/tmp/confectory-dotnet10-final',NUGET_PACKAGES='/tmp/confectory-site-nuget',CONFECTORY_DOTNET='/workspace/toolchains/dotnet-10.0.401/dotnet');env['PATH']=str(Path(env['CONFECTORY_DOTNET']).parent)+':'+env['PATH'];report=case/'build.json'
with report.open('w') as stdout,(case/'build.err').open('w') as stderr:result=subprocess.run([env['CONFECTORY_DOTNET'],str(r/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(project),'linux'],env=env,stdout=stdout,stderr=stderr)
record={'runtime':str(case),'report':str(report),'control':str(control),'proof':str(ready),'productionPackUnmodifiedByInjection':True,'injectedCopiesOnly':['save/ApplySlots.csbody','save/WriteChecked.csbody','file-stream/WriteAtomic.csbody'],'exit':result.returncode};config.write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2));print((case/'build.err').read_text()[-2000:]);raise SystemExit(result.returncode)
