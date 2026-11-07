"""Make reproducible contact sheets for media classification and math QA."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,sys
ROOT=Path(__file__).resolve().parents[2];batch=sys.argv[1];book=ROOT/f'gat-{batch}';work=ROOT/f'.conversion-work/gat-{batch}';check=ROOT/f'conversion-batches/checkpoints/{batch}'
from mtef import walk
formulas=json.loads((book/'formula-transcriptions.json').read_text())['assets'];trees=json.loads((check/'mtef-trees.json').read_text())
from classify import GROUPS
additional={'image'+n for n in GROUPS[batch]['formula'].split()}
selected=[]
for i,f in enumerate(formulas):
 tree=trees.get(f['id']+'-1',[])
 special=any(n['type']==5 and any(n['row_partitions']+n['column_partitions']) or n['type']==3 and n['selector']==4 or n['type']==2 and (n.get('embellishments') or n['code'] in (197,202) or n['face'] in (4,5)) for n in walk(tree))
 if f['id'] in additional or f['method']!='native-equation-tree' or special or i%25==0:selected.append(f)
for k in range(0,len(selected),12):
 canvas=Image.new('RGB',(1600,1920),'#edf1f5');d=ImageDraw.Draw(canvas)
 for j,f in enumerate(selected[k:k+12]):
  x=j%2*800;y=j//2*320;d.text((x+10,y+8),f['id']+' | source above, LaTeX below',fill='black')
  for row,p in enumerate([book/'assets/source-png'/f'{f["id"]}.png',work/'math-qa'/f'{f["id"]}.png']):
   im=Image.open(p).convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);im=bg.convert('RGB');im.thumbnail((770,130));canvas.paste(im,(x+10,y+32+row*140))
 canvas.save(work/f'formula-review-{k//12+1:02}.jpg')
(check/'visual-qa-selection.json').write_text(json.dumps({'selected_formulas':[f['id'] for f in selected],'selection':'All additional formula pictures and manual transcriptions; native partitions, one-sided bars, Greek letters, raised-minus and degree codes and embellishments; every 25th other formula.'},indent=2)+'\n')
print(batch,len(selected),'formulas', (len(selected)+11)//12,'sheets')
