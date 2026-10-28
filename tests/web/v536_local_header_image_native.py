"""Original normalized image metadata candidates, never source writes or user files."""
import base64, hashlib, io, json, os, pathlib, struct, subprocess, sys, tempfile
from PIL import Image, ImageCms

repo = pathlib.Path(sys.argv[1]).resolve()
root = pathlib.Path(tempfile.mkdtemp(prefix='confectory-header-image-native-'))
n = 'Owned.Image::'
sources = {
    'Main': ('function', f'function {n}Main (long input,out bool active) -> long extends {n}FeatureBase {{ // preserve function source\nvalue Exact=9223372036854775805;}}'),
    'FeatureBase': ('function', f'function {n}FeatureBase (long input,out bool active) -> long {{description "preserved function parent";}}'),
    'Info': ('schema', f'schema {n}Info {{ // preserve schema source\nfield Count single general long;value editorInformationDefaults="typed-json-v1";value editorFieldDefault_Count="9223372036854775806";}}'),
    'Base': ('object', f'object {n}Base {{description "preserved parent";value editorIcon="🌿";}}'),
    'Item': ('object', f'object {n}Item extends {n}Base {{ // preserve object source\nuse schema {n}Info;data Count=9223372036854775805;}}'),
}
manifest = f'project Owned.Image version "1" {{standalone true;entry {n}Main;' + ''.join(f'element {key} {kind} "{key}.celem";' for key, (kind, _) in sources.items()) + '}'
project = root/'project.cproj'
project.write_text(manifest)
for key, (_, text) in sources.items(): (root/(key+'.celem')).write_text(text)
original = {p: p.read_bytes() for p in root.iterdir()}
checks = []

def image(alpha=False, lossless=False, size=(128, 128), profile=False):
    buffer = io.BytesIO()
    Image.new('RGBA' if alpha else 'RGB', size, (40, 90, 150, 123) if alpha else (40, 90, 150)).save(buffer, format='WEBP', quality=90, lossless=lossless, **({'icc_profile':ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()} if profile else {}))
    return buffer.getvalue()

def uri(raw): return 'data:image/webp;base64,' + base64.b64encode(raw).decode()

def call(changes, ok=True, owner='Info', operation=None, **extra):
    request = dict(operation=operation or ('functionPresentation' if owner=='Main' else 'informationDefinitions' if owner=='Info' else 'mixedOwnerCopyEdits'), project=str(project), manifest=manifest, id=n+owner, text=sources[owner][1], drafts=[dict(id=n+k, text=t) for k, (_, t) in sources.items() if k!=owner], changes=changes)
    request.update(extra)
    reply = subprocess.run([os.environ.get('CONFECTORY_DOTNET', '/workspace/toolchains/dotnet-10.0.401/dotnet'), str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')], input=json.dumps(request), text=True, capture_output=True, timeout=60)
    assert reply.returncode==0, reply.stderr
    data = json.loads(reply.stdout)
    assert data['ok']==ok, data
    assert all(p.read_bytes()==value for p, value in original.items())
    return data.get('result')

def check(text): checks.append(text); print('PASS '+text, flush=True)

for owner in ['Info','Item','Main']:
    for alpha, lossless, profile in [(a,l,p) for a in [False,True] for l in [False,True] for p in [False,True]]:
        value = uri(image(alpha, lossless, profile=profile))
        result = call([dict(type='description', text='선택 이미지와 설명'), dict(type='icon', text=value)], owner=owner)
        assert not result['sourceWritten'] and not result['compiled'] and not result['updates'] and not result['additions'] and result['manifest']==manifest
        assert ('// preserve function source' if owner=='Main' else '// preserve schema source' if owner=='Info' else '// preserve object source') in result['text'] and ('9223372036854775806' if owner=='Info' else '9223372036854775805') in result['text']
        view = call([], owner=owner, operation='effective', text=result['text'], schemaView=True)
        assert next(v['value'] for v in view['values'] if v['field']=='editorIcon')==value
        if owner=='Main':assert f'extends {n}FeatureBase' in result['text'] and sources['FeatureBase'][1]==original[root/'FeatureBase.celem'].decode()
        if owner=='Item':assert f'extends {n}Base' in result['text'] and sources['Base'][1]==original[root/'Base.celem'].decode()
        units = [dict(id=n+owner, kind=sources[owner][0], revision=0, textHash='0'*64, dirty=True, text=result['text'])]
        assert call([], operation='relationsMap', units=units)['nodes'][0]['icon']==value
check('opaque/alpha and lossy/lossless canvas WebP on information/object/function headers share one description/icon candidate and Browser projection; exact64/comments/parent/other sources remain untouched')

raw = image()
bad = [uri(image(size=(127, 128))), uri(raw[:-1]), uri(raw+b'X'), uri(b'<svg onload="bad"/>'), 'data:image/png;base64,AAAA', 'https://example.invalid/icon.webp', '/private/icon.webp', uri(raw)+' ', uri(raw).replace('base64,', 'base64,\n'), 'data:image/webp;base64,'+'A'*65500]
wrong = bytearray(raw); wrong[4:8] = struct.pack('<I', len(raw)); bad.append(uri(wrong))
unknown = b'JUNK'+struct.pack('<I', 2)+b'xx'; wrong = raw[:4]+struct.pack('<I', len(raw)-8+len(unknown))+raw[8:]+unknown; bad.append(uri(wrong))
for owner in ['Info','Item','Main']:
    for value in bad:
        call([dict(type='description', text='must not partially remain'), dict(type='icon', text=value)], owner=owner, ok=False)
check('wrong dimensions/container/base64/URI/mime/metadata and invalid last image reject the entire candidate without touching original sources')

value = uri(image(True))
for owner in ['Info','Item','Main']:call([dict(type='icon', text=value), dict(type='icon', text='★')], owner=owner, ok=False)
call([dict(type='schema-icon', path=['Count'], contract=dict(kind='general', type='long', cardinality='single'), schema=n+'Info', schemaHash=hashlib.sha256(sources['Info'][1].encode()).hexdigest(), text=value)], ok=False)
call([dict(type='description', text='no foreign owner'), dict(type='icon', text=value)], owner='Main', id='Foreign::Main',ok=False)
call([dict(type='icon',text=value)],owner='Main',operation='informationDefinitions',ok=False)
check('the image path remains information/object/direct-function-header-only; property/foreign-owner widening, duplicate edits and foreign operations remain rejected')
print(json.dumps(dict(checks=checks, evidence=str(root), sourceWritten=False, userFiles=False, projectRun=False)))
