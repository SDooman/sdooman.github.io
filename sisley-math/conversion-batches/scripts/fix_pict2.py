from pathlib import Path
import sys
BOOK=Path(sys.argv[1]); CHECK=Path(sys.argv[2]); (CHECK/"fixed-pict").mkdir(exist_ok=True)
import struct,json
fixed={0:0,2:8,3:2,4:1,5:2,6:4,7:4,8:2,9:8,10:8,11:4,12:4,13:2,14:4,15:4,16:8,17:2,21:2,22:2,26:6,27:6,28:0,29:6,30:0,31:6,32:8,33:4,34:6,35:2,0xa0:2,0xc00:24,0xff:0}
for a in [0x30,0x40,0x50]:
 for b in range(5):fixed[a+b]=8;fixed[a+8+b]=0
for b in range(5):fixed[0x60+b]=12;fixed[0x68+b]=4;fixed[0x78+b]=0;fixed[0x88+b]=0
results={}
for p in (BOOK/'assets/originals').glob('*.pct'):
 b=p.read_bytes()
 if b[10:12]!=b'\x00\x11':continue
 pos=10;ops=[];fonts={0:'Chicago',1:'Geneva',2:'New York',3:'Geneva',4:'Monaco',20:'Times',21:'Helvetica',22:'Courier',23:'Symbol'}
 try:
  while pos<len(b):
   if pos%2:pos+=1
   start=pos;op=struct.unpack_from('>H',b,pos)[0];pos+=2
   if op in fixed:pos+=fixed[op]
   elif op in [1,0x70,0x71,0x72,0x73,0x74,0x80,0x81,0x82,0x83,0x84]:pos+=struct.unpack_from('>H',b,pos)[0]
   elif op in [0x2c,0x2d,0x2e,0x2f]:
    n=struct.unpack_from('>H',b,pos)[0]
    if op==0x2c:
     fid=struct.unpack_from('>H',b,pos+2)[0];sz=b[pos+4];fonts[fid]=b[pos+5:pos+5+sz].decode('mac_roman')
    pos+=2+n
   elif op==0xa1:pos+=4+struct.unpack_from('>H',b,pos+2)[0]
   elif op in [0x28,0x29,0x2a,0x2b]:
    pos+={0x28:4,0x29:1,0x2a:1,0x2b:2}[op];pos+=1+b[pos]
   elif op in (0x90,0x98):
    ops.append((op,b[start:]));pos=len(b);break
   elif op>=0x8100:pos+=4+struct.unpack_from('>I',b,pos)[0]
   elif 0x100<=op<=0x7fff:pos+=(op>>8)*2
   else:raise ValueError(f'unsupported {op:04x} at {start}')
   ops.append((op,b[start:pos]))
   if op==0xff:break
  new=b[:10];count=0
  for op,bb in ops:
   if op==3:
    fid=struct.unpack_from('>H',bb,2)[0]
    if fid in fonts:
     s=fonts[fid].encode('mac_roman');extra=struct.pack('>HHHB',0x2c,len(s)+3,fid,len(s))+s
     new+=extra+bytes(len(extra)%2);count+=1
   new+=bb+bytes(len(bb)%2)
  new=struct.pack('>H',len(new)%65536)+new[2:]
  (CHECK/'fixed-pict'/p.name).write_bytes(new);results[p.name]={'font_resets':count}
 except Exception as e:results[p.name]={'error':str(e)}
print(json.dumps(results,indent=2))
(CHECK/'pict2-fixes.json').write_text(json.dumps(results,indent=2))
