"""Generated, deferred, registered body files; no user or external source."""
import pathlib
import v666_finder_definitions_fixture as definitions
f=definitions.f;ns=definitions.ns
for manifest in f.projects:
 root=manifest.parent;body=root/'Main.csbody';value=body.read_text();marker='OtherProjectBodyOnly'if manifest==f.projects[1]else'BodyCommonNeedle 😀';body.write_text('// '+marker+'\n'+value)
 (root/'LinuxSearch.csbody').write_bytes(b'\xef\xbb\xbf'+b'// BodyLinuxNeedle\r\nreturn 42;\r\n')
 (root/'PreviewSearch.csbody').write_text('// TruncatedBodyPrefixNeedle\n// '+'x'*21000+'\n// TruncatedTailMustNotIndex\nreturn 0;\n')
 (root/'OversizeSearch.csbody').write_text('// OversizeBodyMustNotIndex\n'+'x'*1048577)
 owner=root/'MainBody.celem';s=owner.read_text();pos=s.rfind('}');owner.write_text(s[:pos]+'body linux "LinuxSearch.csbody";body preview "PreviewSearch.csbody";body windows "OversizeSearch.csbody";'+s[pos:])
f.outside=f.root/'OutsideBody.csbody';f.outside.write_text('// OutsideBodyMustNeverIndex\nreturn 99;\n');f.outside_bytes=f.outside.read_bytes()
f.before={str(p):p.read_bytes()for m in f.projects for p in m.parent.rglob('*')if p.is_file()}
