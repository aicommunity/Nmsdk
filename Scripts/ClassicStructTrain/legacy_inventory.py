"""Inventory original saved models, historical figures and recoverable snapshots."""
from __future__ import annotations
from collections import Counter
import hashlib
import json
import logging
import math
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET
from zipfile import ZipFile

from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader
logging.getLogger("pypdf").setLevel(logging.ERROR)

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Docs/ClassicStructTrainExperiments"
WORK = ROOT / "Reports/StructTrainClassic/_work/LegacyInferencePlan-20261123/work"
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
      "c": "http://schemas.openxmlformats.org/drawingml/2006/chart"}
FIGURE = re.compile(r"^\s*(?:Рис(?:унок|унки|\.)|Fig(?:ure|\.)?|Table|Таблица)\s*\d", re.I)
NUMBER = re.compile(r"[-+]?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?")


def save(name, data):
    (WORK / name).write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def text(node):
    return " ".join(t.text or "" for t in node.findall(".//w:t", NS)).strip()


def numbers(value):
    try:
        return [float(x) for x in (value or "").split()]
    except ValueError:
        return []


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "assets").mkdir(exist_ok=True)
    docs, assets, charts, captions, snapshots, models = [], {}, [], [], [], []
    hashes = {}
    for path in sorted(SOURCE.rglob("*")):
        if not path.is_file():
            continue
        relative = str(path.relative_to(SOURCE)).replace("\\", "/")
        sha = digest(path.read_bytes())
        ident = f"D{len(docs)+1:03}"
        doc = {"id": ident, "path": relative, "sha256": sha, "bytes": path.stat().st_size,
               "extension": path.suffix.lower(), "role": "theory" if "Теоретическая проработка/" in relative else "local",
               "duplicate_of": hashes.get(sha), "captions": [], "assets": [], "text": ""}
        hashes.setdefault(sha, ident)
        docs.append(doc)
        if path.suffix.lower() in (".docx", ".pptx", ".xlsx"):
            with ZipFile(path) as z:
                if path.suffix.lower() == ".docx":
                    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("word/_rels/document.xml.rels"))}
                    tree = ET.fromstring(z.read("word/document.xml"))
                    paragraphs = list(tree.findall(".//w:p", NS))
                    texts = [text(p) for p in paragraphs]
                    doc["text"] = "\n".join(texts)
                    for i, (p, value) in enumerate(zip(paragraphs, texts), 1):
                        if FIGURE.search(value):
                            doc["captions"].append({"location": f"paragraph {i}", "text": value})
                        rids = [n.get("{"+NS["r"]+"}embed") for n in p.findall(".//a:blip", NS)]
                        rids += [n.get("{"+NS["r"]+"}id") for n in p.findall(".//{urn:schemas-microsoft-com:vml}imagedata")]
                        for rid in rids:
                            target = rels.get(rid, "")
                            if not target or "media/" not in target:
                                continue
                            member = "word/" + target.replace("../", "")
                            blob = z.read(member)
                            aid = digest(blob)[:16]
                            asset = assets.setdefault(aid, {"id": aid, "extension": Path(member).suffix.lower(), "contexts": []})
                            out = WORK / "assets" / (aid + asset["extension"])
                            if not out.exists(): out.write_bytes(blob)
                            asset["contexts"].append({"doc": ident, "location": f"paragraph {i}", "context": " | ".join(texts[max(0,i-3):i+3])[:1600]})
                            doc["assets"].append(aid)
                elif path.suffix.lower() == ".pptx":
                    slides = sorted([n for n in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)], key=lambda n:int(re.search(r"(\d+)\.xml",n)[1]))
                    slide_texts=[]
                    for slide in slides:
                        i=int(re.search(r"(\d+)\.xml",slide)[1]); tree=ET.fromstring(z.read(slide))
                        value=" ".join(n.text or "" for n in tree.findall(".//a:t",NS))
                        slide_texts.append(f"SLIDE {i}: {value}")
                        doc["captions"].append({"location":f"slide {i}","text":value[:1800]})
                        relfile=f"ppt/slides/_rels/slide{i}.xml.rels"
                        rels={r.get("Id"):r.get("Target") for r in ET.fromstring(z.read(relfile))} if relfile in z.namelist() else {}
                        for blip in tree.findall(".//a:blip",NS):
                            target=rels.get(blip.get("{"+NS["r"]+"}embed"),"")
                            if "media/" not in target: continue
                            member="ppt/"+target.replace("../",""); blob=z.read(member); aid=digest(blob)[:16]
                            asset=assets.setdefault(aid,{"id":aid,"extension":Path(member).suffix.lower(),"contexts":[]})
                            out=WORK/"assets"/(aid+asset["extension"])
                            if not out.exists(): out.write_bytes(blob)
                            asset["contexts"].append({"doc":ident,"location":f"slide {i}","context":value[:1600]})
                            doc["assets"].append(aid)
                    doc["text"]="\n".join(slide_texts)
                for member in sorted(n for n in z.namelist() if re.search(r"/charts/chart\d+\.xml$",n)):
                    tree=ET.fromstring(z.read(member)); series=[]
                    for s in tree.findall(".//c:ser",NS):
                        def cache(tags):
                            for tag in tags:
                                n=s.find("c:"+tag,NS)
                                if n is None: continue
                                pts=n.findall(".//c:pt",NS)
                                if not pts: continue
                                total=n.find(".//c:ptCount",NS)
                                count=int(total.get("val")) if total is not None else max(int(p.get("idx")) for p in pts)+1
                                values=[None]*count
                                for p in pts:
                                    i=int(p.get("idx")); v=p.findtext("c:v",None,NS)
                                    if i<len(values): values[i]=v
                                return values
                            return []
                        series.append({"formulas":[n.text for n in s.findall(".//c:f",NS)],
                                       "values":cache(["val","yVal"]),
                                       "categories":cache(["cat","xVal"]),
                                       "name":" ".join(n.text or "" for n in s.findall("c:tx//c:v",NS))})
                    chart={"id":f"C{len(charts)+1:03}","doc":ident,"member":member,
                           "title":" ".join(n.text or "" for n in tree.findall("c:chart/c:title//a:t",NS)),
                           "axis_titles":[" ".join(n.text or "" for n in title.findall(".//a:t",NS)) for title in tree.findall(".//c:plotArea/*/c:title",NS)],
                           "types":[n.tag.split('}')[-1] for n in tree.iter() if n.tag.endswith('Chart')],"series":series}
                    charts.append(chart)
                doc["native_chart_count"]=sum(c["doc"]==ident for c in charts)
        elif path.suffix.lower()==".pdf":
            reader=PdfReader(path); doc["pages"]=len(reader.pages)
            if doc["role"]=="local":
                pages=[]
                for i,page in enumerate(reader.pages,1):
                    value=page.extract_text() or ""; pages.append(value)
                    for line in value.splitlines():
                        if FIGURE.search(line): doc["captions"].append({"location":f"page {i}","text":line})
                doc["text"]="\n".join(f"PAGE {i}\n{t}" for i,t in enumerate(pages,1))
            else:
                doc["text"]="\n".join((p.extract_text() or "") for p in list(reader.pages)[:2])[:4000]
        elif path.suffix.lower() in (".png", ".svg"):
            aid=sha[:16]; asset=assets.setdefault(aid,{"id":aid,"extension":path.suffix.lower(),"contexts":[]})
            dest=WORK/"assets"/(aid+path.suffix.lower())
            if not dest.exists(): shutil.copy2(path,dest)
            asset["contexts"].append({"doc":ident,"location":"standalone","context":relative})
            doc["assets"].append(aid)
        elif path.suffix.lower()==".txt":
            doc["text"]=path.read_text(encoding="utf-8-sig",errors="replace")
            if path.name.lower().startswith("output_data"):
                lines=doc["text"].splitlines()
                warm = "relearning_" in relative
                for i,line in enumerate(lines if warm else lines[:15]):
                    vs=numbers(line)
                    if len(vs)>=10 and all(v.is_integer() and 0<v<10000 for v in vs[:10]):
                        answers = [int(numbers(x)[0]) for x in lines[i+1:] if not warm and len(numbers(x))==1 and numbers(x)[0] in (0,1)]
                        snapshots.append({"id":f"S{len(snapshots)+1:03}","doc":ident,"path":relative,"line":i+1,
                                          "dendrites":[int(v) for v in vs[:5]],"synapses":[int(v) for v in vs[5:]],
                                          "answers":answers,"answer_count":len(answers),"kind":"warm_transition" if warm else "recognition_snapshot",
                                          "header_extra_fields":vs[10:] if not warm else [],
                                          "extra_columns":vs[10:] if warm else [],
                                          "remaining_lines":len([x for x in lines[i+1:] if x.strip()]),"tail":lines[-3:]})
                        snapshots[-1]["synapses"]=[int(v) for v in vs[5:10]]
                        if not warm: break
        for cap in doc["captions"]: captions.append({"doc":ident,**cap})

    evidence=json.loads((ROOT/"Reports/StructTrainClassic/_work/archive-evidence.json").read_text(encoding="utf-8"))
    def walk(node, prefix, active, project):
        cls=node.get("Class",""); path=prefix
        ps=node.find("Parameters"); params={p.tag:" ".join(p.itertext()).strip() for p in ps} if ps is not None else {}
        active=active and params.get("Activity","1")!="0"
        if cls in ("NNeuronLearner","NNeuronTrainer"):
            neuron=next((c for c in node.findall("Components/*") if c.tag=="Neuron"),None)
            dend=[0]*5; syn=[0]*5; synact=[0]*5; resist=[]
            if neuron is not None:
                for part in neuron.findall("Components/*"):
                    match=re.fullmatch(r"Dendrite(\d+)_(\d+)",part.tag)
                    if not match: continue
                    k,j=map(int,match.groups())
                    if k>5 or j<dend[k-1]: continue
                    dend[k-1]=j
                    found=[s for s in part.findall("Components/*") if re.fullmatch(r"ExcSynapse\d+",s.tag)]
                    syn[k-1]=len(found); synact[k-1]=sum(s.findtext("Parameters/Activity","1")!="0" for s in found)
                    resist += [s.findtext("Parameters/Resistance","") for s in found]
            inp=numbers(params.get("InputPattern")); candidate=None; error=None
            if len(inp)==5 and all(math.isfinite(v) for v in inp):
                item=min(evidence["dataset"],key=lambda s:max(abs(a-b) for a,b in zip(s["pattern"],inp)))
                error=max(abs(a-b) for a,b in zip(item["pattern"],inp))
                if error<0.00006: candidate=item["id"]
            refs=[r for r in evidence["cold"] if r["kind"]==("learner" if cls=="NNeuronLearner" else "trainer") and r["dendrites"]==dend and r["synapses"]==syn]
            nps=neuron.find("Parameters") if neuron is not None else None
            nparams={p.tag:" ".join(p.itertext()).strip() for p in nps} if nps is not None else {}
            trained=numbers(nparams.get("TrainingPattern")); trained_id=None
            if len(trained)==5 and all(math.isfinite(v) for v in trained):
                item=min(evidence["dataset"],key=lambda s:max(abs(a-b) for a,b in zip(s["pattern"],trained)))
                if max(abs(a-b) for a,b in zip(item["pattern"],trained))<0.00006: trained_id=item["id"]
            declared_d=numbers(nparams.get("TrainingDendIndexes")); declared_s=numbers(nparams.get("TrainingSynapsisNum"))
            models.append({"id":f"M{len(models)+1:03}","project":project,"component":path,"class":cls,"effective_active":active,
                           "input_pattern":inp,"candidate_dataset_id":candidate,"pattern_max_error":error,
                           "saved_training_id":trained_id,"training_metadata_matches_graph":declared_d==dend and declared_s==syn and len(trained)==5,
                           "dendrites":dend,"synapses":syn,"active_terminal_synapses":synact,
                           "graph_complete":all(d>0 and s>0 for d,s in zip(dend,syn)),
                           "matching_cold_ids":sorted(set(r["id"] for r in refs)),
                           "parameters":params,"neuron_parameters":nparams,"terminal_resistances":sorted(set(resist)),
                           "source":"Model_00.xml","training_flag":params.get("IsNeedToTrain"),"calculate_mode":params.get("CalculateMode")})
        for child in node.findall("Components/*"):
            walk(child,path+"."+child.tag,active,project)
    config=SOURCE/"Эксперименты/Тестирование/Configs"
    for p in sorted(config.rglob("Model_00.xml")):
        model=ET.parse(p).getroot().find("Model")
        walk(model,"Model",True,p.parent.name)

    for asset in assets.values():
        path=WORK/"assets"/(asset["id"]+asset["extension"])
        try:
            with Image.open(path) as im:
                asset["width"],asset["height"]=im.size
                png=path.with_name(path.stem+"-preview.png")
                if not png.exists():
                    rgba=im.convert("RGBA")
                    Image.alpha_composite(Image.new("RGBA",rgba.size,"white"),rgba).convert("RGB").save(png)
                asset["preview"]=str(png)
        except Exception as ex: asset["preview_error"]=str(ex)
        asset["local"]=any(next(d for d in docs if d["id"]==c["doc"])["role"]=="local" for c in asset["contexts"])
    save("inventory.json",{"documents":docs,"assets":list(assets.values()),"charts":charts,"captions":captions,"snapshots":snapshots,"models":models})
    local=[a for a in assets.values() if a["local"] and a.get("preview")]
    font=ImageFont.truetype("C:/Windows/Fonts/arial.ttf",16)
    for page in range(0,len(local),12):
        sheet=Image.new("RGB",(1500,1200),"#eeeeee"); draw=ImageDraw.Draw(sheet)
        for k,asset in enumerate(local[page:page+12]):
            x=(k%3)*500; y=(k//3)*300
            with Image.open(asset["preview"]) as im:
                im=im.convert("RGB"); im.thumbnail((480,250)); sheet.paste(im,(x+10,y+28))
            context=asset["contexts"][0]
            draw.text((x+10,y+6),f"{asset['id'][:8]}  {context['doc']}  {context['location']}",fill="black",font=font)
        sheet.save(WORK/f"contact-{page//12+1:02}.png")
    print(json.dumps({"documents":len(docs),"primary_unique_documents":sum(d['role']=='local' and not d['duplicate_of'] for d in docs),
                      "assets":len(assets),"local_assets":len(local),"charts":len(charts),"snapshots":len(snapshots),"models":len(models)},ensure_ascii=False))


if __name__=="__main__": main()
