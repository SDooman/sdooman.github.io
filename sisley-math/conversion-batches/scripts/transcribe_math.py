"""Translate the retained equation trees to LaTeX without evaluating exercises."""
from pathlib import Path
import json,re
from mtef import Reader,walk

ROOT=Path(__file__).resolve().parents[2]
def char(n):
    f,c=n['face'],n['code']
    if f==6:return {42:r'\ast ',43:'+',45:'-',60:'<',61:'=',62:'>',163:r'\leq ',174:r'\rightarrow ',179:r'\geq ',180:r'\times ',184:r'\div ',185:r'\neq ',187:r'\approx ',215:r'\cdot '}[c]
    if f==4:return {97:r'\alpha ',98:r'\beta ',103:r'\gamma ',112:r'\pi ',113:r'\theta '}[c]
    if f==5:return {68:r'\Delta '}[c]
    if f==11:return {108:r'\ell ',111:r'\circ '}[c]
    # This legacy equation font uses byte C5 for a raised minus, not the
    # Mac Roman approximately-equal character. Checked against source previews.
    if c==197:return r'{}^{-}'
    # CA is a degree glyph in these equation fonts, not Mac Roman NBSP.
    # All eight affected source assets were compared visually.
    if c==202:return r'{}^{\circ}'
    # The text face in image273 uses AA/BA for opening/closing double quotes.
    if f==1 and c in (170,186):return {170:'``',186:"''"}[c]
    assert f in (1,2,3,7,8,22),f
    s=bytes([c]).decode('mac_roman')
    return {'{':r'\{','}':r'\}','_':r'\_','%':r'\%','#':r'\#','&':r'\&','$':r'\$'}.get(s,s)

def sequence(nodes):
    out=[];i=0
    while i<len(nodes):
        n=nodes[i]
        if n['type']==2 and n['face'] in (1,2) and n['code'] not in (197,202) and not n.get('embellishments'):
            face=n['face'];text=''
            while i<len(nodes) and nodes[i]['type']==2 and nodes[i]['face']==face and nodes[i]['code'] not in (197,202) and not nodes[i].get('embellishments'):
                text+=char(nodes[i]);i+=1
            # Long space runs are exercise blanks or column separation. Emit
            # explicit widths so HTML/TeX whitespace collapsing cannot erase them.
            command='\\text{' if face==1 else '\\mathrm{'
            spaces=r' +' if face==2 else r' {2,}'
            out.append(''.join('\\hspace{'+str(len(piece)*.25)+'em}' if re.fullmatch(spaces,piece) else command+piece+'}' for piece in re.split('('+spaces+')',text) if piece))
        else:out.append(latex(n));i+=1
    return ''.join(out)

def latex(n):
    typ=n['type']
    if typ in (7,8,9,10,11,12,13,14):return ''
    if typ==1:return sequence(n['children'])
    if typ==2:
        value=char(n)
        for e in n.get('embellishments',[]):
            assert e['embellishment']==18,e
            value+=r'^{\prime\prime\prime}'
        return value
    if typ==4:
        alignment={1:'l',2:'c',3:'r'}.get(n['halign'],'l')
        return r'\begin{array}{'+alignment+'}'+r' \\ '.join(latex(x) for x in n['children'] if x['type']==1)+r'\end{array}'
    if typ==5:
        cells=[latex(x) or r'\phantom{0}' for x in n['children'] if x['type']==1];cols=n['columns']
        assert len(cells)==n['rows']*cols
        if any(n['row_partitions']+n['column_partitions']):
            def partitions(data,count):return [(data[i//4]>>(2*(i%4)))&3 for i in range(count)]
            rp=partitions(n['row_partitions'],n['rows']+1);cp=partitions(n['column_partitions'],cols+1)
            assert all(v in (0,1) for v in rp+cp),'Non-solid matrix partition'
            spec=''.join(('|' if cp[i] else '')+'c' for i in range(cols))+('|' if cp[-1] else '')
            lines=[(r'\hline ' if rp[i] else '')+' & '.join(cells[i*cols:(i+1)*cols]) for i in range(n['rows'])]
            return r'\begin{array}{'+spec+'}'+r' \\ '.join(lines)+(r' \\ \hline ' if rp[-1] else '')+r'\end{array}'
        return r'\begin{matrix}'+r' \\ '.join(' & '.join(cells[i:i+cols]) for i in range(0,len(cells),cols))+r'\end{matrix}'
    if typ==3:
        sel,var=n['selector'],n['variation'];slots=[latex(x) for x in n['children'] if x['type'] in (1,4,5)]
        if sel in (1,2,3,4):
            assert len(slots)==1
            l,r={1:('(',')'),2:(r'\{',r'\}'),3:('[',']'),4:('|','|')}[sel]
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
    import sys
    batch=sys.argv[1];check=ROOT/f'conversion-batches/checkpoints/{batch}';book=ROOT/f'gat-{batch}'
    trees=json.loads((check/'mtef-trees.json').read_text());assets=json.loads((check/'assets.json').read_text());items=[];records={};errors={}
    for ident,tree in trees.items():
        try:records[ident]={'id':ident,'latex':sequence(tree),'method':'native-equation-tree','review':'needs_review'}
        except Exception as e:errors[ident]=repr(e)
    for row in assets:
        native=row['native_equations']
        if row.get('pict_version')==1 and len(native)==1 and native[0]['id'] in records:
            items.append({**records[native[0]['id']],'id':row['id'],'native_record':native[0]['id'],'source_asset':f'assets/source-png/{row["id"]}.png','notes':[]})
    (book/'formula-transcriptions.json').write_text(json.dumps({'version':1,'assets':items},ensure_ascii=False,indent=2)+'\n')
    (book/'native-equations.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
    (check/'math-errors.json').write_text(json.dumps(errors,indent=2)+'\n')
    print(json.dumps({'batch':batch,'formula_assets':len(items),'native_equation_records':len(records),'errors':errors}))

if __name__=='__main__':main()
