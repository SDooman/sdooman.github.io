"""Read the MTEF2/4 records found in this document; fail on unsupported records.

Format reference: original Design Science MTEF documentation, archived at
https://rtf2latex2e.sourceforge.net/MTEF3.html (these MTEF2/4 streams use 8-bit characters).
The parsed tree is retained independently of the LaTeX conversion.
"""
import struct, json
from pathlib import Path
from collections import Counter

class Reader:
    def __init__(self,data):
        self.data=data; self.pos=5
        assert data[:5] in (b'\x02\x00\x00\x03\x00',b'\x04\x00\x00\x03\x07'),data[:5]
    def take(self,n):
        assert self.pos+n<=len(self.data),'truncated MTEF'
        b=self.data[self.pos:self.pos+n];self.pos+=n;return b
    def byte(self):return self.take(1)[0]
    def items(self):
        result=[]
        while self.pos<len(self.data):
            item=self.item()
            if item['type']==0:return result
            result.append(item)
        raise ValueError('Unterminated MTEF list')
    def item(self):
        tag=self.byte();typ=tag&15;flags=tag>>4
        out={'type':typ}
        if flags:out['flags']=flags
        if flags&8:
            dx,dy=self.take(2)
            out['nudge']=list(struct.unpack('<hh',self.take(4))) if (dx,dy)==(128,128) else [dx-128,dy-128]
        if typ==0:return out
        if typ==1:
            if flags&4:out['line_spacing']=list(self.take(2))
            if flags&2:out['ruler']=self.item()
            out['children']=[] if flags&1 else self.items()
        elif typ==2:
            out['face']=self.byte()-128;out['code']=self.byte()
            if flags&2:out['embellishments']=self.items()
        elif typ==3:
            out['selector'],out['variation'],out['options']=self.take(3);out['children']=self.items()
        elif typ==4:
            out['halign'],out['valign']=self.take(2)
            if flags&2:out['ruler']=self.item()
            out['children']=self.items()
        elif typ==5:
            out['valign'],out['halign'],out['vjust'],out['rows'],out['columns']=self.take(5)
            out['row_partitions']=list(self.take((out['rows']+4)//4))
            out['column_partitions']=list(self.take((out['columns']+4)//4))
            out['children']=self.items()
        elif typ==6:out['embellishment']=self.byte()
        elif typ==7:out['stops']=list(self.take(3*self.byte()))
        elif typ==8:
            out['font_id']=self.byte();out['style']=self.byte();name=[]
            while (x:=self.byte()):name.append(x)
            out['font_name']=bytes(name).decode('mac_roman')
        elif typ==9:
            size=self.byte();out['size']=[size,*self.take(2 if size==101 else 3 if size==100 else 1)]
        elif typ not in (10,11,12,13,14):raise ValueError(f'Unsupported record {typ} at {self.pos-1}')
        return out
    def parse(self):
        result=self.items()
        assert not any(self.data[self.pos:]),f'trailing MTEF data at {self.pos}'
        return result

def walk(items):
    for item in items:
        yield item
        yield from walk(item.get('children',[]))
        yield from walk(item.get('embellishments',[]))

if __name__=='__main__':
    root=Path(__file__).resolve().parents[2]; result={};errors={};selectors=Counter();chars=Counter();fonts=Counter();embell=Counter()
    for p in (root/'gat-21-40/assets/ole').glob('*.mtef'):
        try:
            tree=Reader(p.read_bytes()).parse();result[p.stem]=tree
            for n in walk(tree):
                if n['type']==3:selectors[(n['selector'],n['variation'])]+=1
                if n['type']==2:chars[(n['face'],n['code'])]+=1
                if n['type']==8:fonts[(n['font_id'],n['font_name'],n['style'])]+=1
                if n['type']==6:embell[n['embellishment']]+=1
        except Exception as e:errors[p.stem]=str(e)
    (root/'conversion-21-40/checkpoints/mtef-trees.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'parsed':len(result),'errors':errors,'templates':dict((str(k),v) for k,v in sorted(selectors.items())),
                     'fonts':dict((str(k),v) for k,v in fonts.items()),'embellishments':dict(embell),
                     'special_chars':dict((str(k),v) for k,v in sorted(chars.items()) if k[0] not in (1,2,3,7,8) or k[1]>127)},indent=2))
