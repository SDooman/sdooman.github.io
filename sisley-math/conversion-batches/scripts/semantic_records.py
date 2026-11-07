"""Reviewed formula-only drawings and data tables. Blanks remain explicit."""
from pathlib import Path
import json,sys
from classify import GROUPS
ROOT=Path(__file__).resolve().parents[2]
def arr(rows,spec='l'):return r'\begin{array}{'+spec+'}'+r' \\ '.join(rows)+r'\end{array}'
def matrix(rows,split=None):
 spec=''.join(('|' if i==split else '')+'c' for i in range(len(rows[0])))
 return r'\left['+arr([' & '.join(row) for row in rows],spec)+r'\right]'
def system(rows):return r'\left\{'+arr(rows)+r'\right.'
def labelblank(letter):return r'\underset{\mathrm{'+letter+r'}}{\underline{\qquad}}'
def completing(coef,rhs):return arr([f'x^2+{coef}x+'+labelblank('B')+'='+rhs+'+'+labelblank('C'),'(x+'+labelblank('A')+')^2='+labelblank('D')])
def t(headers,rows,title=None):return {'kind':'table','title':title,'headers':headers,'rows':rows,'review':'needs_review','blank_meaning':'null means an intentional source blank, not zero'}
F={'41-58':{},'59-80':{},'81-100':{},'101-119':{}};T={b:{} for b in F}
f=F['41-58']
f.update({11:system([r'A_2=\frac12\cdot A_1',r'B_2=B_1']),12:system([r'A_3=A_2',r'B_3={}^{-}3\cdot A_2+B_2']),13:system([r'A_5=2\cdot B_4+A_4',r'B_5=B_4']),27:system([r'A_2=\frac14\cdot A_1',r'B_2=B_1']),28:system([r'A_3=A_2',r'B_3={}^{-}4\cdot A_2+B_2']),30:system([r'A_5=\frac{{}^{-}1}{2}\cdot B_4+A_4',r'B_5=B_4'])})
f[78]=matrix([['3','1','1'],['{}^{-}2','{}^{-}3','4']],2)+r'\quad'+arr(['A_1','B_1'])
f[92]=matrix([['14','21','{}^{-}17'],['20','6','8']],2)+r'\quad'+arr(['A_1','B_1'])
blankmatrix=matrix([[r'\phantom{00}',r'\phantom{00}',r'\phantom{00}']]*2,2)
for n,rows in {79:[r'A_2=\frac13\cdot A_1','B_2=B_1'],80:['A_3=A_2',r'B_3=2\cdot A_2+B_2'],81:['A_4=A_3',r'B_4=\frac{{}^{-}3}{7}\cdot B_3'],82:[r'A_5=\frac{{}^{-}1}{3}\cdot B_4+A_4','B_5=B_4'],93:[r'A_2=\frac1{14}\cdot A_1','B_2=B_1'],94:['A_3=A_2',r'B_3={}^{-}20\cdot A_2+B_2'],95:['A_4=A_3',r'B_4=\frac{{}^{-}1}{24}\cdot B_3'],96:[r'A_5=\frac{{}^{-}3}{2}\cdot B_4+A_4','B_5=B_4']}.items():f[n]=blankmatrix+r'\quad'+arr(rows)
f[211]=matrix([['0','1'],['1','0']])+r'\cdot'+matrix([[r'\frac{\sqrt3}{2}'],[r'\frac12']])+'='+matrix([[r'\frac12'],[r'\frac{\sqrt3}{2}']])+r'=\left(\frac12,\frac{\sqrt3}{2}\right)'
T['41-58'][109]=t(['year in which Olympic record was set','record in seconds'],[['1948','109.2'],['1956','107.7'],['1960','106.3'],['1964','105.1'],['1976','103.5'],['1984','103.0']],'800 meter run for men')
T['41-58'][110]=t(['year in which world record was set','record in seconds'],[['1953','127.3'],['1960','124.1'],['1964','121.5'],['1968','120.5'],['1971','118.3'],['1983','113.28']],'800 meter run for women')
for ids,rows in [([260,276],[['A','2','1'],['B','2','1'],['C','1','2'],['D','1','2']]),([278,284],[['A','3','1'],['B','3','1'],['C','2','2'],['D','2','2'],['E','0','4']]),([300,313],[['A','4','1'],['B','4','1'],['C','3','2'],['D','2','3'],['E','2','3'],['F','0','5']])]:
 for n in ids:T['41-58'][n]=t(['Team','Won','Lost'],rows)
T['41-58'][297]=t(['closeness index','cancer deaths'],[['1.3','114'],['1.6','138'],['2.5','147'],['2.6','130'],['3.4','130'],['3.8','162'],['6.4','178'],['8.3','210'],['11.6','208']])
f=F['59-80'];f[150]=system([r'5\cdot x+8\cdot y\geq80\quad A',r'10\cdot x+4\cdot y\geq100\quad B'])
f[248]=arr([r'(3\cdot x+5)(4\cdot x+{}^{-}3)=3\cdot x(4\cdot x+{}^{-}3)+5\cdot\underline{\qquad}=',r'3\cdot x\cdot\underline{\quad}+3\cdot x\cdot{}^{-}3+5\cdot4\cdot x+5\cdot\underline{\quad}=',r'12\cdot\underline{\quad}+\underline{\quad}\cdot x+20\cdot\underline{\quad}+\underline{\quad}=',r'\underline{\quad}\cdot x^2+(\underline{\quad}+\underline{\quad})\cdot x+\underline{\quad}=',r'\underline{\qquad}+\underline{\qquad}+\underline{\qquad}'])
operation=[list(a) for a in ['afaegbdc','babcdefg','cecdagbf','dgdaefcb','ebegfcad','fdfbcage','gcgfbdea']]
assert all(len(r)==8 for r in operation)
for n in [4,17,18,24,29,54]:T['59-80'][n]=t(['$*$','a','b','c','d','e','f','g'],operation)
T['59-80'][42]=t(['element','$*$-inverse of that element'],[[x,None] for x in 'abcdefg'])
f=F['81-100']
for n,coef,rhs in [(147,'6','8'),(149,'{}^{-}10','{}^{-}11'),(160,'12','{}^{-}11'),(161,'7','{}^{-}13'),(162,r'\sqrt5','{}^{-}1'),(203,r'\sqrt{11}',r'\frac54'),(204,r'\frac ba\cdot ',r'\frac{{}^{-}c}{a}')]:f[n]=completing(coef,rhs)
f[214]=arr([r'x^2+\frac ba\cdot x+\underset{B}{\frac{b^2}{4\cdot a^2}}=\frac{{}^{-}c}{a}+\underset{C}{\frac{b^2}{4\cdot a^2}}',r'\left(x+\underset{A}{\frac12\cdot\frac ba}\right)^2=\underset{D}{\frac{{}^{-}4\cdot a\cdot c+b^2}{4\cdot a^2}}'])
for n,rows in {256:[['5','3','1','0'],['4','3','0','1']],258:[['1',r'\frac35',r'\frac15','0'],['4','3','0','1']],260:[['1',r'\frac35',r'\frac15','0'],['0',r'\frac35',r'\frac{{}^{-}4}{5}','1']],262:[['1',r'\frac35',r'\frac15','0'],['0','1',r'\frac{{}^{-}4}{3}',r'\frac53']],264:[['1','0','1','{}^{-}1'],['0','1',r'\frac{{}^{-}4}{3}',r'\frac53']]}.items():f[n]=matrix(rows,2)
for n,k,equals in [(257,1,False),(259,2,True),(261,3,True),(263,4,True),(265,5,True),(293,2,True),(296,4,True),(298,5,True)]:f[n]=arr([f'A_{k}'+('=' if equals else ''),f'B_{k}'+('=' if equals else '')])
large={321:[['4','{}^{-}2','1','1','0','0'],['1','1','1','0','1','0'],['9','3','1','0','0','1']],322:[['1',r'\frac{{}^{-}1}{2}',r'\frac14',r'\frac14','0','0'],['1','1','1','0','1','0'],['9','3','1','0','0','1']],323:[['1',r'\frac{{}^{-}1}{2}',r'\frac14',r'\frac14','0','0'],['0',r'\frac32',r'\frac34',r'\frac{{}^{-}1}{4}','1','0'],['0',r'\frac{15}{2}',r'\frac{{}^{-}5}{4}',r'\frac{{}^{-}9}{4}','0','1']],326:[['1','0',r'\frac12',r'\frac16',r'\frac13','0'],['0','1',r'\frac12',r'\frac{{}^{-}1}{6}',r'\frac23','0'],['0','0','{}^{-}5','{}^{-}1','{}^{-}5','1']],328:[['1','0',r'\frac12',r'\frac16',r'\frac13','0'],['0','1',r'\frac12',r'\frac{{}^{-}1}{6}',r'\frac23','0'],['0','0','1',r'\frac15','1',r'\frac{{}^{-}1}{5}']],329:[['1','0','0',r'\frac1{15}',r'\frac{{}^{-}1}{6}',r'\frac1{10}'],['0','1','0',r'\frac{{}^{-}4}{15}',r'\frac16',r'\frac1{10}'],['0','0','1',r'\frac15','1',r'\frac{{}^{-}1}{5}']]}
for n,rows in large.items():
 k={321:1,322:2,323:3,328:6,329:7}.get(n);f[n]=matrix(rows,3)+(r'\quad'+arr([f'{x}_{k}'+('=' if k!=1 else '') for x in 'ABC']) if k else '')
for n,k in [(325,4),(327,5)]:f[n]=arr([f'{x}_{k}=' for x in 'ABC'])
f[386]=arr([r'y=2\cdot x^2+10\cdot x+{}^{-}3',r'y=2\cdot(x^2+\underline{\quad}\cdot x)+{}^{-}3',r'y=2\cdot(x^2+5\cdot x+\frac{25}{4})+{}^{-}3+\underline{\quad}',r'y=2\cdot(x+\underline{\quad})^2+\underline{\quad}'])
T['81-100'][371]=t(['','pre-image','image'],[[x,None,None] for x in ['perimeter','surface area','volume']])
T['81-100'][388]=t(['magnitude of size transformation','perimeter','surface area','volume'],[[str(i),None,None,None] for i in range(1,5)])
T['81-100'][397]=t(['magnitude of size transformation','perimeter','surface area','volume'],[['1','12','6','1'],['2','24','24','8'],['3','36','54','27'],['4','48','96','64']])
f=F['101-119']
for n in [23,37]:f[n]=system([r'\frac{{}^{-}1}{3}\cdot x+\frac12\cdot y=0',r'\frac13\cdot x+\frac{{}^{-}1}{2}\cdot y=0',r'x+y=720'])
f[39]=matrix([[r'\frac{{}^{-}1}{3}',r'\frac12'],[r'\frac13',r'\frac{{}^{-}1}{2}'],['1','1']])
f[72]=system([r'\frac13\cdot x+\frac12\cdot y=1\cdot x',r'\frac23\cdot x+\frac12\cdot y=1\cdot y','x+y=350'])
f[193]=system([r'25\cdot a+{}^{-}5\cdot b+1\cdot c=11',r'9\cdot a+3\cdot b+1\cdot c={}^{-}17',r'49\cdot a+7\cdot b+1\cdot c=22'])
for n,values in [(271,['4.2','3.45','2.85','2.32','1.5','0.85']),(278,['1.95','3.17','4.31','5.22','6.4','7.64'])]:T['101-119'][n]=t(['time in seconds','distance in meters'],[[str(i+1),v] for i,v in enumerate(values)])

def main():
 batch=sys.argv[1];book=ROOT/f'gat-{batch}';check=ROOT/f'conversion-batches/checkpoints/{batch}';native=json.loads((book/'native-equations.json').read_text());assets=json.loads((check/'assets.json').read_text());byid={a['id']:a for a in assets}
 formulas=json.loads((book/'formula-transcriptions.json').read_text());mapping={f['id']:f for f in formulas['assets']};semantic={}
 for num in GROUPS[batch]['formula'].split():
  n=int(num);ident='image'+num;row=byid[ident];records=row['native_equations']
  value=F[batch].get(n);method='source-inspected-transcription'
  if value is None:
   assert len(records)==1,(batch,ident,records)
   value=native[records[0]['id']]['latex'];method='native-equation-tree'
  mapping[ident]={'id':ident,'latex':value,'method':method,'review':'needs_review','source_asset':f'assets/source-png/{ident}.png','notes':[]}
 for n,table in T[batch].items():semantic['image'+str(n)]=table
 for row in assets:
  if row['id'] in mapping:continue
  records=[native[x['id']] for x in row['native_equations'] if x['id'] in native]
  if records:semantic[row['id']]={'kind':'embedded-equations','expressions':records,'note':'Equations recovered from native records embedded in a larger drawing. Record order does not establish placement or mathematical constraints.'}
 for ident,data in semantic.items():
  data['source_sha256']=byid[ident]['sha256'];(book/'assets/data'/f'{ident}.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 formulas['assets']=sorted(mapping.values(),key=lambda x:int(x['id'][5:]));(book/'formula-transcriptions.json').write_text(json.dumps(formulas,ensure_ascii=False,indent=2)+'\n');(book/'semantic-records.json').write_text(json.dumps(semantic,ensure_ascii=False,indent=2)+'\n')
 print(batch,'formulas',len(mapping),'tables',len(T[batch]),'other semantic records',len(semantic)-len(T[batch]))
if __name__=='__main__':main()
