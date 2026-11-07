from zipfile import ZipFile
from pathlib import Path
from lxml import etree as E
from pypdf import PdfReader
from collections import Counter,defaultdict
import re,json,hashlib,html
BASE=Path('gat-1-20')
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
def q(s):a,b=s.split(':');return '{'+ns[a]+'}'+b
z=ZipFile('.conversion-work/sized.docx');root=E.fromstring(z.read('word/document.xml'));rels={x.get('Id'):x.get('Target') for x in E.fromstring(z.read('word/_rels/document.xml.rels'))};eq=json.load(open('.conversion-work/equations.json'));diagrams=json.load(open('.conversion-work/diagrams.json'))
pdf=PdfReader('.conversion-work/sized.pdf');pagemap={p.indirect_reference.idnum:i+1 for i,p in enumerate(pdf.pages)};figures=[]
def walk(o):
 if isinstance(o,list):
  for x in o:walk(x)
  return
 o=o.get_object() if hasattr(o,'get_object') else o
 if not isinstance(o,dict):return
 if o.get('/S')=='/Figure':figures.append({'page':pagemap[o.raw_get('/Pg').idnum],'bbox':list(map(float,o['/A']['/BBox']))})
 if '/K' in o:walk(o['/K'])
walk(pdf.trailer['/Root']['/StructTreeRoot']['/K']);assert len(figures)==666
assignment=0;question=None;placements=[];questions=[];paragraphs=[];text_parts=[];sections=[];assets={};numfig=0
# Small diagram labels seen in the source render and extracted graphics; none are silently guessed.
small={5,6,20,110,117,127,132,137,144,145,146,147,152,155,178,185,188,198,207,210,211,214,218,223,227,241,244,253,261}
# These line labels are rendered as a plain l or 1 and need comparison with a good original.
ambiguous={3,76,156,160,195,222,237,248,251,252}
notes={}
for n in small:notes[f'image{n}']='Very small diagram labels; inspect before using this exercise.'
for n in [218,227,244,253]:notes[f'image{n}']='Matrix entries inside the diagram are extremely small; verify them before publishing.'
for n in ambiguous:notes[f'image{n}']='The line label looks like “1” or plain “l”; verify whether it should be ℓ.'
for n in [307,325,333]:notes[f'image{n}']='Matrix brackets are visibly segmented; entries are preserved.'
def esc(t):
 t=html.escape(t,quote=False)
 return re.sub(r'([\\`*_\[\]])',r'\\\1',t)
def image_md(d,pi):
 global numfig
 blip=d.find('.//a:blip',ns);target=rels[blip.get(q('r:embed'))];name=Path(target).name;stem=Path(name).stem;is_eq=name in eq
 ext='svg' if is_eq else 'png';path=f'assets/{stem}.{ext}'
 f=figures[numfig];numfig+=1
 extent=d.find('.//wp:extent',ns);w=int(extent.get('cx'))/9525;h=int(extent.get('cy'))/9525
 if is_eq:w=eq[name]['width'];h=eq[name]['height']
 issues=[]
 if stem in notes:issues=[notes[stem]]
 placement={'id':f'gat-image-{numfig:04}','asset':path,'original':f'assets/originals/{name}','assignment':assignment,'question_id':question,'paragraph_index':pi,'reference_page':f['page'],'bbox_pt':f['bbox'],'display_width_px':round(w,2),'display_height_px':round(h,2),'issues':issues}
 placements.append(placement)
 assets.setdefault(name,{'original':f'assets/originals/{name}','browser_asset':path,'kind':'equation' if is_eq else 'diagram','sha256_original':hashlib.sha256((BASE/'assets/originals'/name).read_bytes()).hexdigest(),'issues':issues})
 alt=f'{"Equation" if is_eq else "Figure"} {stem[5:]} from assignment {assignment}'
 return f'![{alt}]({path})' if is_eq else f'<img src="{path}" alt="{alt}" width="{round(w)}" height="{round(h)}" />'
def run_md(r,pi):
 val=''
 for child in r:
  tag=E.QName(child).localname
  if tag=='t':text_parts.append(child.text or '');val+=esc(child.text or '')
  elif tag=='drawing':val+=image_md(child,pi)
  elif tag=='tab':val+='  '
  elif tag in ('br','cr'):val+='  \n' if child.get(q('w:type'))!='page' else '\n\n'
  elif tag=='noBreakHyphen':val+='‑'
  elif tag=='softHyphen':val+=''
  elif tag=='sym':raise ValueError('Unhandled symbol')
 rp=r.find('w:rPr',ns)
 if rp is not None and val.strip() and '<img' not in val and '![' not in val:
  v=rp.find('w:vertAlign',ns)
  if v is not None and v.get(q('w:val')) in ('superscript','subscript'):
   t='sup' if v.get(q('w:val'))=='superscript' else 'sub';val=f'<{t}>{val}</{t}>'
  position=rp.find('w:position',ns)
  if v is None and position is not None and int(position.get(q('w:val'))):
   tag='sup' if int(position.get(q('w:val')))>0 else 'sub';val=f'<{tag}>{val}</{tag}>'
  b=rp.find('w:b',ns);i=rp.find('w:i',ns)
  lead=val[:len(val)-len(val.lstrip())];tail=val[len(val.rstrip()):];core=val.strip()
  if b is not None and b.get(q('w:val'),'1') not in ('0','false'):core='<strong>'+core+'</strong>'
  if i is not None and i.get(q('w:val'),'1') not in ('0','false'):core='<em>'+core+'</em>'
  val=lead+core+tail
 return val
parts=['# GAT Assignments 1–20','> Text and graphics converted from the supplied Word document. See [conversion notes](conversion-report.md) for page references and remaining issues.',' | '.join(f'[Assignment {i}](#assignment-{i:02})' for i in range(1,21))]
for pi,p in enumerate(root.findall('.//w:body/w:p',ns)):
 raw=''.join(p.itertext()).strip();am=re.match(r'^ASSIGNMENT\s*#?\s*(\d+)',raw,re.I);rm=re.match(r'^([IVX]+)\.(?:\s|$)',raw)
 if am:
  assignment=int(am.group(1));question=None;aid=f'assignment-{assignment:02}';sections.append({'id':aid,'assignment':assignment,'paragraph_index':pi})
 if rm:
  roman=rm.group(1);question=f'gat-{assignment:02}-{roman.lower()}';questions.append({'id':question,'assignment':assignment,'label':roman,'paragraph_index':pi})
 before=numfig
 text=''.join(run_md(r,pi) for r in p.findall('.//w:r',ns)).strip()
 if not text:continue
 text=re.sub(r'</strong>(\s*)<strong>',r'\1',text)
 text=re.sub(r'</em>(\s*)<em>',r'\1',text)
 # Coalesce adjacent emphasis markers caused by Word run boundaries.
 text=re.sub(r'(?<=\w)\*\*\*\*(?=\w)','',text)
 if am:
  text=f'<a id="assignment-{assignment:02}"></a>\n\n## Assignment #{assignment}'
 elif rm:
  cleaned=re.sub(r'^(?:(?:<[^>]+>)|[*])*[IVX]+\.(?:(?:</[^>]+>)|[*])*\s*','',text).strip()
  text=f'<a id="{question}"></a>\n\n### {roman}.'+(f'\n\n{cleaned}' if cleaned else '')
 elif re.match(r'^\d+\.',text):text=re.sub(r'^(\d+)\.',r'\1\\.',text)
 # Question labels are left as authored; exercise instructions remain content.
 parts.append(text)
 paragraphs.append({'index':pi,'assignment':assignment,'question_id':question,'text':raw,'image_placements':[x['id'] for x in placements[before:]],'markdown':text})
assert numfig==len(figures)
source_text=''.join(root.xpath('.//w:body//w:t/text()',namespaces=ns));assert ''.join(text_parts)==source_text
assert len(sections)==20
# Join artificial hard paragraph breaks inside a sentence, preserving all words.
joined=[]
for block in parts:
 if joined and re.search(r'[A-Za-z]$',joined[-1]) and re.match(r'^[a-z]',block) and not joined[-1].startswith(('#','<','>')):
  joined[-1]+=' '+block
 else:joined.append(block)
md='\n\n'.join(joined)+'\n';md=re.sub(r'(<img [^>]+/>)\s*(?=[A-Za-z])',r'\1\n\n',md);(BASE/'GAT-1-20.md').write_text(md)
for qu in questions:
 qu['reference_pages']=sorted({x['reference_page'] for x in placements if x['question_id']==qu['id']})
manifest={'source_filename':'GAT 1-20.doc','source_sha256':hashlib.sha256(Path('source/GAT-1-20.doc').read_bytes()).hexdigest(),'original_cached_page_count':87,'reference_render_page_count':len(pdf.pages),'pagination_note':'Reference pages are from a size-normalized LibreOffice render, not verified original Word page boundaries.','assignments':sections,'questions':questions,'unique_assets':list(assets.values()),'placements':placements}
(BASE/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n');Path('.conversion-work/paragraphs.json').write_text(json.dumps(paragraphs,ensure_ascii=False,indent=2))
pages=defaultdict(list)
for x in placements:pages[x['reference_page']].append(x)
report=['# Conversion report','Converted all 20 assignments. Preserved all 666 image placements using 336 distinct browser-readable graphics (212 SVG equation images and 124 PNG graphics), with 336 original PICT/EMF files retained. All body text in the intermediate Word extraction is represented in the Markdown; superscripts and subscripts are retained.','## Page numbering','The source file reports **87 pages** in its saved metadata. The initial conversion produced 1,351 pages because equation sizes were misread. Correcting those sizes produced **94 reference pages**. Original Word page boundaries could not be verified. The page numbers below refer to that 94-page render, and assignment/question links identify the content independently.','## General limitations','- Many equations remain images, not editable LaTeX or executable expressions. The legacy negative-number notation (a raised minus) is preserved.\n- Print layout, boxes, whitespace, and headers/footers are reflowed. Side-by-side questions follow their source reading order.\n- Old font substitutions and blank EMF rendering were repaired. The original graphics are retained for comparison.\n- Some embedded diagrams have tiny labels or matrix entries; these are flagged below rather than guessed. Some line labels resemble the numeral 1.\n- Source wording and apparent source typos are preserved. This is a conversion and visual recovery pass, not a mathematical answer-key audit.','## Issues by reference page','Pages with an observed remaining graphic issue are listed individually. “Reference page” does not mean the original printed textbook page.','| Reference page | Assignment and question | Issue |','| --- | --- | --- |']
problem_pages=[]
for pg,items in sorted(pages.items()):
 bad=[x for x in items if x['issues']]
 if not bad:continue
 problem_pages.append(pg);refs=[];issues=[]
 for x in bad:
  qu=x['question_id'];label=f'{x["assignment"]}'+(' '+qu.rsplit('-',1)[-1].upper() if qu else '')
  link=f'[{label}](GAT-1-20.md#{qu or "assignment-"+str(x["assignment"]).zfill(2)})'
  if link not in refs:refs.append(link)
  for note in x['issues']:
   if note not in issues:issues.append(note)
 report.append(f'| {pg} | '+', '.join(refs)+' | '+' '.join(issues)+' |')
clean=[i for i in range(1,len(pdf.pages)+1) if i not in problem_pages]
def ranges(seq):
 out=[]
 for n in seq:
  if out and n==out[-1][-1]+1:out[-1].append(n)
  else:out.append([n])
 return ', '.join(str(g[0]) if len(g)==1 else f'{g[0]}–{g[-1]}' for g in out)
report+=['','**Other reference pages:** '+ranges(clean)+'. No additional graphic omission or obvious rendering failure was identified in the extracted assets. This is not a claim of exact original pagination or mathematical proofreading.','## Using this material in a learning platform','The Markdown contains stable assignment and question anchors. `manifest.json` maps each image placement to its assignment, question, original asset, and reference page. These identifiers can later key progress records. Calculator instructions remain as source text; interactive replacements and account/local storage have not been implemented.','Use the PNG fallbacks in `assets/equations-png/` if a target Markdown viewer does not support SVG. Both image types are local; keep the `assets` folder beside the Markdown.']
(BASE/'conversion-report.md').write_text('\n\n'.join(report[:report.index('| Reference page | Assignment and question | Issue |')])+'\n\n'+'\n'.join(report[report.index('| Reference page | Assignment and question | Issue |'):])+'\n')
print(json.dumps({'assignments':len(sections),'questions':len(questions),'nonempty_paragraphs':len(paragraphs),'images':numfig,'unique_assets':len(assets),'reference_pages':len(pdf.pages),'issue_pages':problem_pages,'source_text_characters':len(source_text)},indent=2))
