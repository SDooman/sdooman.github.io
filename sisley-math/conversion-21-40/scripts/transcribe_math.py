"""Translate the retained equation trees to LaTeX without evaluating exercises."""
from pathlib import Path
import json,re
from mtef import Reader,walk

ROOT=Path(__file__).resolve().parents[2]
def char(n):
    f,c=n['face'],n['code']
    if f==6:return {43:'+',45:'-',60:'<',61:'=',62:'>',180:r'\times ',184:r'\div ',215:r'\cdot '}[c]
    if f==4:return {112:r'\pi '}[c]
    if f==11:return {108:r'\ell ',111:r'\circ '}[c]
    # This legacy equation font uses byte C5 for a raised minus, not the
    # Mac Roman approximately-equal character. Checked in all eight source PDFs.
    if c==197:return r'{}^{-}'
    assert f in (1,2,3,7,8,22),f
    s=bytes([c]).decode('mac_roman')
    return {'{':r'\{','}':r'\}','_':r'\_','%':r'\%','#':r'\#','&':r'\&'}.get(s,s)

def sequence(nodes):
    out=[];i=0
    while i<len(nodes):
        n=nodes[i]
        if n['type']==2 and n['face'] in (1,2) and n['code']!=197:
            face=n['face'];text=''
            while i<len(nodes) and nodes[i]['type']==2 and nodes[i]['face']==face and nodes[i]['code']!=197:
                text+=char(nodes[i]);i+=1
            # Long space runs are exercise blanks or column separation. Emit
            # explicit widths so HTML/TeX whitespace collapsing cannot erase them.
            command='\\text{' if face==1 else '\\mathrm{'
            out.append(''.join('\\hspace{'+str(len(piece)*.25)+'em}' if re.fullmatch(r' {2,}',piece) else command+piece+'}' for piece in re.split(r'( {2,})',text) if piece))
        else:out.append(latex(n));i+=1
    return ''.join(out)

def latex(n):
    typ=n['type']
    if typ in (7,8,9,10,11,12,13,14):return ''
    if typ==1:return sequence(n['children'])
    if typ==2:return char(n)
    if typ==4:
        alignment={1:'l',2:'c',3:'r'}.get(n['halign'],'l')
        return r'\begin{array}{'+alignment+'}'+r' \\ '.join(latex(x) for x in n['children'] if x['type']==1)+r'\end{array}'
    if typ==5:
        assert not any(n['row_partitions']+n['column_partitions']),'Partitioned matrix needs review'
        cells=[latex(x) or r'\phantom{0}' for x in n['children'] if x['type']==1];cols=n['columns']
        assert len(cells)==n['rows']*cols
        return r'\begin{matrix}'+r' \\ '.join(' & '.join(cells[i:i+cols]) for i in range(0,len(cells),cols))+r'\end{matrix}'
    if typ==3:
        sel,var=n['selector'],n['variation'];slots=[latex(x) for x in n['children'] if x['type'] in (1,4,5)]
        if sel in (1,2,3):
            assert len(slots)==1
            l,r={1:('(',')'),2:(r'\{',r'\}'),3:('[',']')}[sel]
            if var==1:r='.'
            elif var==2:l='.'
            else:assert var==0
            return r'\left'+l+' '+slots[0]+r' \right'+r
        if sel==13:
            assert var==0 and len(slots) in (1,2) and not any(slots[1:]),slots
            return r'\sqrt{'+slots[0]+'}'
        if sel==14:
            assert var==0 and len(slots)==2
            return r'\frac{'+slots[0]+'}{'+slots[1]+'}'
        if sel in (15,44):
            assert len(slots)==2 and var in (0,1,2)
            sub,sup=slots
            return ('{}' if sel==44 else '')+('_{'+sub+'}' if sub else '')+('^{'+sup+'}' if sup else '')
        raise ValueError(f'Unsupported template {sel}/{var}')
    raise ValueError(f'Unsupported node {typ}')

def main():
    trees=json.loads((ROOT/'conversion-21-40/checkpoints/mtef-trees.json').read_text());items=[]
    for ident,tree in sorted(trees.items(),key=lambda x:int(x[0][5:])):
        value=sequence(tree)
        items.append({'id':ident,'latex':value,'method':'native-equation-tree','status':'candidate','review':'needs_review',
                      'source_asset':f'assets/source-png/{ident}.png','notes':[]})
    (ROOT/'gat-21-40/formula-transcriptions.json').write_text(json.dumps({'version':1,'assets':items},ensure_ascii=False,indent=2)+'\n')
    print('Native formulas converted:',len(items))

if __name__=='__main__':main()
