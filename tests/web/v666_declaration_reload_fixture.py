"""Generated owned declaration forms; no user source or account."""
import v666_finder_content_fixture as f
ns='Example.FrameLoop::'
for manifest in f.projects:
 root=manifest.parent;sources={'ReloadCategory':('category','category '+ns+'ReloadCategory {description "원래 설명😀";value Exact=9223372036854775806;}'),'ReloadModule':('module','module '+ns+'ReloadModule {description "모듈 원문 보존";}')}
 for name,(_,text)in sources.items():(root/(name+'.celem')).write_text(text)
 text=manifest.read_text();end=text.rfind('}');manifest.write_text(text[:end]+''.join('element '+name+' '+kind+' "'+name+'.celem";'for name,(kind,_)in sources.items())+text[end:])
f.before={str(p):p.read_bytes()for m in f.projects for p in m.parent.rglob('*')if p.is_file()}
