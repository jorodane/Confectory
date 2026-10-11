"""Ordinary EditorHome load using an actual Git autocrlf checkout; no provider/pack substitute."""
import hashlib,json,os,pathlib,re,shutil,signal,subprocess,sys,tempfile,time,urllib.request
repo=pathlib.Path(sys.argv[1]).resolve();report=json.loads(pathlib.Path(sys.argv[2]).read_text())
resources=json.loads(re.search(r'\n(\{.*\})\n',(repo/'examples/editor-home/WebBundle.csbody').read_text()).group(1))
with tempfile.TemporaryDirectory(prefix='confectory-checkout-') as temporary:
 root=pathlib.Path(temporary);checkout=root/'repo'
 subprocess.run(['git','clone','--shared','--no-checkout',str(repo),str(checkout)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 def git(*args):return subprocess.run(['git','-c','core.autocrlf=true',*args],cwd=checkout,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 git('checkout','--force','HEAD')
 # Recreate the previous revision's absent attributes in this isolated clone index.
 git('rm','--cached','--ignore-unmatch','.gitattributes');(checkout/'.gitattributes').unlink(missing_ok=True)
 def checkout_resources():
  for id in resources:(checkout/'examples/editor-home/ui'/id).unlink(missing_ok=True)
  git('checkout-index','--force','--',*['examples/editor-home/ui/'+id for id in resources])
 def start(label,success):
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
     assert "Resource 'ConfectoryIcon.svg': size mismatch; expected=1373, actual=1382" in text,text
     assert str(checkout/'examples/editor-home/ui') not in text
    else:
     assert url,'actual EditorHome host did not start'
     origin=url.split('/#')[0]
     for id,row in resources.items():
      body=urllib.request.urlopen(origin+'/'+id,timeout=15).read();assert len(body)==row['size'] and hashlib.sha256(body).hexdigest()==row['sha256'],id
   finally:
    if host.poll() is None:os.killpg(host.pid,signal.SIGTERM)
    host.wait(timeout=15)
 checkout_resources();start('legacy-crlf',False)
 shutil.copyfile(repo/'.gitattributes',checkout/'.gitattributes');git('add','.gitattributes');checkout_resources()
 for id,row in resources.items():
  body=(checkout/'examples/editor-home/ui'/id).read_bytes();assert len(body)==row['size'] and hashlib.sha256(body).hexdigest()==row['sha256'],id
 start('fixed-lf',True)
 print('PASS actual EditorHome legacy CRLF rejection, LF Windows checkout and all '+str(len(resources))+' pinned resource snapshots')
