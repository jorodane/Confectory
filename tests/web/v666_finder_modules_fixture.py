"""Owned direct module requirements; no inherited/foreign source search."""
import json
import v666_finder_content_fixture as f
ns='Example.FrameLoop::';owner=ns+'InterfaceBox';parent=ns+'BaseRules'
for manifest in f.projects:
 root=manifest.parent;direct='OtherProjectModuleAction'if manifest==f.projects[1]else'DirectModuleActionNeedle'
 rows={
  'DirectModuleActionNeedle':('function','function '+ns+'DirectModuleActionNeedle () -> int {}'),
  'OtherProjectModuleAction':('function','function '+ns+'OtherProjectModuleAction () -> int {}'),
  'ChangedModuleActionNeedle':('function','function '+ns+'ChangedModuleActionNeedle () -> int {}'),
  'InheritedModuleActionNeedle':('function','function '+ns+'InheritedModuleActionNeedle () -> int {}'),
  'BaseRules':('module','module '+parent+' {require '+ns+'InheritedModuleActionNeedle () -> int;description "ParentSecretMustNotJoin";}'),
  'InterfaceBox':('module','module '+owner+' {include '+parent+';require '+ns+direct+' () -> int;value editorName="같은 인터페이스";}'),
  'EmptyBox':('module','module '+ns+'EmptyBox {include '+parent+';value editorName="같은 인터페이스";}'),
 }
 for name,(_,text)in rows.items():(root/(name+'.celem')).write_text(text)
 text=manifest.read_text();end=text.rfind('}');manifest.write_text(text[:end]+''.join('element '+name+' '+kind+' "'+name+'.celem";'for name,(kind,_)in rows.items())+text[end:])
f.before={str(p):p.read_bytes()for m in f.projects for p in m.parent.rglob('*')if p.is_file()}
