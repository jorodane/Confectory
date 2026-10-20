"""Opt-in pinned official CLI probe: fresh empty account home, child seccomp
network denial, initialize and account/read only. Never login, model/list or turn.
No token/config copies; raw stderr and the owned temporary tree are removed.
"""
import ctypes,ctypes.util,errno,json,os,pathlib,re,selectors,shutil,socket,subprocess,sys,tempfile,time
repo=pathlib.Path(__file__).resolve().parents[2]
def deny_child_network():
    lib = ctypes.CDLL(ctypes.util.find_library("seccomp") or "libseccomp.so.2", use_errno=True)
    lib.seccomp_init.argtypes = [ctypes.c_uint32]
    lib.seccomp_init.restype = ctypes.c_void_p
    lib.seccomp_syscall_resolve_name.argtypes = [ctypes.c_char_p]
    lib.seccomp_syscall_resolve_name.restype = ctypes.c_int
    lib.seccomp_rule_add.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int, ctypes.c_uint]
    lib.seccomp_load.argtypes = [ctypes.c_void_p]
    lib.seccomp_release.argtypes = [ctypes.c_void_p]
    context = lib.seccomp_init(0x7FFF0000)  # ALLOW except explicit network syscall denies.
    if not context:
        raise RuntimeError("No network guard; refusing to start CLI")
    try:
        # Prevent io_uring from performing networking outside these syscall hooks.
        for name in ("socket", "connect", "sendto", "sendmsg", "sendmmsg",
                     "io_uring_setup", "io_uring_enter", "io_uring_register"):
            number = lib.seccomp_syscall_resolve_name(name.encode())
            if number < 0 or lib.seccomp_rule_add(context, 0x50000 | errno.EPERM, number, 0) != 0:
                raise RuntimeError("Network guard rule unavailable")
        if lib.seccomp_load(context) != 0:
            raise RuntimeError("Network guard load failed")
    finally:
        lib.seccomp_release(context)
    # In this same child BEFORE exec, prove an Internet socket cannot be created.
    for family in (socket.AF_INET, socket.AF_INET6, socket.AF_UNIX):
        try:
            candidate = socket.socket(family)
        except PermissionError:
            continue
        candidate.close()
        raise RuntimeError("Network guard ineffective; refusing to exec")

assert sys.platform=='linux' and len(sys.argv)==2
binary=pathlib.Path(sys.argv[1]);assert binary.is_absolute() and binary.is_file()
root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-official-no-account-'));home=root/'empty-home';scratch=root/'scratch';home.mkdir();scratch.mkdir();env={'CODEX_HOME':str(home),'TMPDIR':str(scratch),'TMP':str(scratch),'TEMP':str(scratch),'PATH':'/usr/bin:/bin'}
version=subprocess.run([str(binary),'--version'],env=env,cwd=scratch,preexec_fn=deny_child_network,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=10);text=version.stdout.decode().strip();assert re.fullmatch(r'codex-cli 0\.159\.0-alpha\.3',text),text
features=re.search(r'string\[\] deniedFeatures=\{([^}]+)\}',(repo/'packs/agent-codex/Provider.csbody').read_text()).group(1);features=re.findall(r'"([a-z0-9_]+)"',features)
args=[str(binary),'app-server','--stdio','--strict-config','-c','web_search="disabled"','-c','cli_auth_credentials_store="ephemeral"']
for f in features:args+=['--disable',f]
args+=['-c','notify=[]'];record={'version':text,'network':'child seccomp denies socket/connect/send and io_uring','freshOwnedHome':True,'platform':'Linux','sentMethods':[],'liveLoginOrModelRequests':False};process=None
try:
 with (root/'owned-stderr.txt').open('wb') as err:
  process=subprocess.Popen(args,env=env,cwd=scratch,preexec_fn=deny_child_network,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,start_new_session=True);selector=selectors.DefaultSelector();selector.register(process.stdout,selectors.EVENT_READ);pending=bytearray()
  def rpc(serial,method,params):
   record['sentMethods'].append(method);process.stdin.write((json.dumps({'id':serial,'method':method,'params':params})+'\n').encode());process.stdin.flush();end=time.monotonic()+12
   while time.monotonic()<end:
    if not selector.select(max(0,end-time.monotonic())):raise TimeoutError('bounded-rpc-timeout')
    chunk=os.read(process.stdout.fileno(),65536)
    if not chunk:raise RuntimeError('stdio-ended-before-response')
    pending.extend(chunk);assert len(pending)<=1048576
    while b'\n' in pending:
     line,_,rest=pending.partition(b'\n');pending[:]=rest;obj=json.loads(line)
     if obj.get('id')==serial and 'method' not in obj:
      if 'error' in obj:record['rpcCode']=obj['error'].get('code');raise RuntimeError('rpc-error')
      return obj['result']
   raise TimeoutError('bounded-rpc-timeout')
  init=rpc(1,'initialize',{'clientInfo':{'name':'confectory','title':'Confectory','version':'0.1.0'},'capabilities':{'experimentalApi':True}});record['initialization']='passed';process.stdin.write(b'{"method":"initialized","params":{}}\n');process.stdin.flush();account=rpc(2,'account/read',{'refreshToken':False});assert account.get('account') is None,'Unexpected account: abort';record['account']='null';record['result']='passed'
except Exception as e:record['result']='failed';record['failureKind']=str(e) if str(e) in ('bounded-rpc-timeout','stdio-ended-before-response','rpc-error') else type(e).__name__
finally:
 if process is not None:
  process.stdin.close()
  try:process.wait(timeout=3)
  except subprocess.TimeoutExpired:process.kill();process.wait(timeout=3)
  record['exitCode']=process.returncode
 stderr=(root/'owned-stderr.txt').read_text(errors='replace')
 record['stderrCategory']='unknown-feature' if 'Unknown feature' in stderr or 'unknown feature' in stderr else 'argument' if 'unexpected argument' in stderr else 'configuration' if 'config' in stderr.lower() else 'other' if stderr else 'none'
 assert not (home/'auth.json').exists();record['authFileCreated']=False;print(json.dumps(record,indent=2));shutil.rmtree(root)
assert record['result']=='passed',record
