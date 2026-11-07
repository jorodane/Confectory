"""Generated static/animated WebP samples, no user files or external payloads."""
import io,struct
from PIL import Image

def encoded(mode,color,**kwargs):
 stream=io.BytesIO();Image.new(mode,(64,32),color).save(stream,format='WEBP',**kwargs);return stream.getvalue()
def chunk(name,data):return name.encode()+struct.pack('<I',len(data))+data+(b'\0'if len(data)&1 else b'')
def riff(*parts):
 data=b'WEBP'+b''.join(parts);return b'RIFF'+struct.pack('<I',len(data))+data
lossless=encoded('RGB',(240,10,20),lossless=True)
lossy=encoded('RGB',(10,180,30),quality=95)
alpha_lossy=encoded('RGBA',(20,50,230,128),quality=95)
alpha_lossless=encoded('RGBA',(240,10,20,128),lossless=True)
# Legal unknown RIFF chunks are ignored; the URL is inert text, never fetched.
metadata=riff(lossless[12:],chunk('JUNK',b'https://must-not-load.invalid/image'))
stream=io.BytesIO();Image.new('RGB',(64,32),(240,10,20)).save(stream,format='WEBP',save_all=True,append_images=[Image.new('RGB',(64,32),(10,180,30))],duration=[100,100],loop=0,lossless=True);animated=stream.getvalue()
frame=bytes([0x30,0,0,0x9d,1,0x2a])+struct.pack('<HH',64,32)+b'\0'
broken=riff(chunk('VP8 ',frame))
canvas=bytes([0,0,0,0])+int(16384).to_bytes(3,'little')+int(0).to_bytes(3,'little');oversized=riff(chunk('VP8X',canvas),chunk('VP8 ',frame))
truncated=lossless[:-1]
