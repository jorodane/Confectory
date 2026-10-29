"""Compare the shared presentation policy with the user's pinned v666 functions."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,zipfile

repo=Path(sys.argv[1]).resolve()
archive=repo/'reference/site-ui/Confectory-Editor-Prototype-v666.zip'
assert hashlib.sha256(archive.read_bytes()).hexdigest()=='7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23'
with zipfile.ZipFile(archive) as z:
    source=z.read('Confectory-v666/dist/blueprint.js').decode()
names=('clampCanvasZoom','canvasZoomPercent','createSteppedZoomWheel')
functions=[]
for name in names:
    start=re.search(r'^function '+name+r'\(',source,re.M)
    end=re.search(r'^function \w+\(',source[start.end():],re.M)
    functions.append(source[start.start():start.end()+end.start()])
script='''import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const actual=await import(pathToFileURL(process.argv[2]+'/examples/editor-home/ui/canvas-zoom.js'));
'''+ '\n'.join(functions)+'''
for(const value of [-1e9,0,.03125,.04,.5,1,2.75,3,3.25,4,4.75,5,5.01,1e9]){
 assert.equal(actual.clampCanvasZoom(value),clampCanvasZoom(value));
 assert.equal(actual.canvasZoomPercent(actual.clampCanvasZoom(value)),canvasZoomPercent(clampCanvasZoom(value)));
}
assert.equal(actual.clampCanvasZoom(NaN),1);assert.equal(actual.clampCanvasZoom(Infinity),1);
const a=actual.createSteppedZoomWheel(),b=createSteppedZoomWheel();let x=1,y=1;
for(const event of [...Array(40)].map(()=>({deltaY:-100,deltaMode:0})).concat(
 [...Array(70)].map(()=>({deltaY:100,deltaMode:0})),
 [{deltaY:-1,deltaMode:1},{deltaY:-2,deltaMode:1},{deltaY:1,deltaMode:2},{deltaY:0,deltaMode:0}])){
 x=a(x,event);y=b(y,event);assert.equal(x,y);
}
a.reset();b.reset();assert.equal(a(4.75,{deltaY:-100,deltaMode:0}),5);assert.equal(b(4.75,{deltaY:-100,deltaMode:0}),5);
assert.deepEqual([...actual.CANVAS_ZOOM_PRESETS],[3.125,6.25,12.5,25,50,75,100,150,200,300,400,500]);
console.log('PASS v666 finite bounds, pointer-wheel steps in both directions, delta modes, reset, invalid restored values and exact original presets');
'''
result=subprocess.run(['node','--input-type=module','-',str(repo)],input=script,text=True,capture_output=True)
if result.stderr:print(result.stderr,file=sys.stderr,end='')
result.check_returncode()
print(result.stdout,end='')
