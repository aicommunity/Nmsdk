"""Evaluate measured legacy inference and static graph preservation."""
from pathlib import Path
import json,sys,re,xml.etree.ElementTree as ET,collections,math,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parent))
from legacy_execute import ROOT,PLAN,CONFIG,OUT,save
from legacy_recover import physical,fingerprint

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def records(p):return [json.loads(line) for line in p.read_text(encoding='utf8').splitlines() if line.strip()]
def metrics(answers,ids,target):
    c={'TP':0,'FP':0,'FN':0,'TN':0}
    for answer,ident in zip(answers,ids):c[('TP' if answer else 'FN') if (ident-1)//50+1==target else ('FP' if answer else 'TN')]+=1
    tp,fp,fn,tn=(c[k] for k in ['TP','FP','FN','TN']);n=tp+fp+fn+tn
    return {**c,'precision':tp/(tp+fp) if tp+fp else None,'recall':tp/(tp+fn) if tp+fn else None,'accuracy':(tp+tn)/n if n else None,
            'balanced_accuracy':.5*(tp/(tp+fn)+tn/(tn+fp)) if tp+fn and tn+fp else None,'Q':fp+fn,'risk':(fp+fn)/n if n else None}
def graph_comparison(before,after):
    a=physical(ET.parse(before).getroot());b=physical(ET.parse(after).getroot())
    source_nodes=set(a['nodes']);result_nodes=set(b['nodes'])
    changes=[]
    for path,entry in a['nodes'].items():
        if path not in b['nodes']:continue
        other=b['nodes'][path]
        if entry['class']!=other['class']:changes.append([path,'class',entry['class'],other['class']])
        for key,value in entry['parameters'].items():
            if other['parameters'].get(key)!=value:changes.append([path,key,value,other['parameters'].get(key)])
    lost_links=sorted(set(map(tuple,a['links']))-set(map(tuple,b['links'])))
    new_links=sorted(set(map(tuple,b['links']))-set(map(tuple,a['links'])))
    return {'passed':not(changes or source_nodes!=result_nodes or lost_links or new_links),'nodes_before':len(source_nodes),'nodes_after':len(result_nodes),
            'lost_nodes':sorted(source_nodes-result_nodes),'new_nodes':sorted(result_nodes-source_nodes),'changed_parameters':changes,
            'lost_links':lost_links,'new_links':new_links,'links_before':len(a['links']),'links_after':len(b['links'])}

def collect(stage):
    result=[]
    for folder in sorted((OUT/stage).glob('*')):
        if not (folder/'process.json').exists():continue
        process=load(folder/'process.json')
        if process['status']!='completed':continue
        for r in records(folder/'results.jsonl'):
            job=r['job'];r['directory']=str(folder.relative_to(ROOT));r['process']=process
            r['metrics']=metrics(r['answers'],r['input_ids'],job['target_class'])
            source=ROOT/job['config'].replace('project.ini','Model_00.xml')
            paths=[source,folder/'loaded/Model_00.xml',folder/'after/Model_00.xml']
            if (folder/'roundtrip-loaded/Model_00.xml').exists():paths.append(folder/'roundtrip-loaded/Model_00.xml')
            signature={'version':3,'hashes':[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]}
            cache_file=folder/'assessment-graph.json';cached=load(cache_file) if cache_file.exists() else {}
            if cached.get('signature')!=signature:
                cached={'signature':signature,'graph_loading':graph_comparison(paths[0],paths[1]),'graph_inference':graph_comparison(paths[1],paths[2])}
                if len(paths)>3:cached['graph_roundtrip']=graph_comparison(paths[2],paths[3])
                save(cache_file,cached)
            for field in ['graph_loading','graph_inference','graph_roundtrip']:
                if field in cached:r[field]=cached[field]
            r['physically_ready']=r['loaded_readback']['consistent'] and r['loaded_readback']['all_initialized']
            result.append(r)
    return result

def main():
    data=load(PLAN);saved=collect('saved-b');recovered=collect('recovered-b');protocols=collect('protocols-a');context=collect('context-a');scientific=collect('scientific-extra')
    first={r['case']:r for r in saved+recovered if r['repeat']==1 and len(r['answers'])==150}
    # Reused measurements share the full physical configuration and protocol.
    reused=load(OUT/'recovered-reused.json') if (OUT/'recovered-reused.json').exists() else []
    for link in reused:
        if link['measured_job'] not in first:continue
        original=first[link['measured_job']];first[link['recovered_job']]=original
    repeat_checks=[]
    for case in sorted({r['case'] for r in saved+recovered+context}):
        rs=sorted([r for r in saved+recovered+context if r['case']==case],key=lambda r:r['repeat'])
        if len(rs)<2:continue
        repeat_checks.append({'case':case,'same_answers':rs[0]['answers']==rs[1]['answers'],'same_peaks':rs[0]['peaks']==rs[1]['peaks'],
                              'same_structure':rs[0]['readback_after']==rs[1]['readback_after']})
    mapping=load(OUT/'recovered-mapping.json') if (OUT/'recovered-mapping.json').exists() else []
    by_row={m['row']:m for m in mapping};row_records={r['id']:r for r in data['restoration_rows']}
    comparisons=[]
    # Canonical response columns are matched only by original kind, target ID,
    # and documented structure; 110/132 never become 111/134.
    evidence=load(ROOT/'Reports/StructTrainClassic/_work/archive-evidence.json')
    canonical=load(ROOT/'Bin/Configs/StructTrainClassic/Prepared/manifest.json')['recognition_models']
    for index,ref in enumerate(evidence['recognition']):
        model=canonical[index]
        assert model['kind']==ref['kind'] and model['id']==ref['id']
        candidates=[r for r in data['restoration_rows'] if r['complete'] and r['kind']==ref['kind'] and r['dendrites']==model['dendrites'] and r['synapses']==model['synapses']]
        groups={by_row[r['id']]['job'] for r in candidates if r['id'] in by_row and 'job' in by_row[r['id']]}
        for key in sorted(groups):
            if key not in first:continue
            measured=first[key];ids=measured['input_ids']
            mismatch=[i for i,a,b in zip(ids,ref['answers'],measured['answers']) if a!=b]
            comparisons.append({'reference':ref,'job':key,'measured_job':measured['case'],'mismatch_ids':mismatch,
                                'canonical_structure':model,'canonical_selection':'pre-existing prepared manifest, fixed before this execution; explicit bracketed variants respected',
                                'archived_metrics':metrics(ref['answers'],ids,(ref['id']-1)//50+1),
                                'measured_metrics':metrics(measured['answers'],ids,(ref['id']-1)//50+1)})
    saved_comparisons=[]
    for r in saved:
        if r['repeat']!=1 or len(r['answers'])!=150:continue
        refs=[(x,canonical[i]) for i,x in enumerate(evidence['recognition']) if x['kind']=='trainer' and x['id']==r['job']['target_id']]
        refs=[(x,c) for x,c in refs if not (v:=re.search(r'\((\d+)\)',str(x['variant']))) or r['dendrites'][2]==int(v[1])]
        saved_comparisons.append({'case':r['case'],'target_id':r['job']['target_id'],'metrics':r['metrics'],
            'references':[{'range':x['source_range'],'variant':x['variant'],'metrics':metrics(x['answers'],r['input_ids'],r['job']['target_class']),
                           'canonical_structure_matches':r['dendrites']==c['dendrites'] and r['synapses']==c['synapses'],
                           'mismatch_ids':[i for i,a,b in zip(r['input_ids'],x['answers'],r['answers']) if a!=b]} for x,c in refs]})
    epochs=[]
    for epoch in data['epochs']:
        rows=[m for m in mapping if m.get('group')=='epoch_1plus4' and m.get('epoch')==epoch['epoch']]
        if not rows or rows[0]['job'] not in first:continue
        measured=first[rows[0]['job']]
        epochs.append({'epoch':epoch['epoch'],'job':rows[0]['job'],'archived':epoch,
                       'measured':metrics(measured['answers'],measured['input_ids'],2)})
    baselines=[]
    for base in data['baselines']:
        candidates=[m for m in mapping if m.get('group')=='baseline' and str(m.get('target'))==str(base['label'])]
        if candidates and candidates[0]['job'] in first:
            measured=first[candidates[0]['job']];baselines.append({'label':base['label'],'job':candidates[0]['job'],'archived':base,
                 'measured':metrics(measured['answers'],measured['input_ids'],2)})
    protocol_first={r['case']:r for r in protocols if r['repeat']==1}
    protocol_comparisons=[]
    if (OUT/'protocol-references.json').exists():
        for reference in load(OUT/'protocol-references.json'):
            measured=first.get(reference['job']) if len(reference['input_ids'])==150 else protocol_first.get(reference['job'])
            if measured is None:continue
            protocol_comparisons.append({'reference':reference,'measured_metrics':metrics(measured['answers'],reference['input_ids'],2),
                'archived_metrics':metrics(reference['answers'],reference['input_ids'],2),
                'mismatch_ids':[i for i,x,y in zip(reference['input_ids'],reference['answers'],measured['answers']) if x!=y]})
    reset_checks=[];reload_checks=[];third_checks=[];precision_checks=[];own_checks=[]
    for r in protocols:
        if r['case'].endswith('-independent'):
            other=protocol_first.get(r['case'].removesuffix('-independent')+'-continuous-control6')
            if other:reset_checks.append({'base':r['case'].removesuffix('-independent'),'answer_differences':sum(x!=y for x,y in zip(r['answers'],other['answers'])),
                'max_peak_difference':max(abs(x-y) for x,y in zip(r['peaks'],other['peaks'])),'independent':r['case'],'continuous':other['case']})
        if r['case'].endswith('-reloadfirst'):
            base=first.get(r['job']['comparison_original'])
            if base:reload_checks.append({'base':base['case'],'same_answer':base['answers'][0]==r['answers'][0],
                'same_peak':base['peaks'][0]==r['peaks'][0],'graph':r['graph_loading']['passed'] and r['graph_inference']['passed']})
        if r['case'].endswith('-third'):
            base=first.get(r['job']['comparison_original'])
            if base:third_checks.append({'base':base['case'],'same_answers':base['answers']==r['answers'],'same_peaks':base['peaks']==r['peaks']})
        if r['case'].endswith('-rounded4'):
            base=first.get(r['case'].removesuffix('-rounded4'))
            if base:precision_checks.append({'base':base['case'],'answer_differences':sum(x!=y for x,y in zip(base['answers'],r['answers'])),
                                            'full_metrics':base['metrics'],'rounded_metrics':r['metrics']})
        if r['job'].get('own_pattern_source')=='literal':
            other=protocol_first.get(r['case'].removesuffix('-literal')+'-dataset')
            if other:own_checks.append({'base':r['job']['comparison_original'],'target':r['job']['target_id'],'literal_answer':r['answers'][0],
                 'dataset_fresh_answer':other['answers'][0],'literal_peak':r['peaks'][0],'dataset_fresh_peak':other['peaks'][0]})
    assembly=[r for r in protocols if r['job'].get('equivalence_control')]
    assembly_check=None
    if len(assembly)==2:
        assembly_check={'same_answers':assembly[0]['answers']==assembly[1]['answers'],'same_peaks':assembly[0]['peaks']==assembly[1]['peaks'],
                        'same_graph':all(r['graph_loading']['passed'] and r['graph_inference']['passed'] for r in assembly),'cases':[r['case'] for r in assembly]}
    context_comparisons=[]
    standalone=first.get('M018-preserved')
    driven=next((r for r in context if r['case']=='M018-parent-driven' and r['repeat']==1),None)
    fullcontext=next((r for r in context if r['case']=='M018-full-context' and r['repeat']==1),None)
    sampled_auto=next((r for r in context if r['case']=='M018-autonomous-context12'),None)
    sampled_drive=next((r for r in context if r['case']=='M018-parent-driven-context12'),None)
    for x,y,label in [(standalone,driven,'autonomous_vs_parent_driven_150'),(sampled_auto,sampled_drive,'autonomous_vs_parent_driven_12'),(sampled_drive,fullcontext,'parent_driven_vs_full_context_12')]:
        if x and y:
            assert x['input_ids']==y['input_ids'],'Context comparison must use identical ordered inputs'
            context_comparisons.append({'comparison':label,'input_count':len(x['answers']),'answer_differences':sum(a!=b for a,b in zip(x['answers'],y['answers'])),
                'max_peak_difference':max(abs(a-b) for a,b in zip(x['peaks'],y['peaks']))})
    output={'saved':saved,'recovered':recovered,'protocols':protocols,'context':context,'scientific_extra':scientific,'reused':reused,'repeat_checks':repeat_checks,
            'recognition_comparisons':comparisons,'saved_comparisons':saved_comparisons,'epochs':epochs,'baselines':baselines,
            'protocol_comparisons':protocol_comparisons,'reset_checks':reset_checks,'reload_checks':reload_checks,'third_checks':third_checks,
            'precision_checks':precision_checks,'own_checks':own_checks,'assembly_check':assembly_check,'context_comparisons':context_comparisons,
            'first_by_job':{k:{'case':r['case'],'directory':r['directory'],'answers':r['answers'],'input_ids':r['input_ids'],'job':r['job'],'metrics':r['metrics']} for k,r in first.items()}}
    output['summary']={'saved_processes':len(saved),'recovered_processes':len(recovered),'valid_saved_states':sum(r['repeat']==1 and len(r['answers'])==150 for r in saved),
        'graph_load_failures':[r['case'] for r in saved+recovered+protocols+context+scientific if not r['graph_loading']['passed']],
        'graph_inference_failures':[r['case'] for r in saved+recovered+protocols+context+scientific if not r['graph_inference']['passed']],
        'graph_roundtrip_failures':[r['case'] for r in saved+recovered+protocols+context if 'graph_roundtrip' in r and not r['graph_roundtrip']['passed']],
        'roundtrip_answer_failures':[r['case'] for r in saved+recovered+protocols+context if r.get('roundtrip_same_first_answer') is False or r.get('roundtrip_same_first_peak') is False],
        'repeat_differences':[c for c in repeat_checks if not c['same_answers'] or not c['same_peaks'] or not c['same_structure']],
        'recognition_comparisons':len(comparisons),'epochs':len(epochs),'baselines':len(baselines)}
    save(OUT/'assessment.json',output);print(json.dumps(output['summary'],ensure_ascii=False))
if __name__=='__main__':main()
