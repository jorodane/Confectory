"""Generated uncompressed Windows BMPs, no user files."""
import struct

def bmp(depth=24,top=False,zero=False):
 w,h=65,33;stride=(w*depth+31)//32*4;raw=bytearray()
 for y in(range(h)if top else range(h-1,-1,-1)):
  color=(240,10,20)if y<16 else(10,180,30);r,g,b=color;row=bytearray()
  for x in range(w):
   row.extend((b,g,r))
   if depth==32:row.append(0 if x<22 else 127 if x<44 else 255)
  raw.extend(row);raw.extend(bytes(stride-len(row)))
 return struct.pack('<2sIHHI',b'BM',54+len(raw),0,0,54)+struct.pack('<IiiHHIIiiII',40,w,-h if top else h,1,depth,0,0 if zero else len(raw),2835,2835,0,0)+raw
bottom24=bmp();top24=bmp(top=True);bottom32=bmp(32);top32=bmp(32,True,True)
def changed(source,offset,value,fmt='<I'):
 raw=bytearray(source);struct.pack_into(fmt,raw,offset,value);return bytes(raw)
truncated=bottom24[:-1];palette=changed(bottom24,28,8,'<H');compressed=changed(bottom32,30,3);profile=changed(bottom24,14,124);oversized=changed(bottom24,18,16385,'<i')
