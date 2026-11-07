from pypdf import PdfReader
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import json
m=json.load(open('.conversion-work/atlas.json'));p=PdfReader('.conversion-work/atlas.pdf');pgmap={pg.indirect_reference.idnum:i for i,pg in enumerate(p.pages)};figs=[]
def walk(o):
 if isinstance(o,list):
  for x in o:walk(x)
  return
 o=o.get_object() if hasattr(o,'get_object') else o
 if not isinstance(o,dict):return
 if o.get('/S')=='/Figure':figs.append(o)
 if '/K' in o:walk(o['/K'])
walk(p.trailer['/Root']['/StructTreeRoot']['/K']);assert len(figs)==len(m);meta={}
for i,(f,info) in enumerate(zip(figs,m)):
 pi=pgmap[f.raw_get('/Pg').idnum];box=f['/A']['/BBox'];l,b,r,t=map(float,box)
 im=Image.open(f'.conversion-work/atlas-pages/page-{pi+1:03}.png').convert('RGB');im=im.crop((max(0,int(l*3)-3),max(0,int((792-t)*3)-3),int(r*3)+3,int((792-b)*3)+3))
 name=Path(info['file']).stem;out=Path('gat-1-20/assets',name+'.png');im.save(out)
 bbox=ImageOps.invert(im).getbbox();meta[Path(info['file']).name]={**info,'output':str(out),'blank':bbox is None,'ink_bounds':bbox}
 assert bbox is not None,name
Path('.conversion-work/diagrams.json').write_text(json.dumps(meta,indent=2))
for batch in range((len(m)+11)//12):
 canvas=Image.new('RGB',(1500,1600),'#e6e6e6');draw=ImageDraw.Draw(canvas)
 for j,info in enumerate(m[batch*12:batch*12+12]):
  name=Path(info['file']).stem;im=Image.open(f'gat-1-20/assets/{name}.png');im.thumbnail((480,360));x=(j%3)*500;y=(j//3)*400;draw.text((x+10,y+10),name,fill='black');canvas.paste(im,(x+10,y+35))
 canvas.save(f'.conversion-work/diagrams-contact-{batch+1:02}.jpg')
files=sorted(Path('.conversion-work').glob('*-equation.png'),key=lambda p:int(p.name.split('-')[0][5:]))
for k in range((len(files)+35)//36):
 canvas=Image.new('RGB',(1500,1440),'white');d=ImageDraw.Draw(canvas)
 for j,pp in enumerate(files[k*36:k*36+36]):
  im=Image.open(pp).convert('RGBA');im.thumbnail((480,90));x=j%3*500;y=j//3*120;d.text((x+10,y+2),pp.stem,fill='black');canvas.paste(im,(x+10,y+24),im)
 canvas.save(f'.conversion-work/equations-contact-{k+1:02}.jpg')
print('Collected and checked 124 diagrams; created contact sheets')
