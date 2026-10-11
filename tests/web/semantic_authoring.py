"""Ordinary EditorHome authoring of real declarations in the opened ButtonGame pack."""
import re
from playwright.sync_api import expect

def verify_schema_authoring(page,project,mount,send,envelope):
 prefix='Example.ButtonGame::'
 def browser():page.locator('#nav').click()
 def create(name,kind):
  browser();page.locator('#new-declaration-kind').select_option(kind);page.locator('#new-declaration-name').fill(name);page.locator('#new-declaration').click();expect(page.locator('.window[data-key="schema"] [data-schema-id]')).to_have_text(prefix+name,timeout=30000)
 def field(name,kind,type_name,cardinality='single'):
  form=page.locator('.window[data-key="schema"] .consumer-definition').filter(has=page.locator('legend').filter(has_text='새 필드'))
  form.locator('[data-definition="name"]').fill(name);form.locator('[data-definition="kind"]').select_option(kind);form.locator('[data-definition="type"]').fill(type_name);form.locator('[data-definition="cardinality"]').select_option(cardinality);form.locator('[data-operation="definition-apply"]').click();expect(page.locator('.window[data-key="schema"] legend').filter(has_text=name)).to_have_count(1,timeout=30000)
 def close():page.locator('.window[data-key="schema"] [data-close]').click()
 create('EntryMeta','schema');field('note','general','string');field('enabled','general','bool');close()
 create('SceneSpec','schema');field('child','compound',prefix+'EntryMeta');field('ticks','general','int','multiple');close()
 create('PreviewSettings','object');close();browser();page.locator('#advanced-source').click();expect(page.locator('#source')).to_be_visible();expect(page.locator('#status')).to_have_text('고급 소스 탐색',timeout=30000)
 # Explicit advanced author input attaches the schema using the existing source-draft operation.
 # No consumer-generated source formatter or additional execution pack is introduced.
 text='object '+prefix+'PreviewSettings { use schema '+prefix+'SceneSpec; data child = { note = ""; enabled = false; }; data ticks = [0, 2]; }\n'
 page.locator('#source').fill(text);page.locator('#apply').click();expect(page.locator('#status')).to_have_text('Shared draft updated',timeout=30000);page.locator('#schema').click();expect(page.locator('.window[data-key="schema"] [data-schema-id]')).to_have_text(prefix+'PreviewSettings',timeout=30000)
 def edit(name,value):
  input=page.locator('.window[data-key="schema"] [data-schema-field="'+name+'"]')
  if isinstance(value,bool):input.set_checked(value)
  else:input.fill(str(value))
  input.locator('..').get_by_role('button',name='Apply field',exact=True).click();expect(page.locator('#status')).to_have_text('Shared field draft updated',timeout=30000);expect(input).to_be_enabled(timeout=30000)
 edit('note','real nested value');edit('enabled',True);edit('ticks[1]',5);page.screenshot(path='/tmp/confectory-v196-schema-authoring.png',full_page=True)
 # A retained semantic window stays pinned while primary selection moves to its schema definition.
 close();browser();page.locator('#keep-properties').click();prop=page.locator('.window[data-key="editor-1"]');expect(prop.locator('[data-schema-id]')).to_have_text(prefix+'PreviewSettings')
 prop.locator('[data-schema-field="note"]').fill('unsent nested input');expect(prop.locator('[data-schema-origin="'+prefix+'EntryMeta"]')).to_have_count(1);prop.locator('[data-schema-origin="'+prefix+'SceneSpec"]').click();expect(page.locator('.window[data-key="schema"] [data-schema-id]')).to_have_text(prefix+'SceneSpec');expect(prop.locator('[data-schema-field="note"]')).to_have_value('unsent nested input');close();prop.locator('[data-close]').click();browser();page.locator('#retained-editors button').click();expect(prop.locator('[data-schema-field="note"]')).to_have_value('unsent nested input');prop.locator('[data-schema-field="note"]').locator('..').get_by_role('button',name='현재 값으로 되돌리기',exact=True).click();prop.locator('[data-operation="release-view"]').click();expect(page.locator('#retained-editors button')).to_have_count(0)
 browser();page.locator('#advanced-source').click();expect(page.locator('#status')).to_have_text('고급 소스 탐색',timeout=30000)
 state=mount();manifest_ids=[row['id'] for row in state['state']['units'] if row['kind']=='project'];assert len(manifest_ids)==1,state['state']['units'];assert send(envelope(state,'dispose'))['ok']
 for id in [prefix+'EntryMeta',prefix+'SceneSpec',prefix+'PreviewSettings',manifest_ids[0]]:page.locator('[data-review-id="'+id+'"]').check()
 page.locator('#review-group').click();expect(page.locator('#confirm')).to_be_enabled(timeout=30000)
 reviewed=mount();registration=next(row['after'] for row in reviewed['state']['review']['units'] if row['kind']=='project');locator=re.search(r'element\s+PreviewSettings\s+object\s+"([^"]+)"',registration);assert locator;source_path=project/locator.group(1);assert send(envelope(reviewed,'dispose'))['ok'];assert not source_path.exists(),'creation or Review bypassed final Confirm'
 page.locator('#confirm').click();expect(page.locator('#status')).to_have_text('Source confirmed',timeout=180000)
 assert 'real nested value' in source_path.read_text();assert 'data ticks = [0, 5];' in source_path.read_text();assert 'enabled = true;' in source_path.read_text();assert 'element PreviewSettings object' in (project/'project.cpack').read_text()
 browser();page.locator('[data-id="'+prefix+'Score"]').click();expect(page.locator('#advanced-source')).to_be_enabled(timeout=30000);close();browser();page.locator('#advanced-source').click();expect(page.locator('#status')).to_have_text('고급 소스 탐색',timeout=30000)
