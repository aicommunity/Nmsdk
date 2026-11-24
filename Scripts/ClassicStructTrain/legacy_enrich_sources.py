"""Attach all 270 archived warm-training references without new experiments."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from legacy_execute import ROOT,PLAN,CONFIG,OUT,save
def main():
    data=json.loads(PLAN.read_text(encoding='utf8'));e=json.loads((ROOT/'Reports/StructTrainClassic/_work/archive-evidence.json').read_text(encoding='utf8'))
    jobs=json.loads((CONFIG/'recovered-jobs.json').read_text(encoding='utf8'));lookup={(j['kind'],tuple(j['dendrites']),tuple(j['synapses'])):j for j in jobs}
    mapping=[r for r in json.loads((OUT/'recovered-mapping.json').read_text(encoding='utf8')) if not r['row'].startswith('W')]
    source=next(d['path'] for d in data['documents'] if d['path'].startswith('Эксперименты/') and d['path'].endswith('Протоколы экспериментов.xlsx'))
    for i,r in enumerate(e['warm'],1):
        job=lookup[('learner',tuple(r['dendrites']),tuple(r['synapses']))]
        sample=min(data['dataset'],key=lambda s:max(abs(x-y) for x,y in zip(s['pattern'],r['pattern'])))
        assert max(abs(x-y) for x,y in zip(sample['pattern'],r['pattern']))<.00006
        ident=f'W{i:04}';ref=f"{source}; {r['source']['sheet']}; строка {r['source']['row']}"
        data['restoration_rows'].append({'id':ident,'group':'warm_protocol','kind':'learner','label':r['case'],'target':sample['id'],
             'dendrites':r['dendrites'],'synapses':r['synapses'],'complete':True,'source':ref,'archived_iterations':r['iterations']})
        mapping.append({'row':ident,'job':job['id'],'source':ref,'target':sample['id'],'group':'warm_protocol','status':'constructed','completion_donors':[]})
    save(OUT/'execution-plan-data.json',data);save(OUT/'recovered-mapping.json',mapping)
    summary=json.loads((OUT/'recovery-summary.json').read_text(encoding='utf8'));summary.update(planned_source_rows=497,additional_warm_links=len(e['warm']),source_rows=len(mapping))
    save(OUT/'recovery-summary.json',summary);print('Added warm-source links',len(e['warm']),'; new physical states: 0')
if __name__=='__main__':main()
