from pathlib import Path
import json, re, shutil

ROOT = Path('gat-1-20')
BACKUP = Path('.conversion-work/pre-latex')
BACKUP.mkdir(exist_ok=True)
for name in ['GAT-1-20.md', 'GAT-1-20.html', 'manifest.json', 'conversion-report.md', 'README.md']:
    if not (BACKUP / name).exists():
        shutil.copy2(ROOT / name, BACKUP / name)

# Manually transcribed against all 17 image contact sheets and the extracted
# text drawing positions. A tilde here means the source's raised negative sign.
raw = r'''
4|\ell
7|x\text{-axis}
8|y\text{-axis}
10|1\cdot x+0\cdot y=~2
11|0\cdot x+1\cdot y=~2
12|x+y=~4
13|1\cdot x+2=0\cdot y
14|x=~2
16|5\cdot x+~7=3
17|5\cdot x+~6=~9
18|\sqrt{3}\cdot x+2=8
21|r_x
22|r_x(x,y)=(~x,y)
23|r_x(x,y)=(x,~y)
24|(3,~\sqrt{23})
25|(3,\sqrt{23})
26|(~5,0)
27|(13.2,0)
28|r_x(~4,~5)
29|r_x(5,~2)
30|r_x(0,~3)
31|r_x(a,b)
32|r_x(~a,~b)
33|x
34|y
35|1\cdot~2+0\cdot~1=~2
36|1\cdot x+0\cdot y=~2
37|~\sqrt{7}
38|1\cdot x+0\cdot y=4
39|0\cdot x+1\cdot y=3
40|x+y=7
41|0\cdot x+~4=~1\cdot y
42|y=4
43|y=x
44|\surd(3)
45|\surd
46|x^2
47|\sqrt{10}
48|\sqrt{3+\sqrt{47}}
49|11\cdot x+4=9
50|11\cdot x+4=\sqrt{11}
51|5\cdot x+6\cdot x+\sqrt{3}=5
52|r_x(x,y)=(x,~y)
53|r_x(~x,~y)=(~x,y)
54|r_y(x,y)=(~x,y)
55|r_y(x,y)=(x,~y)
56|r_y(y,x)=(~y,x)
57|r_y(~x,y)=(x,y)
58|\sqrt{(~13.2)^2}
59|\sqrt{\sqrt{26}+5}
60|r_x(~3,~4)
61|r_y(~3,~4)
62|r_x(r_y(~3,~4))
63|r_x(~a,b)
64|r_y(~a,b)
65|r_x(r_y(~a,b))
66|2\cdot x+5\cdot x=23
67|2\cdot x+x=23
68|2\cdot x+\sqrt{7}\cdot x=23
69|2\cdot(c+d)
71|15^2+8^2=17^2
72|a^2+b^2=c^2
74|\sqrt{58}
75|r_y(~7,~4)
77|y=~x
78|(~1.732)^2
79|~1.732^2
80|\sqrt{7+\sqrt{4.1}}
81|\sqrt{7}+\sqrt{4.1}
82|11x+~21=12
83|11\cdot x+~\sqrt{21}=12
84|\sqrt{11}\cdot x+~21=12
85|r_x(~5,2)
86|r_y(5,~2)
87|r_x(r_y(5,~2))
88|r_x(r_x(5,~2))
89|r_y(r_x(~a,b))
91|c\cdot d+c\cdot d
93|r_{x=~3}(A)=r_{x=~3}(~5,0)=
94|r_{x=2}
95|=r_{x=2}(~1,0)=A''=(5,0)
96|r_{x=2}(\circ r_{x=~3}(A))=r_{x=2}(r_{x=~3}(~5,0)=r_{x=2}(~1,0)=(5,0)=A''
97|r_{x=2}
98|r_{x=~3}
99|r_{x=2}\circ r_{x=~3}
100|\circ
101|r_{x=~3}\circ r_{x=2}
102|x=~3
103|x=2
104|r_{x=~3}\circ(r_{x=2}(A))=r_{x=~3}(9,0)=(~15.0)=A''
105|r_{x=2}\circ r_{x=~3}
106|(r_{x=2}\circ r_{x=~3})(x,y)=(x+10,y)
107|(r_{x=~3}\circ r_{x=2})(x,y)=(x+~10,y)
108|r_{x=~1}\circ r_{x=3}
111|r_{\ell}(A)=
112|r_m
113|m
114|\sqrt{3.6^2+5.7^2}
115|\sqrt{~3.6^2+5.7^2}
116|\sqrt{(~3.6)^2+5.7^2}
118|r_{\ell}
119|r_m
120|(x,y)=
125|r_{\ell}\circ r_m
126|r_{\ell}(A)=A'
129|(x,y)=(x+a,y+b)
130|\sqrt{3^2+4^2}=5
135|r_m\circ r_{\ell}
136|r_{\ell}(A)=
148|\left(\frac{~1}{2},\frac{1}{2}\right)
149|7\cdot x+11=6\cdot x+13
150|12\cdot x+~13=13\cdot x+~5
151|\sqrt{3}\cdot x+17=2\cdot x+~8
154|\left(\frac{1}{\sqrt{2}},\frac{1}{\sqrt{2}}\right)
157|11\cdot x+~17=9\cdot x+~9
158|3\cdot x+23=\frac{1}{3}\cdot x+~7
159|4\cdot x+23=\pi\cdot x+~7
164|\sqrt{6^2+6^2}=\sqrt{72}
165|\sqrt{72}
174|\frac{1}{7}\cdot x+11=~2\cdot x+~9
175|\sqrt{3}\cdot x+5=2x+8
176|x+~4=\sqrt{11}\cdot x
179|r_{y=~x}\circ r_y
180|r_x\circ r_{y=~x}
181|r_{y=~x}\circ r_y
182|r_x\circ r_{y=~x}
192|4\cdot x+11=3\cdot x+~8
193|4\cdot a+11=3\cdot a+~8
194|\sqrt{7}\cdot y+11=\pi\cdot y+~8
196|r_{y=~x}\circ r_y
197|r_y\circ r_{y=~x}
200|5\cdot x+~21=3\cdot x+11
201|5\cdot x+~21=\sqrt{3}\cdot x+11
202|5\cdot a+~\sqrt{7}=3\cdot a+11
208|r_{y=~x}\circ r_x
209|r_x\circ r_{y=~x}
215|y=x\text{ line}
224|k
228|\cdot
230|a_{41}
234|a_{11}\cdot b_{11}+a_{12}\cdot b_{21}
235|a_{21}\cdot b_{12}+a_{22}\cdot b_{22}
242|j
243|s_{21}
247|\times
254|6\cdot0+6\cdot6+8\cdot10
256|A\cdot B=C
259|a_{21}\cdot b_{11}+a_{22}\cdot b_{21}+a_{23}\cdot b_{31}
269|a^2+b^2=c^2
278|n_{21}\cdot n_{13}+n_{22}\cdot n_{23}+n_{23}\cdot n_{33}
280|5\times5
286|2\times1
289|2\times2
298|\times
305|r_{y=x}\circ r_x
306|r_y\circ r_{y=x}
324|n_{31}\cdot n_{12}+n_{32}\cdot n_{22}+n_{33}\cdot n_{32}+n_{34}\cdot n_{42}
328|r_x
330|B\cdot A
335|r_{y=x}(x,y)=
'''
formula = {int(line.split('|',1)[0]): line.split('|',1)[1] for line in raw.strip().splitlines()}

def mat(rows):
    return r'\begin{bmatrix}' + r' \\ '.join(' & '.join(str(v) for v in row) for row in rows) + r'\end{bmatrix}'

def m(rows):
    return mat([row.split() for row in rows.split(';')])

M = {
229: r'A='+m(r'x 4;~3 y;7 0;2\cdot{x} ~1'),
231: m('5 ~2;3 7;~1 ~3'),
232: m('2 ~5;3 4'),
233: m('1 3;~2 0'),
245: m('1 0;0 ~1'),
246: m('5;~2'),
258: m('3;5;8'),
260: m('2 0;0 2')+r'\cdot'+m('1 0 1;0 1 1'),
263: mat([['0','1','2','1','0'],['1','0','0',r'\phantom{0}',r'\phantom{0}'],['1','0',r'\phantom{0}',r'\phantom{0}',r'\phantom{0}'],[r'\phantom{0}']*5,[r'\phantom{0}']*5]),
264: m('1 0;0 ~1')+r'\cdot'+m('1;1'),
265: m('0 1;1 0')+r'\cdot'+m('1;~1'),
266: m('0 1;1 0')+r'\cdot'+m('1 0;0 ~1'),
267: m('0 ~1;1 0')+r'\cdot'+m('1;1'),
270: m('1 0;0 ~1')+r'\cdot'+m('~5;2'),
271: m('1 0;0 ~1')+r'\cdot'+m('4;~6'),
272: m('1 0;0 ~1')+r'\cdot'+m('~5 4;2 ~6'),
273: m('1 0;0 ~1')+r'\cdot'+m('x;y'),
275: m('3 ~7;4 2')+r'\cdot X='+m('3 ~7;4 2'),
276: r'X\cdot'+m(r'5 \sqrt{3};~2 1')+'='+m(r'5 \sqrt{3};~2 1'),
277: m('0 2 1;1 0 3;1 1 0'),
281: m('0 1;1 0')+r'\cdot'+m('3;4'),
282: m('~1 0;0 1')+r'\cdot'+m('4;3'),
283: m('~1 0;0 1')+r'\cdot'+m('0 1;1 0'),
284: m('0 ~1;1 0')+r'\cdot'+m('3;4'),
285: m('1 0;0 ~1')+r'\cdot'+m('~5;2')+'='+m('~5;~2'),
287: m('~5;2'),
288: m('~5;~2'),
290: m('4;6'),
292: m('~1 0;0 1')+r'\cdot'+m('2;~7'),
293: m('~1 0;0 1')+r'\cdot'+m('~3;~5'),
294: m('~1 0;0 1')+r'\cdot'+m('2 ~3 a;~7 ~5 b'),
295: m('~1 0;0 1')+r'\cdot'+m('x;y'),
296: m('~1 0;0 1'),
299: m('1 0;0 1'),
300: m('a b;c d')+r'\cdot X='+m('a b;c d'),
301: r'X\cdot'+m('k l;m n')+'='+m('k l;m n'),
302: r'X\cdot'+m('1 0;0 1')+'='+m('~1 0;0 1'),
303: m('4 1;11 3')+r'\cdot'+m('3 ~1;~11 4'),
304: m('1 0 2;0 1 1;0 1 0')+r'\cdot'+m('1 0 2;0 1 1;0 1 0'),
310: r'X\cdot'+m('1 0;0 1')+'='+m('0 ~1;~1 0'),
311: r'X\cdot'+m('1 0;0 1')+'='+m('0 1;1 0'),
312: m('~1 0;0 1')+r'\cdot'+m('3;0'),
313: m('0 ~1;~1 0')+r'\cdot'+m('~3;0'),
314: m('0 ~1;~1 0')+r'\cdot'+m('~1 0;0 1'),
315: m('0 ~1;1 0')+r'\cdot'+m('3;0'),
316: m('3 ~2;4 1')+r'\cdot\left('+m('2 5;~3 ~1')+r'\cdot'+m('2;1')+r'\right)',
317: m('3 ~2;4 1')+r'\cdot T',
318: r'\left('+m('3 ~2;4 1')+r'\cdot'+m('2 5;~3 ~1')+r'\right)\cdot'+m('2;1')+r'=U\cdot'+m('2;1'),
319: r'U\cdot'+m('2;1'),
320: m('~1 0;0 ~1')+r'\cdot'+m('1 0 1;0 1 1'),
321: m('~1 0;0 ~1'),
322: m('0 1;~1 0'),
323: m('0 1 0 2;1 0 0 1;2 0 0 1;1 1 0 0'),
331: m('1 0;0 ~1')+r'\cdot'+m('0 1;1 0'),
332: m('3 ~2;4 1')+r'\cdot'+m('2 5;~3 ~1')+r'\cdot'+m('2;1'),
334: m('0 1;1 0')+r'\cdot'+m('x;y'),
336: m('1 0.3;0 1'),
}
formula.update(M)
formula = {k:v.replace('~',r'{}^{-}') for k,v in formula.items()}

# Readable labelled arrays have no drawing-specific instructional features.
formula[236] = r'\begin{gathered}\text{Matrix A - daily production}\\\text{number of each style made}\\\begin{array}{c|ccc}\text{worker}\backslash\text{style number}&\#1&\#2&\#3\\\#1&8&4&6\\\#2&6&6&8\end{array}\end{gathered}\qquad\begin{gathered}\text{Matrix B - number of strips}\\\text{of each type of wood}\\\text{for each style}\\\begin{array}{c|ccc}\text{style}&\text{oak }\#1&\text{walnut }\#2&\text{cherry }\#3\\\#1&10&10&0\\\#2&8&6&6\\\#3&0&10&10\end{array}\end{gathered}'
formula[255] = r'\begin{gathered}\text{total number of strips}\\\text{needed each day}\\C=\begin{array}{c|ccc}\text{worker}&\text{oak}&\text{walnut}&\text{cherry}\\\#1&\phantom{116}&\phantom{116}&\phantom{116}\\\#2&\phantom{116}&\phantom{116}&116\end{array}\end{gathered}'
formula[257] = r'\begin{array}{c|ccc}&\text{Children}&\text{Students}&\text{Adults}\\\text{Cinema I}&225&110&50\\\text{Cinema II}&75&180&225\\\text{Cinema III}&280&85&110\\\text{Cinema IV}&0&250&225\end{array}'

notes = {
44:'Calculator key notation: the source shows a radical symbol followed by (3), not a vinculum extending over the argument.',
45:'Bare radical key symbol, followed by (3+7) in the prose; kept as a symbol rather than extending a radical bar over its argument.',
96:'Source notation has an unusual composition-symbol placement and an unclosed parenthesis in its second expression. Transcribed literally; requires mathematical proofreading.',
104:'Source ends with the apparent coordinate typo (raised-minus 15.0), using a period rather than a comma. Preserved literally.',
228:'Source symbol is a centered dot even where surrounding prose reads it as matrix dimensions ("by"); not silently changed to a multiplication cross.',
236:'Converted labelled matrix layout to labelled LaTeX arrays; row and column labels and values retained.',
255:'Converted labelled incomplete matrix to a LaTeX array; all five intentionally blank entries retained.',
257:'Converted labelled matrix to a LaTeX array; row and column labels and values retained.',
263:'Incomplete 5-by-5 exercise matrix: all fifteen missing entries remain blank, with phantom zeroes only reserving layout space.',
}

original = (BACKUP / 'GAT-1-20.md').read_text()
# Currency prices must remain ordinary text when $ also delimits inline math.
original = original.replace('$', r'\$')
manifest = json.loads((BACKUP / 'manifest.json').read_text())
assets = {int(re.search(r'image(\d+)',a['browser_asset'])[1]): a for a in manifest['unique_assets']}
assert len(assets)==336
svg = {i for i,a in assets.items() if a['browser_asset'].endswith('.svg')}
assert svg <= formula.keys(), ('Untranscribed equations', svg-formula.keys())
assert formula.keys() <= assets.keys()

pattern = re.compile(r'!\[[^\]]*\]\(assets/image(\d+)\.svg\)|<img\s+src="assets/image(\d+)\.png"[^>]*\s*/>')
counts = {}
def replacement(match):
    n=int(match[1] or match[2])
    if n not in formula: return match[0]
    counts[n]=counts.get(n,0)+1
    return '$'+formula[n]+'$'
text = pattern.sub(replacement,original)
# Promote a paragraph containing just a formula (and optional punctuation) to
# display math. Formulae occurring within a sentence remain inline.
text = re.sub(r'^\$([^$\n]+)\$([.,]?)$',lambda m:'$$\n'+m[1]+m[2]+'\n$$',text,flags=re.M)
text = text.replace('> Text and graphics converted from the supplied Word document. See [conversion notes](conversion-report.md) for page references and remaining issues.', '> Text and graphics converted from the supplied Word document. Formula-only graphics have been transcribed to LaTeX; diagrams remain images. See [conversion notes](conversion-report.md) and the [formula review](formula-review.md) for remaining issues.')
assert set(counts)==set(formula)
(ROOT/'GAT-1-20.md').write_text(text)

review=[]
for n,a in sorted(assets.items()):
    placements=[p for p in manifest['placements'] if p['asset']==a['browser_asset']]
    entry={'image_id':f'image{n}','source_asset':a['browser_asset'],
           'status':'latex' if n in formula else 'retained_image',
           'occurrences':len(placements),
           'reference_pages':sorted(set(p['reference_page'] for p in placements if p.get('reference_page'))),
           'question_ids':list(dict.fromkeys(p['question_id'] for p in placements if p.get('question_id')))}
    if n in formula:
        entry['latex']=formula[n]
        assert len(placements)==counts[n],(n,len(placements),counts[n])
        a['representation']='latex'
        a['latex']=formula[n]
    else:
        entry['reason']='Diagram, graph, calculator screenshot, or annotated instructional layout; visual relationships retained.'
        a['representation']='image'
    if n in notes: entry['note']=notes[n]
    if a.get('issues'): entry['source_image_issues']=a['issues']
    review.append(entry)
for p in manifest['placements']:
    n=int(re.search(r'image(\d+)',p['asset'])[1])
    p['representation']='latex' if n in formula else 'image'
    if n in formula: p['latex']=formula[n]
stats={'images_reviewed':336,'formula_assets_converted':len(formula),
       'formula_occurrences_converted':sum(counts.values()),
       'image_assets_retained':336-len(formula),'image_occurrences_retained':666-sum(counts.values())}
manifest['latex_conversion']={'notation':'Standard $...$ and $$...$$ LaTeX delimiters; source raised minus written as {}^{-}.', **stats,
                              'original_assets_retained':True,'review_file':'formula-review.md','transcription_file':'formula-transcriptions.json'}
manifest['verification']['pre_latex_verification']=True
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
(ROOT/'formula-transcriptions.json').write_text(json.dumps({'statistics':stats,'assets':review},indent=2,ensure_ascii=False)+'\n')
print(json.dumps(stats,indent=2))
