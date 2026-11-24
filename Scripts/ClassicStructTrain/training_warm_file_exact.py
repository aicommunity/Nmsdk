"""Historical text stimuli, including the initial input; keep earlier controls intact."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import WORK,save,run_jobs,load
from training_protocols import warm_job

job=warm_job()
save(WORK/'warm-stimulus-provenance.json',{'authoritative_phase':'warm-file-exact','preserved_control_phase':'warm','job':job,
 'distinction':'Archive text has four decimal digits; XLSX tables retain full precision. Earlier warm control used full-precision initial input 22 and rounded following file inputs. The authoritative file series also uses rounded first input. Old native observations are retained unchanged.',
 'historical_source':'Docs/ClassicStructTrainExperiments/Эксперименты/Тестирование/Configs/relearning_1/input_data.txt'})
run_jobs('VP1',[job],'warm-file-exact',2)
save(WORK/'warm-file-exact-completion.json',{'completed':True,'real_independent_attempts':3,'directed_transitions_per_repeat':90})
