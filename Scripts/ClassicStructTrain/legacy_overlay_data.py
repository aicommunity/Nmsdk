"""Build aligned plot data without time scaling or amplitude normalization."""
from pathlib import Path
import json,sys,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from legacy_execute import ROOT,OUT,save
def main():
    a=json.loads((OUT/'assessment.json').read_text(encoding='utf8'));curves=json.loads((OUT/'digitized-waves.json').read_text(encoding='utf8'));byid={c['id']:c for c in curves}
    overlays=[]
    for key,oldids,match,title in [('111',['H111NL','H111NT'],'-five111','Пример 111: архив обучения и фиксированные структуры'),
      ('129',['H129'],'-transition22to129','Переход 22→129: архив и фиксированные структуры'),('37',['H37'],'-transition22to37','Переход 22→37: архив и фиксированные структуры')]:
        records=[r for r in a['protocols'] if match in r['case'] and r['repeat']==1]
        series=[];native=[];statistics=[]
        for r in records:
            raw=[json.loads(s) for s in (ROOT/r['directory']/'waveforms.jsonl').read_text().splitlines() if s.strip()];period=-1;points=[]
            for p in raw:
                if p['tick']==0:period+=1
                points.append([p['time']+period*1334/2000,p['sum_soma']])
            label=('NL' if r['kind']=='learner' else 'NT')+str(r['job'].get('frozen_state_reference_id',111))+(' / порог 100' if r['job'].get('threshold_control') else ' / порог 0,0115')
            native.append((r,label,points))
            groups=[]
            for point in raw:
                if point['tick']==0:groups.append([])
                groups[-1].append(point['sum_soma'])
            statistics.append({'label':label,'case':r['case'],'first_peak':max(groups[0]),'last_peak':max(groups[-1]),'threshold_control':r['job'].get('threshold_control',False)})
        if not native:continue
        ref=next((p for r,label,p in native if r['kind']=='learner' and r['job'].get('threshold_control') and (key=='111' or r['job'].get('frozen_state_reference_id')==22)),native[0][2])
        reference_time=max((p for p in ref if p[0]<=.6),key=lambda p:p[1])[0]
        old_reference=byid[oldids[0]]['first_peak_time']
        for oldid in oldids:
            c=byid[oldid];series.append({'label':'Архив '+oldid,'x':[p['time']-old_reference for p in c['points']],'y':[p['potential'] for p in c['points']],'source':'digitized_learning'})
        for r,label,points in native:series.append({'label':label,'x':[p[0]-reference_time for p in points],'y':[p[1] for p in points],'source':r['case']})
        left=min(x for s in series for x in s['x']);right=max(x for s in series for x in s['x'])
        grid=np.arange(np.floor(left/.0005)*.0005,np.ceil(right/.0005)*.0005+.00025,.0005).round(9).tolist();values=[]
        for s in series:values.append(np.interp(grid,s['x'],s['y'],left=np.nan,right=np.nan))
        rows=[[x,*[None if not np.isfinite(v[i]) else float(v[i]) for v in values]] for i,x in enumerate(grid)]
        overlays.append({'id':'O'+key,'title':title,'headers':['Время от первого максимума, с',*[s['label'] for s in series]],'rows':rows,
            'reference_native_peak_time':reference_time,'reference_historical_peak_time':old_reference,
            'native_statistics':statistics,'historical_statistics':[{'id':oid,'first_peak':max(p['potential'] for p in byid[oid]['points'] if p['time']<=byid[oid]['points'][0]['time']+.6),
                'last_peak':max(p['potential'] for p in byid[oid]['points'] if p['time']>=byid[oid]['points'][-1]['time']-.6)} for oid in oldids],
            'alignment':'One constant origin shift for all native curves and one for the corresponding historical panel; no time stretching or amplitude fitting. Linear interpolation only for a uniform 0.0005 s plotting grid; raw samples retained.',
            'time_uncertainty_max':max(p['time_uncertainty'] for oid in oldids for p in byid[oid]['points']),
            'voltage_uncertainty_max':max(p['potential_uncertainty'] for oid in oldids for p in byid[oid]['points'])})
    save(OUT/'overlays.json',overlays);print('Built historical overlays',len(overlays))
if __name__=='__main__':main()
