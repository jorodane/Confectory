"""Ordinary CLI compile/Run of the typed linked-data reader, not game authoring."""
import json,os,subprocess,sys,tempfile
from pathlib import Path
repo=Path(sys.argv[1]).resolve();dotnet=os.environ['CONFECTORY_DOTNET'];cli=repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'
with tempfile.TemporaryDirectory(prefix='cf-linked-data-') as folder:
    root=Path(folder);project=root/'project.cpack'
    project.write_text(f'''project Alpha version "1" {{ standalone true; entry Alpha::Main;
registry Confectory.RuntimeBase {json.dumps(str(repo/'packs/runtime-base/pack.cpack'))}; dependency Confectory.RuntimeBase version "0.1.0";
registry Confectory.Build.DotNet {json.dumps(str(repo/'targets/dotnet/pack.cpack'))}; dependency Confectory.Build.DotNet version "0.1.0";
target portable Confectory.Build.DotNet::Portable; target linux Confectory.Build.DotNet::Linux;
element Main function "main.celem"; element MainBody implementation "body.celem"; element Rules object "rules.celem"; element Unlinked object "unlinked.celem"; element Fields schema "fields.celem"; }}''')
    (root/'main.celem').write_text('function Alpha::Main () -> int { provide Alpha::Main with Alpha::MainBody; use object Alpha::Rules; }')
    (root/'body.celem').write_text('implementation Alpha::MainBody for Alpha::Main () -> int { import Confectory.RuntimeBase::ReadDeclaredLong as Read (string,string) -> long; body common "body.csbody"; }')
    (root/'fields.celem').write_text('schema Alpha::Fields { field Good single general long; field Wrong single general string; field IntValue single general int; }')
    rules=root/'rules.celem';rules.write_text('object Alpha::Rules { use schema Alpha::Fields; data Good = 17; data Wrong = "17"; data IntValue = 17; }')
    (root/'unlinked.celem').write_text('object Alpha::Unlinked { use schema Alpha::Fields; data Good = 777; }')
    body='''Console.WriteLine(calls.Read.Invoke("Alpha::Rules","Good"));
foreach(var pair in new[]{("Alpha::Rules","Wrong"),("Alpha::Rules","IntValue"),("Alpha::Rules","Missing"),("Alpha::Unlinked","Good"),("Bravo::Rules","Good")}) {
 try { calls.Read.Invoke(pair.Item1,pair.Item2); return 8; } catch(ArgumentException) { }
} return 0;'''
    (root/'body.csbody').write_text(body)
    def run(expected):
        result=subprocess.run([dotnet,str(cli),'build',str(project),'linux'],text=True,capture_output=True,timeout=120,check=True)
        report=json.loads(result.stdout);executed=subprocess.run(report['run'],cwd=root,text=True,capture_output=True,timeout=20,check=True)
        assert executed.stdout.strip()==str(expected),executed.stdout
        return report['key']
    before=run(17);rules.write_text(rules.read_text().replace('Good = 17','Good = 41'));after=run(41)
    assert before!=after and (root/'body.csbody').read_text()==body
print('PASS exact linked long, wrong/missing type, unlinked and foreign object rejection, value-only relink')
