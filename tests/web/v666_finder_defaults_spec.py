"""Execute the original v666 search helper over its authored storage shape."""
import json,pathlib,subprocess,sys,zipfile
r=pathlib.Path(sys.argv[1]);
with zipfile.ZipFile(r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip')as z:
 app=z.read('Confectory-v666/dist/app.js').decode();blueprint=z.read('Confectory-v666/dist/blueprint.js').decode()
assert 'next.blueprint=structuredClone(graph)'in blueprint and'object.functionDefinition=next'in blueprint
start=app.index('function workspaceSearchText(');end=app.index('function workspaceObjectTypeLabel',start);helper=app[start:end]
script=helper+'''
const object={id:'OriginalIDMustNotIndex',owner:'OriginalOwnerMustNotIndex',Greeting:'기본인사😀',functionDefinition:{body:'OriginalBodyNeedle',blueprint:{nodes:[{id:'GraphNodeIDMustNotIndex',text:'DeepGraphTextNotOriginallySearched',definition:{body:'DeeperCodeNotOriginallySearched'}}]}}};
const text=workspaceSearchText(object);if(!text.includes('기본인사😀')||!text.includes('OriginalBodyNeedle')||['DeepGraphTextNotOriginallySearched','DeeperCodeNotOriginallySearched','OriginalIDMustNotIndex','OriginalOwnerMustNotIndex'].some(s=>text.includes(s)))throw Error('authored search depth/ownership shape differs');
console.log('PASS original saved Blueprint node text lies beyond depth 4; owned property Unicode and direct function body are searched. Deep graph/code traversal is not a new mandatory remainder.');
'''
subprocess.run(['node','--input-type=module','-'],input=script,text=True,check=True)
