"""Large exact registration proof, including the inverse archived-registration recovery."""
import hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
host=[os.environ["CONFECTORY_DOTNET"],sys.argv[1]]
def invoke(operation,**payload):
    return json.loads(subprocess.check_output(host,input=json.dumps(dict(operation=operation,**payload)),text=True))
def h(text):return hashlib.sha256(text.encode()).hexdigest()
with tempfile.TemporaryDirectory(prefix="cf-paged-retirement-proof-") as tmp:
    root=Path(tmp)/"project";root.mkdir()
    candidate=root/"candidate";candidate.mkdir()
    sources={
      "Main":("function",'function Alpha::Main () -> int { provide Alpha::Main with Alpha::Body; }'),
      "Body":("implementation",'implementation Alpha::Body for Alpha::Main () -> int { body common "main.csbody"; }'),
      "Target":("buildtarget",'buildtarget Alpha::Target { tool "not-called.dll"; }'),
      "Rules":("object",'object Alpha::Rules { use schema Alpha::Fields; data Count = 5; }'),
      "Fields":("schema",'schema Alpha::Fields { field Count single general long; }'),
      "ArchivedValue":("object",'object Alpha::ArchivedValue extends Alpha::Rules {}'),
    }
    for i in range(400-len(sources)-1):
        name=f"Extra{i:04}";sources[name]=("object",f"object Alpha::{name} {{}}")
    entries=[f'element {name} {kind} "{name}.celem";' for name,(kind,text) in sources.items()]
    full='project Alpha version "1" { standalone true; entry Alpha::Main; target linux Alpha::Target; target other Alpha::Target; '+" ".join(entries)+" }"
    reduced=full.replace('element ArchivedValue object "ArchivedValue.celem";','')
    for folder in (root,candidate):
        for name,(kind,text) in sources.items():(folder/f"{name}.celem").write_text(text)
        (folder/"main.csbody").write_text("return 0;")
    def verify(restore,late=False):
        old,new=(reduced,reduced.rstrip()[:-1]+' element ArchivedValue object "ArchivedValue.celem"; }') if restore else (full,reduced)
        (root/"project.cpack").write_text(old);(candidate/"project.cpack").write_text(new)
        if late:(candidate/f"Extra{400-len([x for x in sources if not x.startswith('Extra')])-2:04}.celem").write_text("invalid")
        child=sources["ArchivedValue"][1]
        request=dict(originalProject=str(root/"project.cpack"), candidateProject=str(candidate/"project.cpack"),target="linux",restore=restore,
          changes=["Alpha::ProjectManifest","project.cpack",h(old),new,"Alpha::ArchivedValue","ArchivedValue.celem",h(child),child])
        combined=invoke("prepareExistingSchemaObjectRetirement",**request)
        assert combined["ok"],combined
        proof=combined["result"]["proof"]
        if late:
            assert not proof["eligible"],proof
            return
        assert proof["eligible"] and proof["pagedReadProof"],proof
        assert len(proof["reads"])>235
        assert {Path(row["path"]).name for row in proof["reads"]}=={f"{name}.celem" for name in sources if name!="ArchivedValue"}|{"main.csbody"}
        (candidate/"project.cpack").write_text(combined["result"]["preparedManifest"])
        assert invoke("validateExistingSchemaObjectRetirement",**request)["result"]==proof
    verify(False);verify(True);verify(False,True)
    print("PASS exact 400 declaration retirement/recovery proof, full read set and changed candidate refusal",flush=True)
