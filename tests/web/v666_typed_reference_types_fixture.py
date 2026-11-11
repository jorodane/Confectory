"""New nominal reference choices keep exact native type source proofs."""
import copy
import v666_function_types_fixture as x
f=x.f
def request(c=None):
 c=c or x.catalog();choices={row['id']:row for row in c['nativeTypes']};payload=choices[f.n+'Payload'];remote=choices['External.Fields::Leaf'];module=choices[f.n+'NativeRules'];kind=choices[f.n+'Mood'];q=payload['reference'];qr=remote['reference'];assert q['available']and qr['available']and q['kind']==qr['kind']=='reference'and q['profile']==qr['profile']=='information-reference-struct-v1';signature={'args':[{'name':'payload','type':q['clrType']},{'name':'snapshot','type':payload['clrType']},{'name':'services','type':module['clrType']+'[]'},{'name':'remote','type':qr['clrType']+'[]'},{'name':'choice','type':kind['clrType'],'mode':'out'}],'return':q['clrType']};fn=x.owner+'_Function_'+'d'*32
 row=dict(type='function-add',id=fn,name='정보 참조 계약',description='명시적 인스턴스 타입',signature=signature,nativeTypes={r['clrType']:copy.deepcopy(r['proof'])for r in [q,payload,module,qr,kind]})
 return dict(action='applySlots',id=x.owner,rows=[],basis=c['basis'],declaration=dict(id=x.owner,hash=f.state()['schema']['textHash'],changes=[row]))
x.request=request
