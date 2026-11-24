"""Test the existing version-1 EditWorkspace writer and readers on a disposable copy.

Generate the input fixture with v821_cell_removal_history_ui.py compound-deep-guard.
Pass the resulting owned project directory and separately built previous checkouts.
Use --diagnose-candidate to reproduce the unsafe interpretation tested at 0e33a1e1.
The candidate is tested in memory and on a disposable copy only.
"""

import argparse
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


ROLES = {
    'EditWorkspace': {
        'Open': '(string,string,string) -> string',
        'Close': '(string) -> void',
        'Read': '(string,string) -> string[]',
        'EditBatch': '(string,string[],string[],long[],string[]) -> bool',
        'Export': '(string) -> string',
        'Restore': '(string,string) -> void',
        'History': '(string,string,string) -> string',
    },
    'SchemaEditing': {'Call': None, 'Describe': None, 'Inspect': None},
    'FileStream': {'Snapshot': None},
}
PACKS = {
    'EditWorkspace': 'packs/edit-workspace',
    'SchemaEditing': 'packs/schema-editing',
    'FileStream': 'packs/file-stream',
    'Build.DotNet': 'targets/dotnet',
}
GRAPH = 'Owned.Elements::PairBody/body:common'
INNER = GRAPH + '/node:other/node:nest/node:inner'
TAIL = GRAPH + '/node:other/node:nest/node:tail'
FINISH = GRAPH + '/node:other/node:finish'
SIBLING = GRAPH + '/node:body/node:inner'
UNRELATED = 'Owned.Elements::MainBody/body:common'

BODY = r'''
string Required(string name) => Environment.GetEnvironmentVariable("CF_HISTORY_"+name) ?? throw new ArgumentException(name);
string project=Required("PROJECT"), mode=Required("MODE"), checkpoint=Required("CHECKPOINT");
string graph=Required("GRAPH"), inner=Required("INNER"), tail=Required("TAIL"), finish=Required("FINISH"), sibling=Required("SIBLING"), unrelated=Required("UNRELATED");
string Hash(string text)=>Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(text))).ToLowerInvariant();
var owner=calls.Open.Invoke(project,"compatibility-probe","nested-cell-history");
try{
 string[] Read(string id)=>calls.Read.Invoke(owner,id);
 string Text(string id)=>Read(id)[3];
 System.Text.Json.Nodes.JsonNode Inspect()=>System.Text.Json.Nodes.JsonNode.Parse(calls.History.Invoke(owner,"inspect","{}"))!;
 void Check(bool passes){if(!passes)throw new InvalidOperationException("Workspace history assertion failed: "+mode);}
 void Edit(string[] ids,string[] texts){
  var observed=Array.ConvertAll(ids,Read);
  Check(calls.EditBatch.Invoke(owner,ids,texts,Array.ConvertAll(observed,row=>long.Parse(row[4])),Array.ConvertAll(observed,row=>Hash(row[3]))));
 }
 void Replay(string step,int undo,int redo){
  var preview=Inspect()[step]!;
  Check(preview["available"]!.GetValue<bool>());
  var result=System.Text.Json.Nodes.JsonNode.Parse(calls.History.Invoke(owner,step,System.Text.Json.JsonSerializer.Serialize(new{token=preview["token"]!.ToString()})))!;
  Check(result["accepted"]!.GetValue<bool>()&&result["undoCount"]!.GetValue<int>()==undo&&result["redoCount"]!.GetValue<int>()==redo);
 }
 if(mode=="write-legacy"){
  Edit([unrelated],[Text(unrelated)+"\n// Separate draft"]);
  var edited=System.Text.Json.Nodes.JsonNode.Parse(Text(sibling))!;
  edited["source"]=edited["source"]!.ToString()+"\r\n// Previous-reader saved edit";
  Edit([sibling],[edited.ToJsonString()]);
  Console.WriteLine(calls.Export.Invoke(owner));return 0;
 }
 if(mode=="candidate"){
  // Unchanged source inputs are observed by EditBatch but should be checked again at replay.
  Edit([graph,inner,tail,finish],[System.IO.File.ReadAllText(Required("AFTER")),Text(inner),Text(tail),Text(finish)]);
  Console.WriteLine(calls.Export.Invoke(owner));return 0;
 }
 string physicalGraph=Text(graph);
 string saved=System.IO.File.ReadAllText(checkpoint);
 string originalSibling=mode=="read-legacy"?Text(sibling):"";
 try{calls.Restore.Invoke(owner,saved);}
 catch(ArgumentException error) when(mode=="cold-observations"&&error.Message=="Saved history owner mismatch"){
  var history=Inspect();
  Check(Text(graph)==physicalGraph&&history["undoCount"]!.GetValue<int>()==0&&history["redoCount"]!.GetValue<int>()==0);
  return 0;
 }
 if(mode=="read-legacy"){
  var checkpointData=System.Text.Json.Nodes.JsonNode.Parse(saved)!;
  string Draft(string id)=>System.Linq.Enumerable.Single(checkpointData["changes"]!.AsArray(),row=>row!["id"]!.ToString()==id)!["draft"]!.ToString();
  Check(Text(graph)==physicalGraph&&Text(sibling)==Draft(sibling)&&Text(unrelated)==Draft(unrelated));
  Replay("undo",1,1);
  Check(Text(graph)==physicalGraph&&Text(sibling)==originalSibling&&Text(unrelated)==Draft(unrelated));
  Replay("redo",2,0);
  Check(Text(graph)==physicalGraph&&Text(sibling)==Draft(sibling)&&Text(unrelated)==Draft(unrelated));
  return 0;
 }
 Check(mode is "stale-candidate" or "cold-candidate");
 var recorded=System.Text.Json.Nodes.JsonNode.Parse(saved)!["history"]!["undo"]![0]!["units"]![0]!;
 Check(Text(graph)==recorded["after"]!.ToString());
 Replay("undo",0,1);
 Check(Text(graph)==recorded["before"]!.ToString());
 if(mode=="stale-candidate")Check(Text(inner)==System.IO.File.ReadAllText(Required("LEAF")));
 else{
  bool missing=false;
  try{Text(inner);}catch(ArgumentException error) when(error.Message=="Unknown owned unit."){missing=true;}
  Check(missing);
 }
 return 0;
}finally{calls.Close.Invoke(owner);}
'''


def build_reader(repo, directory, dotnet):
    directory.mkdir()
    names = {f'Confectory.{pack}::{name}' for pack, members in ROLES.items() for name in members}
    bindings = [line for line in (repo / 'examples/editor-home/Main.celem').read_text().splitlines()
                if line.startswith('provide ') and line.split()[1] in names]
    assert len(bindings) == len(names), bindings
    (directory / 'Main.celem').write_text('function Fixture.History::Main () -> int {\n'
                                        'provide Fixture.History::Main with Fixture.History::Body;\n'
                                        + '\n'.join(bindings) + '\n}')
    imports = '\n'.join(f'import Confectory.{pack}::{name} as {name} {signature};'
                        for pack, members in ROLES.items() for name, signature in members.items() if signature)
    (directory / 'Body.celem').write_text('implementation Fixture.History::Body for Fixture.History::Main () -> int {\n'
                                        + imports + '\nbody common "Main.csbody";\n}')
    (directory / 'Main.csbody').write_text(BODY)
    declarations = '\n'.join(f'registry Confectory.{pack} {json.dumps(str(repo / path / "pack.cpack"))}; '
                             f'dependency Confectory.{pack} version "0.1.0";' for pack, path in PACKS.items())
    manifest = directory / 'project.cpack'
    manifest.write_text('project Fixture.History version "1.0.0" { standalone true; entry Fixture.History::Main;\n'
                        'element Main function "Main.celem"; element Body implementation "Body.celem";\n'
                        + declarations + '\ntarget portable Confectory.Build.DotNet::Portable;\n}')
    env = dict(os.environ, CONFECTORY_DOTNET=dotnet, CONFECTORY_ELEMENT_AUTHORING_HOST=str(
        repo / 'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'))
    result = subprocess.run([dotnet, str(repo / 'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),
                             'build', str(manifest), 'portable'], env=env, cwd=repo, capture_output=True, text=True)
    assert result.returncode == 0, (repo, result.stdout[-4000:], result.stderr[-4000:])
    return json.loads(result.stdout)['run'], env


def verify(args, scratch):
    project = scratch / 'owned project'
    project.mkdir()
    for path in args.fixture.iterdir():
        if path.is_file() and not path.is_symlink():
            shutil.copyfile(path, project / path.name)
    graph_file = project / 'Pair.graph.json'
    original = {file: file.read_bytes() for file in project.iterdir()}
    graph = json.loads(original[graph_file])
    selected, = (node for node in graph['nodes'] if node['id'] == 'other')
    nested, = (node for node in selected['graph']['nodes'] if node['kind'] == 'graph')
    assert [node['id'] for node in selected['graph']['nodes']] == ['nest', 'finish']
    assert [node['id'] for node in nested['graph']['nodes']] == ['inner', 'tail']
    graph['nodes'].remove(selected)
    graph['edges'] = [edge for edge in graph['edges'] if edge['from'] != 'other']
    next(edge for edge in graph['edges'] if edge['to'] == 'other')['to'] = 'after'
    after = scratch / 'removed.json'
    after.write_text(json.dumps(graph))
    leaf = project / 'Pair.other.inner.node.json'
    dotnet = os.environ.get('CONFECTORY_DOTNET') or shutil.which('dotnet')
    assert dotnet, 'A local .NET 10 SDK is required'
    repos = [args.current, *args.previous]
    runners = [build_reader(repo, scratch / f'reader-{index}', dotnet) for index, repo in enumerate(repos)]

    def run(index, mode, checkpoint, expected):
        command, env = runners[index]
        saved = checkpoint.read_bytes() if checkpoint.exists() else None
        params = dict(PROJECT=str(project / 'project.cproj'), MODE=mode, CHECKPOINT=str(checkpoint),
                      GRAPH=GRAPH, INNER=INNER, TAIL=TAIL, FINISH=FINISH, SIBLING=SIBLING, UNRELATED=UNRELATED,
                      AFTER=str(after), LEAF=str(leaf))
        result = subprocess.run(command, env=dict(env, **{'CF_HISTORY_' + key: value for key, value in params.items()}),
                                cwd=scratch, capture_output=True, text=True)
        assert result.returncode == 0, (repos[index], mode, result.stdout, result.stderr)
        assert {file: file.read_bytes() for file in project.iterdir()} == expected
        assert (checkpoint.read_bytes() if checkpoint.exists() else None) == saved
        return result.stdout

    legacy = scratch / 'legacy.json'
    legacy.write_text(run(1, 'write-legacy', legacy, original))
    saved = json.loads(legacy.read_text())
    assert saved['version'] == 1 and saved.get('cellHistoryProfile') is None
    assert {row['id'] for row in saved['changes']} == {SIBLING, UNRELATED}
    for index, repo in enumerate(repos):
        run(index, 'read-legacy', legacy, original)
        print(f'PASS {repo.name} cold legacy v1 read, Undo/Redo, separate draft and bytes retained', flush=True)

    if not args.diagnose_candidate:
        return
    candidate = scratch / 'candidate.json'
    candidate.write_text(run(1, 'candidate', candidate, original))
    batch = json.loads(candidate.read_text())
    entry, = batch['history']['undo']
    assert batch['version'] == 1 and 'cellRemoval' not in entry
    assert [row['id'] for row in entry['units']] == [GRAPH]
    changed_leaf = json.loads(original[leaf])
    changed_leaf['source'] += '\n// Changed after the original batch observation'
    leaf.write_text(json.dumps(changed_leaf))
    for index, repo in enumerate(repos):
        run(index, 'stale-candidate', candidate, original | {leaf: leaf.read_bytes()})
        print(f'PASS {repo.name} exposed the candidate gap: generic Undo accepts a changed retained leaf', flush=True)

    leaf.write_bytes(original[leaf])
    graph_file.write_bytes(after.read_bytes())  # Simulate the physical state after Confirm in the test copy only.
    batch['changes'] = []
    candidate.write_text(json.dumps(batch))
    observed = copy.deepcopy(batch)
    for node, source_id in [('inner', INNER), ('tail', TAIL), ('finish', FINISH)]:
        name = f'Pair.other.{node}.node.json'
        text = original[project / name].decode()
        observed['history']['undo'][0]['units'].append(
            dict(id=source_id, kind='blueprint-node', path=name, before=text, after=text))
    observations = scratch / 'observations.json'
    observations.write_text(json.dumps(observed))
    for index, repo in enumerate(repos):
        files = original | {graph_file: after.read_bytes()}
        run(index, 'cold-candidate', candidate, files)
        run(index, 'cold-observations', observations, files)
        print(f'PASS {repo.name} exposed cold locator loss and rejected a synthetic guarded v1 entry atomically', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('fixture', type=Path, help='Owned project generated by the deep-guard GUI test')
    parser.add_argument('--current', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--previous', type=Path, action='append', required=True, help='Built previous reader checkout')
    parser.add_argument('--diagnose-candidate', action='store_true', help='Reproduce the 0e33a1e1 candidate limitations')
    args = parser.parse_args()
    args.current = args.current.resolve()
    args.previous = [reader.resolve() for reader in args.previous]
    with tempfile.TemporaryDirectory(prefix='cf-nested-v1-') as folder:
        verify(args, Path(folder))
