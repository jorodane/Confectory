"""Complete bounded registered-menu discovery across the existing 256-object page.

Synthetic files only; no execution or source writes by the authoring query.
"""
import json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

host=[os.environ["CONFECTORY_DOTNET"],sys.argv[1]]
repo=Path(__file__).resolve().parents[2]
ns="Example.EditorContextActions"

def query(project):
    request=dict(operation="editorMenuDeclarations",project=str(project),target="linux")
    return json.loads(subprocess.run(host,input=json.dumps(request),text=True,
                                     capture_output=True,check=True,timeout=30).stdout)

with tempfile.TemporaryDirectory(prefix="cf-menu-pages-") as temp:
    root=Path(temp)
    hidden=root/"registered-only";hidden.mkdir()
    (hidden/"pack.cpack").write_text('pack Synthetic.Hidden version "1" { element Hidden object "Hidden.celem"; }')
    (hidden/"Hidden.celem").write_text('object Synthetic.Hidden::Hidden { value editorContextMenu = true; value editorName = "Not a dependency"; }')
    for count in (40,255,256,257,400,530):
        folder=root/str(count);shutil.copytree(repo/"examples/editor-context-actions",folder)
        project=folder/"project.cpack"
        manifest=project.read_text().replace("../../packs/schema-editing/pack.cpack",str(repo/"packs/schema-editing/pack.cpack")).replace("../../targets/dotnet/pack.cpack",str(repo/"targets/dotnet/pack.cpack"))
        entries=[]
        for i in range(count-2):
            name=f"AAA{i:04}";path=folder/(name+".celem")
            path.write_text(f"object {ns}::{name} {{}}\n")
            entries.append(f'element {name} object "{path.name}";')
        project.write_text(manifest.rstrip()[:-1]+f' registry Synthetic.Hidden "{hidden/"pack.cpack"}";\n'+"\n".join(entries)+"\n}\n")
        original={p:p.read_bytes() for p in folder.glob("*") if p.is_file()}
        result=query(project)
        if count==530:
            assert not result["ok"] and "Menu discovery budget" in result["message"],result
        else:
            assert result["ok"],result
            actions=result["result"]["actions"]
            assert len(actions)==1 and actions[0]["id"]==ns+"::MetadataProposal" and actions[0]["available"],actions
            assert not result["result"]["executed"] and not result["result"]["sourceWritten"]
        assert all(p.read_bytes()==raw for p,raw in original.items())
        if count!=400:continue
        # The last filler is beyond the former cap. Changing a declared object
        # into a legitimate menu is immediately observed; no old discovery used.
        late=folder/"AAA0397.celem"
        body=(folder/"MetadataProposal.celem").read_text()
        late.write_text(body.replace(ns+"::MetadataProposal",ns+"::AAA0397").replace("메타데이터 변경안","Late added registration"))
        added=query(project)
        assert added["ok"] and len(added["result"]["actions"])==2,added
        assert added["result"]["actions"][0]["title"]=="Late added registration"
        assert added["result"]["actions"][0]["available"]
        assert added["result"]["version"]!=result["result"]["version"]
        late.write_bytes(original[late])
        assert query(project)["result"]==result["result"]
        for failure in ("missing","malformed","permission"):
            if failure=="missing":late.unlink()
            elif failure=="malformed":late.write_text(f"object {ns}::AAA0397 {{ !")
            else:late.chmod(0)
            try:
                denied=query(project)
                assert not denied["ok"],(failure,denied)
            finally:
                if failure=="permission":late.chmod(0o600)
                late.write_bytes(original[late])
        assert query(project)["result"]==result["result"]
    print("PASS 40/255/256/257/400 objects, late registration, fresh errors, direct dependency scope, existing global budget")
