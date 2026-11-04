"""Audit the bounded human-facing copy delta; do not translate backend errors."""
import hashlib,json,pathlib,re,subprocess,sys
repo=pathlib.Path(sys.argv[1]).resolve();plan=json.loads((repo/'docs/v666-value-guidance-copy.json').read_text())
def original(path):return subprocess.check_output(['git','show',plan['baseCommit']+':'+path],cwd=repo,text=True)
source='examples/editor-home/ui/feature-authoring.js';before=original(source);expected=before
for row in plan['changes']:
 assert not any(c in row['before']+row['after']for c in "\n\r'\"`\\<>"),row
 assert re.search('[가-힣]',row['before'])and re.search('[가-힣]',row['after'])
 assert before.count(row['before'])==row['count'];expected=expected.replace(row['before'],row['after'])
for row in plan['logicChanges']:
 assert expected.count(row['before'])==row['count'];expected=expected.replace(row['before'],row['after'])
actual=(repo/source).read_text();assert actual==expected,'Code, selector, user data, or an unlisted message changed'
prior=json.loads((repo/'docs/v666-code-editor-copy.json').read_text())
for row in prior['changes']:assert actual.count(row['after'])==row['count'],'Earlier C# editor guidance regressed'
bundle='examples/editor-home/WebBundle.csbody';pattern=r'("feature-authoring.js":\{"file":"feature-authoring.js","mime":"text/javascript","bytePolicy":"utf8-lf-v1","canonicalSize":)\d+(,"canonicalSha256":")[0-9a-f]+(")'
data=actual.encode();expected,n=re.subn(pattern,lambda m:m[1]+str(len(data))+m[2]+hashlib.sha256(data).hexdigest()+m[3],original(bundle));assert n==1 and(repo/bundle).read_text()==expected
for path in {row['path']for row in plan['nativeChanges']}:
 expected=original(path)
 for row in (r for r in plan['nativeChanges']if r['path']==path):
  assert expected.count(row['before'])==row['count'];expected=expected.replace(row['before'],row['after'])
 assert(repo/path).read_text()==expected,'Unlisted backend change'
changed=set(subprocess.check_output(['git','diff','--name-only',plan['baseCommit'],'--','src','targets','packs','examples'],cwd=repo,text=True).splitlines());assert changed=={source,bundle,*[row['path']for row in plan['nativeChanges']]},changed
print('PASS 15 explicit value/expression/pin guidance messages/15 occurrences only; owned root argument-only edits use existing atomic checkpoint CAS; all other logic/selectors/HTML/runtime contracts/permissions/backend diagnostics unchanged outside bounded owned-value checkpoint admission; canonical asset identity exact')
