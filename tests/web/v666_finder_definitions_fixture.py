"""Generated definition sources in the existing owned project fixture."""
import json,pathlib
import v666_finder_content_fixture as f
ns='Example.FrameLoop::'
f.definition_sources={}
for manifest in f.projects:
 root=manifest.parent
 members=[dict(id='stable-ready',name='EnumDefinitionNeedle 😀',icon='★'),dict(id='stable-done',name='완료 항목',icon='✓')]
 if manifest==f.projects[1]:members[0]['name']='OtherProjectEnumOnly'
 sources={
  'InvalidChoice.celem':'enum '+ns+'InvalidChoice {value editorEnumProfile="unknown-profile";}',
  'UnusedInfo.celem':'schema '+ns+'UnusedInfo {field UnplacedDefinitionNeedle single general string;field ExactDefinitionType single general long;}',
  'Signature.celem':'function '+ns+'Signature (int InputDefinitionNeedle) -> string {}',
  'Choice.celem':'enum '+ns+'Choice {value editorEnumProfile="nominal-members-v1";value editorEnumValues='+json.dumps(json.dumps(members,ensure_ascii=False,separators=(',',':')),ensure_ascii=False)+';description "EnumDescriptionNeedle";}',
 }
 kinds={'InvalidChoice':'enum','UnusedInfo':'schema','Signature':'function','Choice':'enum'}
 for name,text in sources.items():(root/name).write_text(text)
 text=manifest.read_text();end=text.rfind('}');manifest.write_text(text[:end]+''.join('element '+name[:-6]+' '+kinds[name[:-6]]+' "'+name+'";'for name in sources)+text[end:]);f.definition_sources[str(manifest)]=sources
f.before={str(p):p.read_bytes()for m in f.projects for p in m.parent.rglob('*')if p.is_file()}
