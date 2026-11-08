"""Generated bounded geometry/alpha SVGs and independent integer pixel planes."""
import base64,random

def padded(raw,total):
 at=raw.rindex(b'</svg>');size=total-len(raw)-7;assert size>=0
 body=bytearray((base64.b64encode(random.Random(1666).randbytes(size))[:size]));position=1048575-(at+4)
 if 0<=position<=size-4:body[position:position+4]='🧪'.encode()
 result=raw[:at]+b'<!--'+body+b'-->'+raw[at:];assert len(result)==total;return result

def geometry():
 rows=['<svg xmlns="http://www.w3.org/2000/svg" id="generated-grid" width="400" height="200">'];pixels=bytearray(400*200*4)
 def number(n):return str(n)+'.'+'0'*380
 for y in range(20):
  for x in range(40):
   color=((x*29+y*11)%256,(x*13+y*31)%256,(x*47+y*7)%256);rows.append('<rect x="'+number(x*10)+'" y="'+number(y*10)+'" width="'+number(10)+'" height="'+number(10)+'" fill="#'+bytes(color).hex()+'"/>')
   for py in range(y*10,y*10+10):
    for px in range(x*10,x*10+10):i=(py*400+px)*4;pixels[i:i+4]=bytes((*color,255))
 rows.append('</svg>');return ''.join(rows).encode(),bytes(pixels)

def alpha():
 from v666_resource_svg_fixture import alpha
 raw=alpha.replace(b'<svg ',b'<svg id="generated-alpha" ');pixels=bytearray()
 for y in range(33):
  for x in range(65):pixels.extend((0,0,0,0)if x<15 or x<30 and y>=24 else(240,10,20,128)if x<30 else(240,10,20,255)if y<24 else(10,180,30,255))
 return padded(raw,1048600),bytes(pixels)

def expected(raw):
 if b'id="generated-grid"'in raw:return 400,200,geometry()[1]
 if b'id="generated-alpha"'in raw:return 65,33,alpha()[1]
 raise AssertionError('unknown generated source')
