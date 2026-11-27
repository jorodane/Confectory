"""Exact local leaf-reference proof; no source writes or compiler needed."""
import pathlib,os,json,subprocess,hashlib,tempfile,sys
host=[os.environ['CONFECTORY_DOTNET'],sys.argv[1]]
with tempfile.TemporaryDirectory(prefix='reference-overlay-proof-') as d:
 p=pathlib.Path(d)
 source='object Alpha::Link { use schema Alpha::LinkInfo; data Target = Alpha::One; data Note = "same"; }'
 files={'Link':'object','LinkInfo':'schema','TargetInfo':'schema','One':'object','Two':'object','Wrong':'object'}
 (p/'project.cpack').write_text('project Alpha version "1" { '+' '.join(f'element {k} {v} "{k}.celem";' for k,v in files.items())+' }')
 contents={'Link':source,'LinkInfo':'schema Alpha::LinkInfo { field Target single reference Alpha::TargetInfo; field Note single general string; }','TargetInfo':'schema Alpha::TargetInfo { field Count single general long; }','One':'object Alpha::One { use schema Alpha::TargetInfo; data Count = 0; }','Two':'object Alpha::Two { use schema Alpha::TargetInfo; data Count = 7; value editorName = "Two"; }','Wrong':'object Alpha::Wrong {}'}
 for k,v in contents.items(): (p/(k+'.celem')).write_text(v)
 def call(target='Two',**kw):
  req=dict(operation='validateLongDataOverlay',originalProject=str(p/'project.cpack'),id='Alpha::Link',relative='Link.celem',baseline=hashlib.sha256(source.encode()).hexdigest(),after=source.replace('Alpha::One','Alpha::'+target))
  req.update(kw)
  return json.loads(subprocess.check_output(host,input=json.dumps(req),text=True))
 def eligible(v):return v.get('ok') and v.get('result',{}).get('eligible')
 good=call();assert eligible(good) and good["result"]["reference"] is True,good
 assert {pathlib.Path(x['path']).name for x in good['result']['reads']}=={'TargetInfo.celem','One.celem','Two.celem'}
 for name in ['Wrong','Missing','Link']: assert not eligible(call(name)),name
 for changed in ['object Alpha::Two extends Alpha::One {}','object Alpha::Two { use schema Alpha::TargetInfo; use implementation Alpha::PotentialCode; }','object Alpha::Two { use schema Alpha::LinkInfo; }','object Alpha::Two { use schema Alpha::TargetInfo; value always = true; }']:
  (p/'Two.celem').write_text(changed);assert not eligible(call()),changed
 (p/'Two.celem').write_text(contents['Two'].replace('"Two"','"Renamed"'));assert eligible(call())
 (p/'Two.celem').chmod(0);assert not eligible(call());(p/'Two.celem').chmod(0o600)
 assert not eligible(call(baseline='0'*64))
 assert not eligible(call(after=source.replace('Alpha::One','Alpha::Two').replace('same','different')))
 assert (p/'Link.celem').read_text()==source
 print('PASS pure reference edge proof, exact reads, invalid, missing, inherited, executable, retyped, metadata, permission, stale baseline, mixed edit')
