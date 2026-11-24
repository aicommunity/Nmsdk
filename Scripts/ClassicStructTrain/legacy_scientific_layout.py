"""Resolve the report contents and flag pagination defects after rendering."""
from pathlib import Path
import json,re
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT/'Reports/StructTrainClassic/_work/LegacyChecks-20261123'
def norm(s):return re.sub(r'\s+',' ',s).strip()
def main():
 pages=PdfReader(WORK/'scientific-docx-gost-render/ScientificComparisons.pdf').pages
 headings=json.loads((WORK/'scientific-report-headings.json').read_text(encoding='utf8'))
 toc={};summary=[]
 for i,page in enumerate(pages,1):
  text=page.extract_text();compact=norm(text)
  if i>2:
   for h in headings:
    if norm(h) in compact and h not in toc:toc[h]=i
  summary.append({'page':i,'words':len(text.split()),'start':compact[:110],'end':compact[-110:]})
 missing=[h for h in headings if h not in toc]
 assert not missing,missing
 (WORK/'scientific-toc.json').write_text(json.dumps(toc,ensure_ascii=False,indent=2),encoding='utf8')
 (WORK/'scientific-pagination.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps({'pages':len(pages),'sparse_pages':[p for p in summary if p['words']<20],'contents':toc},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
