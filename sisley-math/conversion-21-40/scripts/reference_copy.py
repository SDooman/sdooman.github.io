"""Make an internal rendering copy with original PDFs rasterized for Word.

The source DOCX is never modified. Original EMFs appear blank in the bundled
LibreOffice; this copy replaces only their preview media and disables OLE.
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E

ROOT=Path(__file__).resolve().parents[2]
def main():
    with ZipFile(ROOT/'source/GAT-21-40.docx') as src, ZipFile(ROOT/'conversion-21-40/checkpoints/reference.docx','w',ZIP_DEFLATED) as dest:
        r=E.fromstring(src.read('word/document.xml'));ns=r.nsmap
        for obj in r.findall('.//w:object',ns):
            obj.tag='{'+ns['w']+'}pict'
            for child in list(obj):
                if E.QName(child).localname=='OLEObject':obj.remove(child)
            for shape in obj.findall('.//v:shape',ns):shape.attrib.pop('{'+ns['o']+'}ole',None)
        rels=E.fromstring(src.read('word/_rels/document.xml.rels'))
        for rel in rels:
            if rel.get('Target','').endswith('.emf'):rel.set('Target',rel.get('Target')[:-4]+'.png')
        types=E.fromstring(src.read('[Content_Types].xml'))
        if not any(n.get('Extension')=='png' for n in types):E.SubElement(types,'{'+types.nsmap[None]+'}Default',Extension='png',ContentType='image/png')
        for name in src.namelist():
            data=src.read(name)
            if name=='word/document.xml':data=E.tostring(r)
            elif name=='word/_rels/document.xml.rels':data=E.tostring(rels)
            elif name=='[Content_Types].xml':data=E.tostring(types)
            elif name.startswith('word/media/') and name.endswith('.emf'):
                name=name[:-4]+'.png';data=(ROOT/'gat-21-40/assets/source-png'/Path(name).name).read_bytes()
            dest.writestr(name,data)

if __name__=='__main__':main()
