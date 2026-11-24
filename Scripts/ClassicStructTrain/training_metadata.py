"""Clarify provenance without changing native observations."""
from pathlib import Path
from datetime import datetime,timezone
import sys,argparse
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import ROOT,WORK,SOURCE,BASE,load,save,sha

parser=argparse.ArgumentParser();parser.add_argument('--final',action='store_true');args=parser.parse_args()
source=SOURCE/'Эксперименты/Тестирование/Configs/relearning_1/input_data.txt';assert source.is_file()
vectors=[list(map(float,line.split())) for line in source.read_text().splitlines() if line.strip()]
assert vectors==[r['pattern'] for r in load(BASE)['warm_sequence']]
path=WORK/'warm-stimulus-provenance.json';data=load(path);correct=str(source.relative_to(ROOT)).replace('\\','/')
if data['historical_source']!=correct:
 data['source_path_before_correction']=data['historical_source'];data['source_path_correction']='Corrected metadata path to the actual archived Configs/relearning_1 file. Native stimulus values and observations were not changed.'
data.update(historical_source=correct,historical_source_sha256=sha(source),verified_vectors=len(vectors));save(path,data)
priority=WORK/'stale-controller-priority-correction.json'
if priority.exists():
 rows=load(priority)
 if isinstance(rows,dict):rows=[rows]
 for row in rows:row['origin_of_lower_priority']='Not independently established; the lower class and its correction were observed. No algorithmic effect is inferred from wall time alone.'
 save(priority,rows)
if args.final:
 assert load(WORK/'completion-audit.json')['passed']
 summary=load(WORK/'report-data.json')['summary']
 save(WORK/'progress.json',{'status':'completed','planned_study_date':'2026-11-23','finished_utc':datetime.now(timezone.utc).isoformat(),'coverage':load(WORK/'coverage-summary.json'),'results':summary,'remaining':[]})
 save(WORK/'active-sessions.json',{'status':'completed','native_processes_pending':0,'note':'Terminal results or concrete reasons verified from actual records; no study computation remains active.'})
print('Verified archived file stimuli and clarified operational metadata')
