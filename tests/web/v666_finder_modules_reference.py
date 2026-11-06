"""Execute the authored shallow helper against its direct module method shape."""
import hashlib,json,pathlib,subprocess,sys,zipfile
r=pathlib.Path(sys.argv[1]).resolve();path=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(path.read_bytes()).hexdigest()=='7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23'
with zipfile.ZipFile(path)as z:
 source=z.read('Confectory-v666/dist/app.js').decode();start=source.index('function workspaceSearchText(value){');end=source.index('\nfunction workspaceObjectTypeLabel',start);helper=source[start:end]
script=helper+'''\nconst own={name:'같은 인터페이스',group:'module',kind:'Module',methods:[{id:'PrivateStableIdMustNotSearch',name:'DirectModuleActionNeedle'}],linkedModules:['BaseRules']};const text=workspaceSearchText(own);if(!text.includes('DirectModuleActionNeedle')||text.includes('PrivateStableIdMustNotSearch')||text.includes('ParentSecretMustNotJoin'))throw Error('authored module search shape differs');console.log('PASS authored v666 helper searches direct methods[].name; opaque ID and unjoined parent contents excluded');'''
subprocess.run(['node','-e',script],check=True)
