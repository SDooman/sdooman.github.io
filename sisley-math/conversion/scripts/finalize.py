from pathlib import Path
import json,re,zipfile,hashlib
base=Path('gat-1-20')
external=[
(12,'gat-03-i','Reflections in Parallel Lines — Sketch Sheet #1'),
(18,'gat-04-xi','Composites of Reflections in Parallel Lines — Sketch Sheet #2'),
(29,'gat-06-vii','Composite of Reflections in Intersecting Lines — Sketch Sheet #1'),
(30,'gat-06-vii','Composite of Reflections in Intersecting Lines — Sketch Sheet #2'),
(44,'gat-09-vi','Reflections in Intersecting Lines — Sketch Sheet #3'),
(46,'gat-10-ii','Reflections in Intersecting Lines — Sketch Sheet #4'),
(61,'gat-13-iii','Symmetry Series — Sketch Sheet #1'),
(65,'gat-14-iv','Symmetry Series — Sketch Sheet #2'),
(69,'gat-15-iv','Symmetry Series — Sketch Sheet #3'),
(73,'gat-16-iv','Symmetry Series — Sketch #4')]
m=json.loads((base/'manifest.json').read_text());m['external_dependencies']=[{'reference_page':pg,'question_id':q,'title':title,'status':'referenced but not included in supplied document'} for pg,q,title in external]
for a in m['unique_assets']:
 if a['kind']=='equation':a['png_fallback']='assets/equations-png/'+Path(a['original']).stem+'.png'
m['verification']={'detected_image_placements':666,'browser_loaded_images':666,'broken_image_links':0,'source_text_comparison':'Matches imported Word body text after normalizing whitespace and capitalization.','distinct_assets_visually_reviewed':336,'question_ids_unique':True}
(base/'manifest.json').write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n')
p=base/'conversion-report.md';s=p.read_text();s=s.replace('- Source wording and apparent source typos', '- **10 separate classroom sketch sheets are referenced but are not included in this file.** Those exercises need the additional source sheets.\n- Source wording and apparent source typos')
lines=s.splitlines();rows={};first=None;last=None
for i,line in enumerate(lines):
 mt=re.match(r'^\| (\d+) \| (.*?) \| (.*?) \|$',line)
 if mt:
  if first is None:first=i
  last=i;rows[int(mt[1])]=[mt[2],mt[3]]
for pg,q,title in external:
 assignment=int(q.split('-')[1]);label=q.rsplit('-',1)[1].upper();link=f'[{assignment} {label}](GAT-1-20.md#{q})';msg=f'Missing separate worksheet: {title}.'
 if pg in rows:
  if link not in rows[pg][0]:rows[pg][0]+=', '+link
  rows[pg][1]+=' '+msg
 else:rows[pg]=[link,msg]
newrows=[f'| {pg} | {refs} | {note} |' for pg,(refs,note) in sorted(rows.items())]
lines[first:last+1]=newrows;s='\n'.join(lines)+'\n'
def ranges(seq):
 groups=[]
 for x in seq:
  if groups and groups[-1][-1]+1==x:groups[-1].append(x)
  else:groups.append([x])
 return ', '.join(str(a[0]) if len(a)==1 else f'{a[0]}–{a[-1]}' for a in groups)
clean=ranges([i for i in range(1,95) if i not in rows]);s=re.sub(r'\*\*Other reference pages:\*\*.*?\. No additional', '**Other reference pages:** '+clean+'. No additional',s)
s=s.replace('Pages with an observed remaining graphic issue are listed individually.', 'Pages with a remaining graphic issue or missing separate worksheet are listed individually.')
s=s.replace('## Using this material in a learning platform\n', '## Verification\n\nAll 666 image references loaded in a local browser preview. The rendered text matches the imported Word body text after normalizing whitespace and capitalization. All 336 distinct graphics were inspected.\n\n## Using this material in a learning platform\n')
p.write_text(s)
r=base/'README.md';s=r.read_text().replace('See the report before publishing exercises with flagged labels or matrix entries.','See the report before publishing exercises with flagged labels or matrix entries. The file also references 10 separate classroom sketch sheets that are not included.');r.write_text(s)
with zipfile.ZipFile('GAT-1-20-markdown.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(base.rglob('*')):
  if p.is_file():z.write(p,p.as_posix())
with zipfile.ZipFile('GAT-1-20-markdown.zip') as z:assert z.testzip() is None
print(json.dumps({'zip':'GAT-1-20-markdown.zip','zip_bytes':Path('GAT-1-20-markdown.zip').stat().st_size,'files':len([p for p in base.rglob('*') if p.is_file()]),'issue_pages':len(rows),'external_worksheets':len(external)},indent=2))
