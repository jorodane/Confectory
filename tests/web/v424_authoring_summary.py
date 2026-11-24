"""Ordinary authoring host semantic summaries retain advanced review for uncovered edits."""
import json,subprocess,sys
from pathlib import Path
from tempfile import TemporaryDirectory
exe,host=sys.argv[1:]
def summary(kind,before,after,**scope):
 result=subprocess.run([exe,host],input=json.dumps(dict(operation='reviewSummary',kind=kind,before=before,after=after,**scope)),text=True,capture_output=True,timeout=15);assert result.returncode==0,result.stderr;reply=json.loads(result.stdout);assert reply["ok"],reply;return reply["result"]
s=summary('function','','function Demo::Fn (int count, string[] names) -> bool { }');assert not s['additionalChanges'];assert {x['label'] for x in s['changes']}=={'선언 생성','기능 계약'}
a='function Demo::Fn (int count) -> bool { }';b='function Demo::Fn (long amount) -> string[] { }';s=summary('function',a,b);assert not s['additionalChanges'] and len(s['changes'])==1;assert 'count' in s['changes'][0]['before'] and 'amount' in s['changes'][0]['after']
a='module Demo::Module { }';b='module Demo::Module { require Demo::Fn (int) -> int; default Demo::Fn with Demo::Impl; provide Demo::Fn with Demo::Impl; include Demo::Other; }';s=summary('module',a,b);assert not s['additionalChanges'];assert {x['label'] for x in s['changes']}=={'필요 기능','기본 구현','제공 구현','포함'}
a='module Demo::Module { include Demo::One; include Demo::Two; }';b='module Demo::Module { include Demo::Two; include Demo::One; }';s=summary('module',a,b);assert not s['additionalChanges'] and len(s['changes'])==1
for kind,a,b in [
 ('function','function Demo::Fn () -> int { }','function Demo::Fn () -> int { // extra comment\n }'),
 ('function','function Demo::Fn () -> int { }','function Demo::Renamed () -> int { }'),
 ('implementation','implementation Demo::Impl for Demo::Fn () -> int {body common "old.csbody";}','implementation Demo::Impl for Demo::Fn () -> int {body common "new.csbody";}'),
 ('module','module Demo::Module { }','module Demo::Module { option target "linux"; }'),
 ('function','function Demo::Fn () -> int { }','invalid source'),
]:assert summary(kind,a,b)['additionalChanges'],(kind,a,b)
print('PASS authoring contract/module summaries: exact signatures, binding/order changes; body/identity/tool/comment/invalid edits retain advanced review')


with TemporaryDirectory() as directory:
    root = Path(directory)
    project = root / "project.cproj"
    names = ("Recipe", "Fiber", "Tile", "Panel")
    project.write_text('project Demo version "1.0.0" {\n' + "".join(
        f'element {name} object "{name}.celem";\n' for name in names) + "}\n")
    for name in names[1:]:
        (root / f"{name}.celem").write_text(f"object Demo::{name} {{}}")

    def recipe(ingredients, output="Demo::Panel", count=4):
        return (f'object Demo::Recipe {{ value concept = "recipe"; value ingredients = {json.dumps(ingredients)}; '
                f'value output = "{output}"; value outputCount = {count}; }}')

    original = recipe('{"Demo::Fiber":2,"Demo::Tile":3}')
    (root / "Recipe.celem").write_text(original)
    label = dict(project=str(project), path="Recipe.celem")
    staged = recipe('{"Demo::Fiber":5,"Demo::Tile":3}', count=6)
    valid = summary("object", original, staged, **label)
    assert valid["recipeQuantities"] == [
        {"role": "ingredient", "id": "Demo::Fiber", "before": 2, "after": 5},
        {"role": "result", "id": "Demo::Panel", "before": 4, "after": 6},
    ]
    ordinary = summary("object", original, staged)
    assert {key: value for key, value in valid.items() if key != "recipeQuantities"} == ordinary
    for rejected in (
        recipe('{"Demo::Fiber":5,"Demo::Tile":0}'),
        recipe('{"Demo::Fiber":5,"Demo::Fiber":3}'),
        recipe('{"Demo::Fiber":5,"Demo::Missing":3}'),
        recipe('{"Demo::Fiber":5}'),
        recipe('{"Demo::Fiber":5,"Demo::Tile":3}', output="Demo::Tile"),
    ):
        assert "recipeQuantities" not in summary("object", original, rejected, **label)
    assert "recipeQuantities" not in summary("object", original, staged, project=str(project), path="Tile.celem")

print("PASS recipe summaries contain only same-row owned numeric changes; ordinary review and rejection boundaries stay intact")
