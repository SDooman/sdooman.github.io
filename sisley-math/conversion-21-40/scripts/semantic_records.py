"""Explicitly transcribed tables and annotations. Blank exercises stay blank.

These records are independent of preserved vector layout; editing table values
does update Markdown/HTML, while diagram semantics do not yet relayout artwork.
"""
from pathlib import Path
import json,copy
ROOT=Path(__file__).resolve().parents[2]
N=r'{}^{-}'
def main():
    result={}
    def table(n,headers,rows,title=None):
        result[f'image{n}']={'kind':'table','headers':headers,'rows':rows,'title':title,'blank_meaning':'Unfilled source exercise cell; no answer inferred.'}
    def math(n,*values):result[f'image{n}']={'kind':'annotated-math','expressions':[{'id':f'expression-{i+1}','latex':v} for i,v in enumerate(values)]}
    table(200,['The diameter of a circle','The circumference of the same circle'],[[1,r'$\pi$'],[3,None],[None,r'$\sqrt{14}\cdot\pi$'],['4.5',None],[None,10]])
    years=[1948,1952,1956,1960,1964,1968,1972,1976,1980,1984,1988,1992]
    women=['24.4','23.7','23.4','24.0','23.0','22.5','22.4','22.37','22.03','21.81','21.34','21.81']
    table(204,['Year','Winning time'],list(map(list,zip(years,women))))
    table(205,['Size transformation magnitude',r'Image of $(1,\sqrt{2})$'],[[f'${N}3$',None],[f'${N}1$',None],[2,None],[4,None],[7,None]])
    table(224,['Size transformation magnitude',r'Image of $(1,\sqrt{0.9})$'],[[f'${N}3$',fr'$({N}3,{N}3\cdot\sqrt{{0.9}})$'],[f'${N}1$',fr'$({N}1,{N}1\cdot\sqrt{{0.9}})$'],[2,r'$(2,2\cdot\sqrt{0.9})$'],[4,r'$(4,4\cdot\sqrt{0.9})$'],[7,r'$(7,7\cdot\sqrt{0.9})$']])
    table(231,['The measure of a length in meters','The measure of the same length in inches'],[[1,None],[2,'78.74'],[3,'118.11'],[5,'196.85'],[None,'393.70']])
    table(260,['The length of an object in inches','The length of the same object in centimeters'],[[0,None],[1,None],[2,None],[10,None]])
    world=[[1953,'127.3'],[1960,'124.1'],[1964,'121.5'],[1968,'120.5'],[1971,'118.3'],[1983,'113.28']]
    for n in (397,429,465):table(n,['Year in which world record was set','Record in seconds'],copy.deepcopy(world),'800-meter run for women')
    for n in (431,449):table(n,['L1','L2'],[[1,7],[2,13],[6,26],[7,30],[10,35],[11,33]])
    table(464,['Year in which Olympic record was set','Record in seconds'],[[1948,'109.2'],[1956,'107.7'],[1960,'106.3'],[1964,'105.1'],[1976,'103.5'],[1984,'103.0']],'800-meter run for men')
    teams=['Braves','Dodgers','Cubs','Reds','Giants','Phillies'];wins53=[92,105,65,68,70,83];wins54=[89,92,64,74,97,75];wins55=[85,98,72,75,80,77]
    table(489,['Team','Wins in 1953','Wins in 1954'],list(map(list,zip(teams,wins53,wins54))),'Number of season wins for six National League teams')
    table(512,['Team','Wins in 1954','Wins in 1955'],list(map(list,zip(teams,wins54,wins55))),'Number of season wins for six National League teams')
    names=['Blankers-Koen, Netherlands','Jackson, Australia','Cuthbert, Australia','Rudolph, USA','McGuire, USA','Szewinska, Poland','Stecher, E. Germany','Eckert, E. Germany','Wockel, E. Germany','Brisco-Hooks, USA','Griffith-Joyner, USA','Torrence, USA']
    table(494,['Year','Name, nation','Time in seconds'],list(map(list,zip(years,names,women))),'200-meter run for women, Olympic gold medal times')
    names=['Patton, USA','Stanfield, USA','Morrow, USA','Berruti, Italy','Carr, USA','Smith, USA','Borzov, USSR','Quarrie, Jamaica','Mennea, Italy','Lewis, USA','DeLoach, USA','Marsh, USA']
    men=['21.1','20.7','20.6','20.5','20.3','19.83','20.00','20.23','20.19','19.80','19.75','20.01']
    table(522,['Year','Name, nation','Time in seconds'],list(map(list,zip(years,names,men))),'200-meter run for men, Olympic gold medal times')
    blank=r'\boxed{\phantom{00}}';x=r'\overset{x}{'+blank+'}';y=r'\overset{y}{'+blank+'}'
    for n in (122,124):math(n,x+r'+2\cdot '+y+'=10')
    math(123,r'\overset{x}{\boxed{3}}+2\cdot\overset{y}{\boxed{4}}=10\longrightarrow 3+2\cdot4=10')
    math(125,r'\overset{x}{\boxed{4}}+2\cdot\overset{y}{\boxed{3}}=10\longrightarrow 4+2\cdot3=10')
    math(126,x+r'+2\cdot '+y+'=10',r'x+2\cdot y=10')
    math(127,x+'+'+y+'=10','x+y=10')
    math(128,x+'+'+y+'=10')
    math(168,x+'+'+N+r'3\cdot '+y+'=10','x+'+N+r'3\cdot y=10')
    math(169,x+'+'+N+r'3\cdot '+y+'=10')
    math(193,r'(-2,3)\longrightarrow(0,0)',r'(5,1)\longrightarrow(7,-2)\longrightarrow\left(1,\frac{-2}{7}\right)')
    math(195,r'(-2,3)\longrightarrow(-7,2)\longrightarrow\left(1,\frac{-2}{7}\right)',r'(5,1)\longrightarrow(0,0)')
    math(199,r'3\cdot '+x+'+'+y+'='+N+'10')
    math(206,r'(2,8)\longrightarrow(0,0)',r'(11,'+N+r'5)\longrightarrow(9,'+N+r'13)\longrightarrow\left(1,\frac{'+N+r'13}{9}\right)')
    math(207,y+'='+N+r'1.4\cdot '+x,'y='+N+r'1.4\cdot x')
    math(209,y+'='+N+r'1.4\cdot('+x+'+3)','y='+N+r'1.4\cdot(x+3)')
    math(214,y+'='+N+r'1.4\cdot('+x+'+'+N+'3)','y='+N+r'1.4\cdot(x+'+N+'3)')
    math(216,'('+y+'+7)='+N+r'1.4\cdot '+x,'y+7='+N+r'1.4\cdot x')
    math(392,r'y=\frac13\cdot x',r'T(x,y)=(x+'+N+r'2,y+3)',r'(y+'+N+r'3)=\frac13\cdot(x+2)')
    math(394,r'y=3.4\cdot x',r'T(x,y)=(x+'+N+r'6,y+9)')
    math(395,'y='+N+r'2.1\cdot x','(y+'+N+'7)='+N+r'2.1\cdot(x+3)')
    math(401,'y='+N+r'2.13\cdot x',r'T(x,y)=(x+'+N+r'3,y+7)')
    math(402,r'y=0.64\cdot x',r'(y+5)=0.64\cdot(x+'+N+'11)')
    math(413,r'(-2,3)\longrightarrow(0,0)',r'(6,-2)\longrightarrow(8,-5)\longrightarrow\left(1,\frac{-5}{8}\right)',r'(-2,3)\longrightarrow(-8,5)\longrightarrow\left(1,\frac{-5}{8}\right)',r'(6,-2)\longrightarrow(0,0)')
    math(421,r'y=\frac{'+N+r'5}{8}\cdot x',r'T_1(x,y)=(x+'+N+r'2,y+3)',r'(y+'+N+r'3)=\frac{'+N+r'5}{8}\cdot(x+2)',r'T_2(x,y)=(x+6,y+'+N+r'2)',r'(y+2)=\frac{'+N+r'5}{8}\cdot(x+'+N+'6)')
    math(433,r'y=\frac{24}{9}\cdot(x+'+N+r'1.5)+10',r'T(x,y)=\left(x,y+\frac{14}{9}\right)')
    math(461,r'y=\frac{24}{9}\cdot(x+'+N+r'1.5)+10',r'T(x,y)=\left(x,y+\frac{14}{9}\right)',r'y+\frac{'+N+r'14}{9}=\frac{24}{9}\cdot(x+'+N+r'1.5)+10',r'y=\frac{24}{9}\cdot(x+'+N+r'1.5)+10+\frac{14}{9}')
    result['image3']={'kind':'annotated-matrix','row_labels':['D','LA','NY','SL','SE'],'column_labels':['D','LA','NY','SL','SE'],'entries':[[None]*5 for _ in range(5)],'notes':['Blank direct-flight matrix exercise. No entries have been supplied.']}
    math(8,r'\begin{bmatrix}0&1\\1&0\end{bmatrix}\cdot\begin{bmatrix}1&0\\0&'+N+r'1\end{bmatrix}\begin{bmatrix}0\\2\end{bmatrix}',r'(r_{y=x}\circ r_x)(0,2)')
    result['image8']['matrices']=[{'id':'matrix3','entries':[[0,1],[1,0]]},{'id':'matrix2','entries':[[1,0],[0,-1]]},{'id':'matrix1','entries':[[0],[2]]}]
    math(25,r'\begin{bmatrix}e&f\\g&h\end{bmatrix}\cdot\begin{bmatrix}a&b\\c&d\end{bmatrix}',r'T_2\circ T_1')
    result['image25']['matrices']=[{'id':'T2','entries':[['e','f'],['g','h']]},{'id':'T1','entries':[['a','b'],['c','d']]}]
    result['image462']={'kind':'screenshot-transcript','lines':['Med–Med','y=ax+b','a=2.666666667','b=7.555555556'],'notes':['Displayed rounded decimals, not substituted exact rational values.']}
    result['image453']={'kind':'screenshot-transcript','lines':['(6.5, 28)','P=(6.5, 70/3)'],'notes':['Printed coordinate annotations only. The calculator plot remains an image.']}
    result['image430']={'kind':'screenshot-transcript','lines':[],'source_data_asset':'image429','notes':['Scatterplot has no visible numeric axes. No data inferred from pixel positions.']}
    result['image450']={'kind':'screenshot-transcript','lines':[],'source_data_asset':'image449','notes':['Calculator plot and selected markers preserved. No display scale inferred.']}
    result['image2']={'kind':'directed-network','nodes':[
        {'id':'SE','label':'Seattle'},{'id':'NY','label':'New York'},{'id':'LA','label':'L.A.'},{'id':'SL','label':'St. Louis'},{'id':'D','label':'Dallas'}],
        'edges':[{'id':f'flight-{i+1:02}','from':a,'to':b} for i,(a,b) in enumerate([
            ('SE','NY'),('NY','SE'),('SE','LA'),('LA','SE'),('SE','SL'),('LA','SL'),('SL','LA'),
            ('SL','NY'),('NY','SL'),('NY','D'),('SL','D'),('LA','D'),('D','SE')])],
        'notes':['Thirteen visible directional arrows transcribed from the original. The separate flight-matrix exercise remains blank. Node/edge data are separate from the preserved vector layout.']}
    for key,value in result.items():value['source_asset_id']=key;value['review']='needs_review'
    (ROOT/'gat-21-40/semantic-records.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    out=ROOT/'gat-21-40/assets/data';out.mkdir(exist_ok=True)
    for key,value in result.items():(out/f'{key}.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    print('Structured tables and annotations:',len(result))
if __name__=='__main__':main()
