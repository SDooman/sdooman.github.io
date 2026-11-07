"""Apply the explicit category decisions from inspection of all 111 non-OLE graphics."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
CATEGORIES={
 'network':[2],
 'annotated_matrix':[3,8,25],
 'dilation':[4,34,35,53,56,92],
 'geometry':[5,36,58,59,66,70,81,95,107,108,111,133,170,171,175,221,243,334,490,523,527],
 'shapes_symmetry':[90,103],
 'coordinate_plot':[49,60,75,91,101,104,105,115,129,132,141,149,157,164,176,189,196,244,254,259,283,336,357,375,377,399,403,444,482,517,528,543],
 'calculation_flow':[122,123,124,125,126,127,128,168,169,193,195,199,206,207,209,214,216,392,394,395,401,402,413,421,433,461],
 'table':[200,204,205,224,231,260,397,429,431,449,464,465,489,494,512,522],
 'screenshot':[430,450,453,462],
}
RASTER={133:'The water-fill texture contains two raster fragments; retain the original artwork.',
        175:'The flag/person illustration contains two raster fragments; retain the original artwork.',
        430:'Calculator scatterplot screenshot; source data are available in image429, but display scale and selected markers are not inferred.',
        450:'Calculator scatterplot/line screenshot; source data are in image449. A mathematical plot can be built later without imitating screen pixels.',
        453:'Calculator plot with vector annotations; screenshot retained and printed coordinate labels transcribed.',
        462:'Calculator results screen retained; visible text is transcribed.'}
NOTES={
101:['The printed A-prime and B-prime coordinate labels appear swapped relative to their drawn positions. Source labels are preserved.'],
123:['The source intentionally shows the false statement 3 + 2·4 = 10 while teaching non-solutions. It is preserved exactly.'],
129:['The negative sign in the A-prime coordinate is faint/raised; compare with image104 and the source.'],
199:['The source right-hand side is a raised negative 10; it is preserved.'],
259:['The source labels C=(2,5.07), alongside B=(1,2.54). This potential rounding/typing inconsistency is preserved.'],
}
def main():
    rows=json.loads((ROOT/'conversion-21-40/checkpoints/embedded-pdfs.json').read_text());mapping={}
    for category,ids in CATEGORIES.items():
        for n in ids:
            ident=f'image{n}';assert ident not in mapping;mapping[ident]=category
    expected={r['id'] for r in rows if not r['equation_object']};assert set(mapping)==expected,(expected-set(mapping),set(mapping)-expected)
    result=[]
    for row in rows:
        n=int(row['id'][5:]);notes=NOTES.get(n,[])[:]
        if n in RASTER:notes.append(RASTER[n])
        result.append({'id':row['id'],'source_sha256':row['pdf_sha256'],'category':'formula' if row['equation_object'] else mapping[row['id']],
                       'classification_review':'inspected','conversion_review':'needs_review','contains_raster':n in RASTER,'notes':notes})
    (ROOT/'conversion-21-40/visual-decisions.json').write_text(json.dumps({'version':1,'method':'Source graphics and question context visually inspected; native equation objects parsed separately.','assets':result},ensure_ascii=False,indent=2)+'\n')
    taxonomy=json.loads((ROOT/'visual-pipeline/taxonomy.json').read_text())
    if not any(x['id']=='dilation' for x in taxonomy['categories']):
        taxonomy['categories'].append({'id':'dilation','label':'Dilations and size transformations','target':'geometry-scene','review':'Preserve the stated centre and scale factor; distinguish given values from approximate drawing positions.'})
    (ROOT/'visual-pipeline/taxonomy.json').write_text(json.dumps(taxonomy,ensure_ascii=False,indent=2)+'\n')
    print({key:len(value) for key,value in CATEGORIES.items()})
if __name__=='__main__':main()
