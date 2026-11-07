"""Preserve DOCX body order as Markdown before any formula replacements."""
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
from pypdf import PdfReader
import hashlib, html, json, re

import sys
BATCH=sys.argv[1]; FIRST,LAST=map(int,BATCH.split('-')); ROOT=Path(__file__).resolve().parents[2];BOOK=ROOT/f'gat-{BATCH}';CHECK=ROOT/f'conversion-batches/checkpoints/{BATCH}'
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def escape(t):return re.sub(r'([\\`*_\[\]$])',r'\\\1',html.escape(t,quote=False))
def main():
    source=ROOT/f'source/GAT-{BATCH}.doc';z=ZipFile(CHECK/'sized.docx');root=E.fromstring(z.read('word/document.xml'));ns=root.nsmap
    ns['a']='http://schemas.openxmlformats.org/drawingml/2006/main';ns['wp']='http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
    rels={x.get('Id'):x.get('Target') for x in E.fromstring(z.read('word/_rels/document.xml.rels'))}
    metadata={x['id']:x for x in json.loads((CHECK/'assets.json').read_text())}
    placement=[];paragraphs=[];questions=[];assignments=[];alltext=[];assignment=0;question=None;saved_page=1
    parts=[f'# GAT Assignments {BATCH.replace(chr(45),chr(8211))}','> Converted from the supplied Word document. [Conversion notes](conversion-report.md) describe the graphics and remaining review items.',
           ' | '.join(f'[Assignment {i}](#assignment-{i})' for i in range(FIRST,LAST+1))]
    def graphic(node,pi):
        if E.QName(node).localname=='object':
            image=node.find('.//v:imagedata',ns);target=rels[image.get('{'+ns['r']+'}id')]
            style=node.find('.//v:shape',ns).get('style');dims={k:float(v)*(72 if unit=='in' else 1) for k,v,unit in re.findall(r'(width|height):([\d.]+)(pt|in)',style)}
            w,h=dims['width']*4/3,dims['height']*4/3
        else:
            image=node.find('.//a:blip',ns);target=rels[image.get('{'+ns['r']+'}embed')];ext=node.find('.//wp:extent',ns)
            w,h=int(ext.get('cx'))/9525,int(ext.get('cy'))/9525
        ident=Path(target).stem;item=metadata[ident];pid=f'gat{FIRST}{LAST}-media-{len(placement)+1:04}'
        placement.append({'id':pid,'asset_id':ident,'assignment':assignment,'question_id':question,'paragraph_index':pi,
                          'saved_break_segment':saved_page,'reference_page':None,'display_width_px':round(w,2),'display_height_px':round(h,2),
                          'asset':f'assets/source-png/{ident}.png','original':f'assets/originals/{Path(item["original"]).name}','representation':'image'})
        return f'<img src="assets/source-png/{ident}.png" alt="Source graphic {ident[5:]} from assignment {assignment}" width="{round(w)}" data-placement="{pid}" />'
    def run(r,pi):
        nonlocal saved_page
        val=''
        for child in r:
            tag=E.QName(child).localname
            if tag=='t':t=child.text or '';alltext.append(t);val+=escape(t)
            elif tag in ('drawing','object'):val+=graphic(child,pi)
            elif tag=='tab':val+='  '
            elif tag in ('br','cr'):val+='\n\n' if child.get('{'+ns['w']+'}type')=='page' else '  \n'
            elif tag=='lastRenderedPageBreak':saved_page+=1
            elif tag=='noBreakHyphen':val+='‑'
            elif tag=='sym':raise ValueError('Unmapped Word symbol')
        if val.strip() and '<img' not in val:
            props=r.find('w:rPr',ns)
            if props is not None:
                align=props.find('w:vertAlign',ns);position=props.find('w:position',ns)
                supersub=align.get('{'+ns['w']+'}val') if align is not None else None
                if supersub in ('superscript','subscript'):val=f'<{supersub[:3]}>{val}</{supersub[:3]}>'
                elif position is not None and int(position.get('{'+ns['w']+'}val')):
                    tag='sup' if int(position.get('{'+ns['w']+'}val'))>0 else 'sub';val=f'<{tag}>{val}</{tag}>'
                for style,tag in [('b','strong'),('i','em')]:
                    setting=props.find('w:'+style,ns)
                    if setting is not None and setting.get('{'+ns['w']+'}val','1') not in ('0','false'):
                        lead=val[:len(val)-len(val.lstrip())];tail=val[len(val.rstrip()):];val=lead+f'<{tag}>'+val.strip()+f'</{tag}>'+tail
        return val
    assert not root.findall('.//w:tbl',ns),'Tables require explicit conversion'
    for pi,p in enumerate(root.findall('.//w:body/w:p',ns)):
        raw=''.join(p.xpath('.//w:t/text()',namespaces=ns)).strip();am=re.match(r'^ASSIGNMENT\s*#?\s*(\d+)',raw,re.I);rm=re.match(r'^([IVX]+)(?:\.(?:\s|$)|$)',raw)
        if am:
            assignment=int(am.group(1));question=None;assignments.append({'id':f'assignment-{assignment}','assignment':assignment,'paragraph_index':pi})
        # A subquestion labelled I after H is alphabetic, not a second Roman I.
        if rm and rm.group(1)=='I' and any(q['assignment']==assignment for q in questions):rm=None
        if rm:
            roman=rm.group(1);question=f'gat-{assignment}-{roman.lower()}';questions.append({'id':question,'label':roman,'assignment':assignment,'paragraph_index':pi})
        before=len(placement);text=''.join(run(r,pi) for r in p.findall('.//w:r',ns)).strip()
        if not text:continue
        for tag in ('strong','em','sup','sub'):text=re.sub(f'</{tag}>(\\s*)<{tag}>',r'\1',text)
        if am:text=f'<a id="assignment-{assignment}"></a>\n\n## Assignment #{assignment}'
        elif rm:
            text=re.sub(r'^(?:(?:<[^>]+>)|[*])*[IVX]+\.?(?:(?:</[^>]+>)|[*])*\s*','',text).strip()
            text=f'<a id="{question}"></a>\n\n### {roman}.\n\n{text}'
        elif re.match(r'^\d+\.',text):text=re.sub(r'^(\d+)\.',r'\1\\.',text)
        parts.append(text);paragraphs.append({'index':pi,'assignment':assignment,'question_id':question,'text':raw,'media_ids':[x['asset_id'] for x in placement[before:]],'markdown':text})
    source_text=''.join(root.xpath('.//w:body//w:t/text()',namespaces=ns));assert ''.join(alltext)==source_text
    assert [a['assignment'] for a in assignments]==list(range(FIRST,LAST+1))
    assert len(placement)==len(root.findall('.//w:drawing',ns))
    assert {p['asset_id'] for p in placement}==set(metadata)
    md='\n\n'.join(parts)+'\n';(BOOK/f'GAT-{BATCH}.md').write_text(md);(CHECK/'image-based.md').write_text(md)
    manifest={'version':1,'source_filename':source.name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
              'original_cached_page_count':{'41-58':79,'59-80':103,'81-100':98,'101-119':102}[BATCH],'reference_render_page_count':None,'pagination_note':'Saved page-break markers are incomplete; reference pagination comes from the repaired render, not original printed numbering.',
              'body_text_characters':len(source_text),'assignments':assignments,'questions':questions,'placements':placement,'assets':list(metadata.values())}
    write(BOOK/'manifest.json',manifest);write(CHECK/'paragraphs.json',paragraphs)
    print(json.dumps({'assignments':len(assignments),'questions':len(questions),'graphics':len(placement),'source_characters_preserved':len(source_text)}))

if __name__=='__main__':main()
