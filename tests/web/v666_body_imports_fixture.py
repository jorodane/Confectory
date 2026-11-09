"""Same-contract native bodies retain existing, exactly observed local imports."""
import copy,hashlib,json,subprocess
import v536_information_shared_bodies_fixture as _base
for _key in dir(_base):
 if not _key.startswith('_'):globals()[_key]=getattr(_base,_key)
helper=f.n+'StableBodyHelper';helper_file='StableBodyHelper.celem';helper_body='stable-helper.csbody'
for name,kind,text in [('StableBodyHelper','function','function '+helper+' (long value) -> long {provide '+helper+' with '+helper+'Body;}'),('StableBodyHelperBody','implementation','implementation '+helper+'Body for '+helper+' (long value) -> long {body common "'+helper_body+'";}')]:
 (f.project/(name+'.celem')).write_text(text);f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element '+name+' '+kind+' "'+name+'.celem";registry Confectory.Build.DotNet',1))
(f.project/helper_body).write_bytes('// 읽기 의존 원문 😀\r\nreturn checked(value+3);\r\n'.encode())
for fn in functions:
 local=fn.split('::')[1];p=f.project/('elements/'+local+'.celem');text=p.read_text();assert 'provide 'not in text;p.write_text(text.replace('{','{provide '+fn+' with '+fn+'Body;',1))
 p=f.project/(local+'Body.celem')
 if mode!='leaf':p.write_text(p.read_text().replace('{','{import '+helper+' as StableHelper (long) -> long;',1))
 sources[fn]='return calls.StableHelper.Invoke(checked(nativeAmount+nativeCount)); // '+labels[functions.index(fn)]+' · 원문 9223372036854775806 😀\n'
 selected[fn]='return calls.StableHelper.Invoke(checked(nativeAmount-nativeCount)); // '+labels[functions.index(fn)]+' · 직접 편집 9223372036854775806 😀\n'
 if mode=='leaf':
  sources[fn]=sources[fn].replace('calls.StableHelper.Invoke(checked(nativeAmount+nativeCount))','checked(nativeAmount+nativeCount)');selected[fn]=selected[fn].replace('calls.StableHelper.Invoke(checked(nativeAmount-nativeCount))','checked(nativeAmount-nativeCount)')
 (f.project/paths[fn]).write_bytes(sources[fn].encode())
(f.project/'MainBody.celem').write_text('implementation '+f.n+'MainBody for '+f.n+'Main () -> int {import '+n.caller+' as SharedCaller (long,long) -> long;body common "Main.csbody";}')
(f.project/'Main.csbody').write_text('int result=checked((int)calls.SharedCaller.Invoke(30,5));global::System.Console.WriteLine(result);return result;')
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};_base.snapshot=snapshot
def execute(expected,name):
 result=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(f.manifest),'portable'],env=f.env,text=True,capture_output=True);(f.case/(name+'-build.log')).write_text(result.stdout+result.stderr);assert result.returncode==0,result.stdout[-3000:]+result.stderr[-1000:];report=json.loads(result.stdout);run=subprocess.run(report['run'],env=f.env,text=True,capture_output=True);(f.case/(name+'-run.json')).write_text(json.dumps(dict(exit=run.returncode,stdout=run.stdout,stderr=run.stderr)));assert(run.returncode,run.stdout.strip())==(expected,str(expected)),(run.returncode,run.stdout,run.stderr)
def verify_live():
 _base.verify_live();execute(26,'same-contract-native-imports');f.checked('actual preserved shared caller executes both explicitly edited native bodies through the unchanged local helper: result26')
