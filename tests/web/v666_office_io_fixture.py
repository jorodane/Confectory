"""Owned real OS-read scheduling probe, never a product hook or UI receipt injection."""
import pathlib,shutil,subprocess,json,os,time,hashlib,stat

def configure(f):
 root=f.case/'instrumented-engine';project=root/'editor';project.mkdir(parents=True)
 shutil.copytree(f.repo/'examples/editor-home',project,dirs_exist_ok=True,ignore=shutil.ignore_patterns('.confectory','.build','bin','obj'))
 gates=f.case/'owned-file-io';fifo=pathlib.Path(str(gates)+'.fifo');
 originals={}
 for name in ['edit-workspace','development-tools']:
  shutil.copytree(f.repo/'packs'/name,root/name)
  for p in (root/name).glob('*.csbody'):originals[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
 tool=root/'development-tools/Invoke.csbody';source=tool.read_text();anchor='try{\nSystem.Text.Json.Nodes.JsonNode result;'
 helper='''string[] ReadForOwnedIO(string target){var slot=System.Threading.Thread.GetNamedDataSlot("Owned.IO.ToolRead");var prior=System.Threading.Thread.GetData(slot);System.Threading.Thread.SetData(slot,true);try{return calls.Read.Invoke(draft,target);}finally{System.Threading.Thread.SetData(slot,prior);}}
'''
 assert source.count(anchor)==1;source=source.replace(anchor,helper+anchor)
 anchor='var u=calls.Read.Invoke(draft,id);if(model["nodeScope"]';assert source.count(anchor)==1;tool.write_text(source.replace(anchor,'var u=ReadForOwnedIO(id);if(model["nodeScope"]'))
 read=root/'edit-workspace/Read.csbody';source=read.read_text();anchor='lock(state){';assert source.count(anchor)==1
 probe='''
// Only this owned test engine inserts a real pipe read inside the unchanged edit lock.
string probe=Environment.GetEnvironmentVariable("CONFECTORY_OWNED_IO_PROBE")??"";
if(System.Threading.Thread.GetData(System.Threading.Thread.GetNamedDataSlot("Owned.IO.ToolRead")) is true&&probe.Length>0&&System.IO.File.Exists(probe+".arm")){
 System.IO.File.Delete(probe+".arm");System.IO.File.WriteAllText(probe+".entered","real-tool-read-holds-edit-lock");using var stream=System.IO.File.OpenRead(probe+".fifo");if(stream.ReadByte()!=1)throw new System.IO.IOException("Owned physical-read failure");}
'''
 read.write_text(source.replace(anchor,anchor+probe))
 manifest=project/'project.cpack';source=manifest.read_text().replace('"../../','"'+str(f.repo)+'/')
 for name in ['edit-workspace','development-tools']:source=source.replace(str(f.repo/'packs'/name/'pack.cpack'),str(root/name/'pack.cpack'))
 manifest.write_text(source)
 rows={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [tool,read]}
 (f.case/'io-instrumentation.json').write_text(json.dumps(dict(purpose='schedule real tool IO while holding real EditWorkspace lock; genuine native receipt and UI, no metadata injection',changedOwnedCopies=rows,originalHashes=originals,sourceRepositoryEdited=False),indent=2))
 command=[f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(manifest),'linux']
 built=subprocess.run(command,env=f.env,capture_output=True,text=True,timeout=240);(f.case/'instrumented-build.log').write_text(built.stdout+'\n'+built.stderr);assert built.returncode==0,built.stderr[-4000:]
 f.report=json.loads(built.stdout);os.mkfifo(fifo,0o600);owned=fifo.lstat();identity=(owned.st_dev,owned.st_ino);f.env['CONFECTORY_OWNED_IO_PROBE']=str(gates)
 def arm():
  for suffix in ['.entered','.arm','.released']:pathlib.Path(str(gates)+suffix).unlink(missing_ok=True)
  pathlib.Path(str(gates)+'.arm').write_text('once')
 def entered():return pathlib.Path(str(gates)+'.entered').exists()
 def release(success=True):
  if not entered()or pathlib.Path(str(gates)+'.released').exists():return
  deadline=time.monotonic()+5
  while time.monotonic()<deadline:
   try:
    fd=os.open(fifo,os.O_WRONLY|os.O_NONBLOCK)
    try:os.write(fd,bytes([1 if success else 0]))
    finally:os.close(fd)
    pathlib.Path(str(gates)+'.released').write_text('success'if success else'failure')
    return
   except OSError as e:
    if e.errno!=6:raise
    time.sleep(.02)
  raise AssertionError('owned pipe reader release deadline')
 def cleanup():
  current=fifo.lstat();assert stat.S_ISFIFO(current.st_mode)and(current.st_dev,current.st_ino)==identity and current.st_uid==os.getuid()and current.st_nlink==1
  (f.case/'owned-fifo-cleanup.json').write_text(json.dumps(dict(path=str(fifo),device=identity[0],inode=identity[1],hostExited=f.host is None or f.host.poll()is not None,releaseObserved=pathlib.Path(str(gates)+'.released').exists())))
  assert f.host is None or f.host.poll()is not None
  fifo.unlink()
 release.cleanup=cleanup
 return arm,entered,release
