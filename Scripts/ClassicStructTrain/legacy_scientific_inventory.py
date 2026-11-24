"""Anchor comparisons to the actual scientific figures and their plotted caches."""
from pathlib import Path
import copy,json,re,sys,zipfile,xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parent))
from legacy_execute import ROOT,OUT,CONFIG,save
N={'c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def col(n):
    s=''
    while n:n,k=divmod(n-1,26);s=chr(65+k)+s
    return s

def main():
    data=load(OUT/'execution-plan-data.json');evidence=load(ROOT/'Reports/StructTrainClassic/archive-evidence.json')
    book=ROOT/'Docs/ClassicStructTrainExperiments/Эксперименты/Исследование/Обучение нескольким примерам.xlsx'
    charts=[]
    with zipfile.ZipFile(book) as archive:
        for member in archive.namelist():
            if not re.fullmatch(r'xl/charts/chart\d+\.xml',member):continue
            root=ET.fromstring(archive.read(member));series=[]
            for node in root.findall('.//c:ser',N):
                ref=node.find('c:val/c:numRef/c:f',N)
                values={int(p.get('idx')):float(p.findtext('c:v',namespaces=N)) for p in node.findall('c:val/c:numRef/c:numCache/c:pt',N)}
                series.append({'formula':ref.text if ref is not None else None,'cache':values})
            charts.append({'member':member,'series':series})
    sources={}
    for record in data['source_chart_renders']:
        if record['doc']!='D146':continue
        formula=record['series'][0]['formula']
        # SERIES wrapper contains the same worksheet range as c:numRef/c:f.
        match=next((c for c in charts if any(s['formula'] and s['formula'] in formula for s in c['series'])),None)
        if not match:raise ValueError('No XML cache for '+record['id'])
        source=copy.deepcopy(record);source['xml_member']=match['member'];source['cached_series']=match['series'];sources[record['id']]=source
    recovered=load(CONFIG/'recovered-jobs.json');protocols=load(CONFIG/'protocol-jobs.json')
    lookup={(j['kind'],tuple(j['dendrites']),tuple(j['synapses'])):j for j in recovered}
    extra=[];points={};conflicts=[]
    refs=load(OUT/'protocol-references.json')
    for source_id,sheet_name in [('E019','Схема 0 на 1(2)+4'),('E020','Схема 0 на 1+4(верн. синапсы)')]:
        source=sources[source_id];sheet=evidence['research_sheets'][sheet_name]
        val=lambda address:sheet.get(address,{}).get('value')
        cache=source['cached_series'][0]['cache'];cache={int(k):v for k,v in cache.items()}
        result=[]
        for index,old_plot in sorted(cache.items()):
            state=index+1
            reference=next((r for r in refs if r['sheet']==sheet_name and r['state']==state),None)
            if source_id=='E019':
                cell=col(index+2)+'32';input_ids=list(range(41,61))+list(range(101,111))
                # The seventh scientific point has aggregate TP and a complete
                # structural output header, although its binary column is incomplete.
                source_file=ROOT/'Docs/ClassicStructTrainExperiments/Эксперименты/Исследование/0 на 1(2)+4'/f'output_data{index}.txt'
                vector=list(map(int,source_file.read_text(encoding='utf-8-sig').splitlines()[0].split()[:10]))
                base=lookup.get(('learner',tuple(vector[:5]),tuple(vector[5:])))
                if not base:raise ValueError('Scientific point lacks recovered state: '+str(vector))
                job=next((j for j in protocols if j['id'].startswith(base['id']+'-') and j.get('input_ids')==input_ids),None)
                if job is None:
                    job=copy.deepcopy(base);job.update(id=base['id']+'-science-subset30',input_ids=input_ids,target_id=51,target_class=2,
                        trace=False,roundtrip=False,scientific_source=source_id,scientific_state=state)
                    extra.append(job)
                job_id=job['id'];d,s=vector[:5],vector[5:]
            else:
                if reference is None:raise ValueError('Missing full historical state '+str(state))
                cell='L'+str(15+index);input_ids=reference['input_ids'];job_id=reference['job'];d=reference['dendrites'];s=reference['synapses']
            binary_tp=None
            if reference is not None:binary_tp=sum(v for ident,v in zip(reference['input_ids'],reference['answers']) if 51<=ident<=100)
            row={'state':state,'old_plot':old_plot,'old_cell':val(cell),'old_cell_address':cell,'old_binary_tp':binary_tp,
                 'job':job_id,'input_ids':input_ids,'dendrites':d,'synapses':s,'source_file':str(source_file.relative_to(ROOT)) if source_id=='E019' else None}
            result.append(row)
            if old_plot!=val(cell) or (binary_tp is not None and old_plot!=binary_tp):conflicts.append({'source':source_id,**row})
        points[source_id]=result
    save(OUT/'scientific-source-charts.json',sources);save(OUT/'scientific-source-points.json',points)
    save(OUT/'scientific-source-conflicts.json',conflicts);save(CONFIG/'scientific-jobs.json',extra)
    summary={'scientific_sources':list(sources),'E019_points':len(points['E019']),'E020_points':len(points['E020']),
             'new_protocols':[j['id'] for j in extra],'source_conflicts':len(conflicts)}
    save(OUT/'scientific-inventory-summary.json',summary);print(json.dumps(summary,ensure_ascii=False))
if __name__=='__main__':main()
