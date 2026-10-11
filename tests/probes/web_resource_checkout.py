"""Ordinary EditorHome load using an actual Git autocrlf checkout; no provider/pack substitute."""
import hashlib,json,os,pathlib,re,shutil,signal,subprocess,sys,tempfile,time,urllib.request
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text())
resources=json.loads(re.search(r'\n(\{.*\})\n',(repo/'examples/editor-home/WebBundle.csbody').read_text()).group(1))
with tempfile.TemporaryDirectory(prefix='confectory-checkout-') as temporary:
 root=pathlib.Path(temporary);checkout=root/'repo'
 subprocess.run(['git','clone','--shared','--no-checkout',str(repo),str(checkout)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 def git(*args):return subprocess.run(['git','-c','core.autocrlf=true',*args],cwd=checkout,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 # Actual legacy checkout -> attributes pull; do not re-extract resources.
 git('checkout','-B','work/current','1d48031e9409fb3fcbcd616e190fabd55e38ea6d')
 ui=checkout/'examples/editor-home/ui'
 before={id:hashlib.sha256((ui/id).read_bytes()).hexdigest() for id in resources if (ui/id).is_file()}
 # Retained-byte assertions apply to resources whose declared content did not change.
 # A normal UI implementation update legitimately replaces app.js/consumer.css.
 unchanged={id for id,row in resources.items() if id in before and hashlib.sha256((ui/id).read_bytes().replace(b'\r\n',b'\n') if row.get('bytePolicy')=='utf8-lf-v1' else (ui/id).read_bytes()).hexdigest()==row.get('canonicalSha256',row.get('sha256'))}
 assert any(resources[id].get('bytePolicy')=='utf8-lf-v1' for id in unchanged) and any(resources[id]['mime']=='image/png' for id in unchanged)
 git('pull','--ff-only','origin','work/current')
 pulled={id:hashlib.sha256((ui/id).read_bytes()).hexdigest() for id in resources}
 assert all(before[id]==pulled[id] for id in unchanged),'pull unexpectedly rewrote unchanged resources'
 before=pulled
 def identity(row):return (row.get('canonicalSize',row.get('size')),row.get('canonicalSha256',row.get('sha256')))
 def start(label,success,diagnostic=""):
  env=os.environ.copy();env.update(CONFECTORY_UI='web',CONFECTORY_EDITOR_REPO=str(checkout),CONFECTORY_ENTRY_STORAGE=str(root/label),CONFECTORY_HOME_STORAGE=str(root/label))
  env.pop('CONFECTORY_WEB_PROJECT',None)
  with (root/(label+'.log')).open('w+') as log:
   host=subprocess.Popen(report['run'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
   try:
    deadline=time.monotonic()+60;url=None
    while time.monotonic()<deadline:
     log.flush();log.seek(0);text=log.read()
     for line in text.splitlines():
      if line.startswith('CONFECTORY_WEB_UI '):url=line.split(' ',1)[1]
     if url or host.poll() is not None:break
     time.sleep(.1)
    if not success:
     assert host.poll() is not None and not url,text
     assert diagnostic in text,'expected resource-specific rejection: '+diagnostic+'\n'+text
     assert str(checkout/'examples/editor-home/ui') not in text
    else:
     assert url,'actual EditorHome host did not start'
     origin=url.split('/#')[0]
     for id,row in resources.items():
      body=urllib.request.urlopen(origin+'/'+id,timeout=15).read();size,digest=identity(row);assert len(body)==size and hashlib.sha256(body).hexdigest()==digest,id
   finally:
    if host.poll() is None:os.killpg(host.pid,signal.SIGTERM)
    host.wait(timeout=15)
 assert any((ui/id).read_bytes().count(b'\r\n') for id,row in resources.items() if row.get('bytePolicy')=='utf8-lf-v1')
 start('retained-crlf',True)
 assert before=={id:hashlib.sha256((ui/id).read_bytes()).hexdigest() for id in resources},'host modified original working tree'
 # Fresh normal checkout obeys attributes, alongside the untouched retained CRLF checkout.
 lf=root/'fresh-lf';subprocess.run(['git','-c','core.autocrlf=true','clone', '--shared',str(repo),str(lf)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 saved=checkout;checkout=lf;start('fresh-lf',True);checkout=saved
 text_id=next(id for id,row in resources.items() if row.get('bytePolicy')=='utf8-lf-v1');text_file=ui/text_id;original=text_file.read_bytes()
 tests=[('content',bytes([62 if original[0]!=62 else 60])+original[1:],'SHA-256 mismatch for canonical UTF-8 LF'),('encoding',b'\xff'+original[1:],'invalid UTF-8 encoding'),('bom',b'\xef\xbb\xbf'+original,'UTF-8 LF policy forbids BOM'),('utf16',original.decode('utf-8').encode('utf-16'),'invalid UTF-8 encoding'),('bare-cr',original.replace(b'\r\n',b'\r',1),'UTF-8 LF policy forbids bare CR and NUL'),('raw-budget',b'x'*4194305,'per-resource byte budget exceeded')]
 try:
  for label,payload,error in tests:text_file.write_bytes(payload);start(label,False,"Resource '"+text_id+"': "+error)
 finally:text_file.write_bytes(original)
 binary_id=next(id for id,row in resources.items() if row['mime']=='image/png');binary_file=ui/binary_id;original=binary_file.read_bytes()
 try:binary_file.write_bytes(bytes([original[0]^1])+original[1:]);start('binary',False,"Resource '"+binary_id+"': SHA-256 mismatch for loaded bytes")
 finally:binary_file.write_bytes(original)
 assert before=={id:hashlib.sha256((ui/id).read_bytes()).hexdigest() for id in resources}
 print('PASS actual EditorHome retained CRLF after attribute pull and fresh LF; '+str(len(resources))+' canonical/exact snapshots; content/encoding/BOM/binary/budget rejection; original bytes unchanged')
