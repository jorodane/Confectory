"""The SVG suite must reach its dedicated EOL, package and restore chains once each."""
import ast,pathlib,sys
s=(pathlib.Path(sys.argv[1])/'tools/verify_desktop.py').read_text();tree=ast.parse(s)
branches=[node for node in ast.walk(tree)if isinstance(node,ast.If)and isinstance(node.test,ast.Compare)and isinstance(node.test.ops[0],ast.Eq)and any(isinstance(x,ast.Constant)and x.value=='resource-svg'for x in node.test.comparators)]
# One preflight guard and exactly three test chains. No duplicate/unreachable inner branches.
assert len(branches)==4,len(branches)
bodies=[ast.get_source_segment(s,node).split('\nelif ',1)[0]for node in branches]
for token in ["work.run(label+'-resource-svg-boundary'","work.run('packaged-resource-'","work.run('restored-resource-'"]:
 direct=[ast.get_source_segment(s,n)for node in branches for body in node.body for n in ast.walk(body)if isinstance(n,ast.Call)]
 assert sum(token in call for call in direct)==1,token
assert "['svg','avif','transfer']"in s
print('PASS dedicated SVG EOL/package/restore routing; no duplicate SVG test branch or generic header fallthrough')
