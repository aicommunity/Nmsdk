"""Resolve the contents and inspect final rendered report pagination."""
from pathlib import Path
import sys,re,argparse
from pypdf import PdfReader
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import WORK,load,save

parser=argparse.ArgumentParser();parser.add_argument('--pdf',type=Path,required=True);args=parser.parse_args()
headings=load(WORK/'report-headings.json');pages=PdfReader(args.pdf).pages;toc={};summary=[]
norm=lambda text:re.sub(r'\s+',' ',text).strip()
for index,page in enumerate(pages,1):
 text=page.extract_text();compact=norm(text)
 if index>2:
  for h in headings:
   if norm(h) in compact and h not in toc:toc[h]=index
 summary.append({'page':index,'words':len(text.split()),'start':compact[:120],'end':compact[-120:]})
assert set(toc)==set(headings),'Every content entry needs an actual rendered heading'
save(WORK/'report-toc.json',toc);save(WORK/'report-pagination.json',summary)
print({'pages':len(pages),'sparse_pages':[p for p in summary if p['words']<20],'contents':toc})
