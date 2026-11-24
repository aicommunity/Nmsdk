"""Distill the retained corrected report for a new report with new content."""
from pathlib import Path
import sys,shutil,zipfile,json
from docx import Document
from docx.oxml.ns import qn
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import WORK,DELIVERY,sha,save

def main():
 source=DELIVERY/'ScientificComparisons.docx'
 folder=WORK/'template';folder.mkdir(parents=True,exist_ok=True);reference=folder/'Reference.docx'
 if not reference.exists():shutil.copy2(source,reference)
 assert sha(reference)==sha(source)
 doc=Document(reference);sections=[]
 for s in doc.sections:
  sections.append({k:getattr(s,k).cm if getattr(s,k) is not None else None for k in ['page_width','page_height','left_margin','right_margin','top_margin','bottom_margin','header_distance','footer_distance']})
 styles={}
 for name in ['Normal','Title','Heading 1','Caption']:
  s=doc.styles[name];p=s.paragraph_format
  styles[name]={'font':s.font.name,'size_pt':s.font.size.pt if s.font.size else None,'bold':s.font.bold,'italic':s.font.italic,'alignment':str(p.alignment),'line_spacing':p.line_spacing,'first_line_indent_cm':p.first_line_indent.cm if p.first_line_indent is not None else None,'space_before_pt':p.space_before.pt if p.space_before is not None else None,'space_after_pt':p.space_after.pt if p.space_after is not None else None}
 with zipfile.ZipFile(reference) as z:
  parts={n:{'length':len(z.read(n)),'sha256':__import__('hashlib').sha256(z.read(n)).hexdigest(),'classification':'editable' if n in ['word/document.xml','word/_rels/document.xml.rels','docProps/core.xml','[Content_Types].xml'] or n.startswith('word/media/') else 'preserve-only'} for n in z.namelist()}
 save(folder/'evidence.json',{'reference':str(source),'sha256':sha(source),'reference_pages':33,'sections':sections,'styles':styles,'parts':parts})
 text='# Contract for the new training reproducibility report\n\n'
 text+=f'Retained source: {source}\nSHA256: {sha(source)}\nLocal identical reference: {reference}\nReference 33 pages, {len(sections)} section(s). Prior full-page reference QA is reused because this hash is unchanged.\n\n'
 text+='The user requested the corrected report appearance, with near-GOST conventions, explained terms, axes and units. New content replaces the entire body; previous text, table data and figures are not content to preserve. Pagination is expected to change.\n\n'
 text+='Page system and paragraph roles (measured):\n\n'+json.dumps({'sections':sections,'styles':styles},ensure_ascii=False,indent=2)+'\n\n'
 text+='Slots: word/document.xml/w:body/* except final sectPr are editable. Reuse Title, Normal, Heading 1, Caption; clone the original figure/caption/table patterns as needed. Preserve the final section geometry, first-page footer policy, footer PAGE field, styles, numbering, theme, fonts and document settings. New report images may be added to media and document relationships. Document core properties may record the new report. No other source feature is intentionally changed.\n\n'
 text+='Tables: Times New Roman 12 pt, readable variable row height, repeated header, light gray D9D9D9 borders, sufficient padding. Figures: native chart exports from the new XLSX, centered at up to 16.5 cm with numbered caption below; keep figure with caption. Sparse data use large markers/dashed lines; dense traces use solid lines. All axes and units explicit.\n\n'
 text+='Gates: retained source hash unchanged; geometry and preserve-only package parts unchanged; all new pages rendered and inspected; exact hashes of embedded chart PNGs matched to Excel exports; formula/native chart QA passed. New content must distinguish history, prior frozen-state inference and actual new learning.\n'
 (folder/'artifact.md').write_text(text,encoding='utf8');print('Recorded reference style contract')
if __name__=='__main__':main()
