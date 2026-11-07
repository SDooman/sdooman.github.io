"""Source-inspected category decisions, independent of conversion representation."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[2]
# The default covers coordinate-plane drawings inspected on the contact sheets.
# Every exception is explicit; formula membership comes from native records or
# the separately reviewed transcription mapping, never filename heuristics.
GROUPS={
 '41-58':{
 'formula':'11 12 13 26 27 28 30 78 79 80 81 82 92 93 94 95 96 211 219',
 'table':'109 110 260 276 278 284 297 300 313',
 'calculation_flow':'9 265 280','annotated_matrix':'312',
 'screenshot':'35 36 66 69 73 74 75 76',
 'geometry':'163 183 201 240 253 271 272 281 282 309',
 'rotation':'124 166 175 182 203 206 215 220 221 237 255 310 321',
 'reflection_translation':'210 224','shapes_symmetry':'199 238 239 256 257',
 'dilation':'131 259 267 270 302 308','network':'261 277'},
 '59-80':{
 'formula':'57 150 202 235 248 256',
 'table':'4 17 18 24 29 42 54',
 'screenshot':'23 32','geometry':'13 51 71 201 218 223 225 229 240 246',
 'reflection_translation':'30 203','shapes_symmetry':'209 219 224',
 'calculation_flow':'78 267 330 331','annotated_matrix':'94 96 98',
 'illustration':'236'},
 '81-100':{
 'formula':'39 147 149 160 161 162 196 197 203 204 214 215 216 217 218 219 220 221 222 238 239 240 241 242 243 244 245 256 257 258 259 260 261 262 263 264 265 285 286 293 296 298 316 321 322 323 325 326 327 328 329 337 386 419 420 421',
 'calculation_flow':'13 15 16 65 66 67 68 110 111 150 151 174 177 234 330 363 423',
 'annotated_matrix':'345 481 482 483','table':'371 388 397',
 'screenshot':'152 170 172 178 180 189 228 248 354 355 403',
 'rotation':'76','geometry':'306 334 335 369 387 402 409 416 432 435 447 454 465 467 494 495',
 'map':'434 444 445 446 460','network':'489'},
 '101-119':{
 'formula':'23 37 39 72 105 193 196 197','table':'271 278',
 'annotated_matrix':'16 19 89','network':'1 15 20 90',
 'calculation_flow':'96 100 147 148 149 168 169 170 194 231',
 'geometry':'6 7 9 25 29 45 52 57 75 78 86 95 249 250 256 266',
 'reflection_translation':'143 162 178 179 189 276 281','dilation':'259 260 269 270 272 299',
 'map':'63 87 242','shapes_symmetry':'24',
 'screenshot':'123 124 142 198 229 244 264 280 291 298','illustration':'209'}
}
NOTES={
 '41-58':{203:'Curved labels in the legacy preview have gaps; compare the preserved PICT before relying on these labels.'},
 '59-80':{196:'Some ordinary letters in this legacy preview render as Symbol glyphs. The original PICT is preserved; its labels need correction before publication.',78:'Small legacy formula labels need review; the complete vector layout is retained.'},
 '81-100':{127:'Some formula labels render with legacy Symbol-font substitutions; original artwork is retained.',177:'One embedded formula is extremely small in the legacy drawing preview. Its native equation is exposed separately for review.',442:'Several ordinary letters render as Symbol glyphs in the legacy preview; original artwork is retained.'},'101-119':{}
}
for batch,ids in {'41-58':'272 282','59-80':'13 232 240 241 274 275 290','101-119':'24 143 261 276 277 281 282'}.items():
 for n in ids.split():NOTES[batch][int(n)]='Some formula labels are small in the legacy preview and need layout review. Available native equations are exposed separately.'
def main():
 batch=sys.argv[1];check=ROOT/f'conversion-batches/checkpoints/{batch}';book=ROOT/f'gat-{batch}'
 assets=json.loads((check/'assets.json').read_text());formulas={r['id'] for r in json.loads((book/'formula-transcriptions.json').read_text())['assets']};byid={r['id']:r for r in assets};groups=GROUPS[batch];assigned={}
 for cat,ids in groups.items():
  for n in ids.split():
   key='image'+n;assert key in byid and key not in assigned,(batch,key);assigned[key]=cat
 decisions=[]
 for r in assets:
  ident=r['id'];category='formula' if ident in formulas else assigned.get(ident,'coordinate_plot');notes=[]
  if r.get('contains_raster') and category not in ('formula','table'):notes.append('Contains original raster artwork; retained as an image. Vector conversion is incomplete.')
  if int(ident[5:]) in NOTES[batch]:notes.append(NOTES[batch][int(ident[5:])])
  decisions.append({'id':ident,'category':category,'contains_raster':r.get('contains_raster',False),'original_sha256':r['sha256'],'status':'candidate','review':'needs_review','notes':notes})
 (check/'visual-decisions.json').write_text(json.dumps({'version':1,'assets':decisions},ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
