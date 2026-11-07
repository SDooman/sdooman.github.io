"""Extract immutable embedded EMF/PDF artwork and OLE streams from this batch.

No Office object is executed. The small CFB reader supports the compound files
encountered here and rejects cyclic/out-of-range sector chains.
"""
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
from pypdf import PdfReader
import argparse, hashlib, io, json, logging, struct, subprocess
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[2]
BOOK = ROOT/'gat-21-40'
CHECK = ROOT/'conversion-21-40/checkpoints'
def write(p, x):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(x, ensure_ascii=False, indent=2)+'\n')
def sha(b): return hashlib.sha256(b).hexdigest()

def streams(b):
    assert b[:8] == bytes.fromhex('d0cf11e0a1b11ae1')
    sector = 1 << struct.unpack_from('<H',b,30)[0]
    mini = 1 << struct.unpack_from('<H',b,32)[0]
    def sec(n):
        assert n < len(b)//sector-1
        return b[(n+1)*sector:(n+2)*sector]
    def chain(n, table, get):
        out=[]; seen=set()
        while n < 0xfffffffa:
            assert n not in seen and n < len(table)
            seen.add(n); out.append(get(n)); n=table[n]
        return b''.join(out)
    fat_ids=[x for x in struct.unpack_from('<109I',b,76) if x < 0xfffffffa]
    assert struct.unpack_from('<I',b,72)[0] == 0, 'DIFAT continuation unsupported'
    fat=list(struct.unpack('<'+'I'*(len(fat_ids)*sector//4), b''.join(sec(x) for x in fat_ids)))
    regular=lambda n:chain(n,fat,sec)
    directory=regular(struct.unpack_from('<I',b,48)[0]); entries=[]
    for offset in range(0,len(directory),128):
        d=directory[offset:offset+128]; size=struct.unpack_from('<H',d,64)[0]
        if size<2: continue
        entries.append((d[:size-2].decode('utf-16-le'),d[66],struct.unpack_from('<I',d,116)[0],struct.unpack_from('<Q',d,120)[0]))
    root=next(x for x in entries if x[1]==5); ministream=regular(root[2])[:root[3]]
    mf=regular(struct.unpack_from('<I',b,60)[0]); minifat=list(struct.unpack('<'+'I'*(len(mf)//4),mf))
    result={}
    for name,typ,start,size in entries:
        if typ != 2: continue
        data=chain(start,minifat,lambda n:ministream[n*mini:(n+1)*mini]) if size<4096 else regular(start)
        result[name]=data[:size]
    return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--pdftocairo',required=True);args=parser.parse_args()
    logging.getLogger('pypdf').setLevel(logging.ERROR)
    for name in ('originals','source-pdf','source-png','source-svg','ole'):(BOOK/'assets'/name).mkdir(parents=True,exist_ok=True)
    rows=[]; equations={}
    with ZipFile(ROOT/'source/GAT-21-40.docx') as z:
        root=E.fromstring(z.read('word/document.xml'));ns=root.nsmap
        rels={x.get('Id'):x.get('Target') for x in E.fromstring(z.read('word/_rels/document.xml.rels'))}
        for obj in root.findall('.//w:object',ns):
            img=obj.find('.//v:imagedata',ns);ole=obj.find('.//o:OLEObject',ns)
            ident=Path(rels[img.get('{'+ns['r']+'}id')]).stem
            name=rels[ole.get('{'+ns['r']+'}id')];b=z.read('word/'+name)
            (BOOK/'assets/ole'/Path(name).name).write_bytes(b)
            ss=streams(b);native=ss.get('Equation Native',ss.get('\x01Ole10Native'))
            assert native is not None
            if 'Equation Native' in ss:
                offset=struct.unpack_from('<I',native)[0];count=struct.unpack_from('<I',native,8)[0]
            else:offset=4;count=struct.unpack_from('<I',native)[0]
            mtef=native[offset:offset+count]
            assert len(mtef)==count and mtef[0] in (2,4),(ident,mtef[:10])
            (BOOK/'assets/ole'/f'{ident}.mtef').write_bytes(mtef)
            equations[ident]={'ole_file':Path(name).name,'ole_sha256':sha(b),'mtef_sha256':sha(mtef),'mtef_version':mtef[0]}
        for n in sorted((n for n in z.namelist() if n.startswith('word/media/')),key=lambda x:int(Path(x).stem[5:])):
            b=z.read(n); ident=Path(n).stem;(BOOK/'assets/originals'/Path(n).name).write_bytes(b)
            pdfs=[];o=0
            while o<len(b):
                op,size=struct.unpack_from('<II',b,o);assert size>=8 and o+size<=len(b)
                rec=b[o:o+size];o+=size
                if op==70 and b'%PDF-' in rec:
                    start=rec.index(b'%PDF-');end=rec.rfind(b'%%EOF')+5;assert end>start
                    pdfs.append(rec[start:end]+b'\n')
            assert len(pdfs)==1,(n,len(pdfs))
            pdf=pdfs[0];p=BOOK/'assets/source-pdf'/f'{ident}.pdf';p.write_bytes(pdf)
            reader=PdfReader(p);assert len(reader.pages)==1;page=reader.pages[0]
            rows.append({'id':ident,'original':n,'width':float(page.mediabox.width),'height':float(page.mediabox.height),
                         'text':page.extract_text(),'emf_sha256':sha(b),'pdf_sha256':sha(pdf),'equation_object':equations.get(ident)})
    write(CHECK/'embedded-pdfs.json',rows)
    def render(row):
        ident=row['id'];source=BOOK/'assets/source-pdf'/f'{ident}.pdf'
        for options,dest in [(['-png','-r','216','-singlefile'],BOOK/'assets/source-png'/ident),(['-svg'],BOOK/'assets/source-svg'/f'{ident}.svg')]:
            subprocess.run([args.pdftocairo,*options,str(source),str(dest)],check=True,capture_output=True)
    with ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(render,rows))
    print(json.dumps({'graphics':len(rows),'equation_objects':len(equations),'source_pdf_and_png_and_svg':len(rows)}))

if __name__=='__main__':main()
