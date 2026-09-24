"""Read-only comparison of metrics at original audit vs present checkout."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = next(p for p in Path(__file__).resolve().parents if (p / ".gitmodules").exists())
OUT = ROOT/"build/audit-review-20260924/analyzer"
OUT.mkdir(parents=True, exist_ok=True)
SCRIPTS = ROOT / 'Bin/Configs/SpikeSamples/StructTrain/scripts'

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

historical = subprocess.check_output([
    'git', '-c', f'safe.directory={ROOT.as_posix()}/Bin', '-C', str(ROOT/'Bin'),
    'show', 'd2361191bdcc582e82eb1071571d185f6b35c79f:Configs/SpikeSamples/StructTrain/scripts/selectivity_metrics.py'
])
(OUT/'selectivity_metrics_at_audit.py').write_bytes(historical)
old = load('historical_metrics', OUT/'selectivity_metrics_at_audit.py')
now = load('current_metrics', SCRIPTS/'selectivity_metrics.py')
sys.path.insert(0, str(SCRIPTS))
audit = load('current_inventory_metrics', SCRIPTS/'audit_structtrain.py')
target = {'target_class':'1','stim_count':'4','isi0':'0.01','isi1':'0.02','isi2':'0.03',
          'isi3':'','neuron_fired':'1','neuron_t_rel':'.06','late_fired':'0',
          'late_t_rel':'-1','match':'1','neuron_spike_count':'1','neuron_spike_times':'.06'}
foil = {**target,'target_class':'0','neuron_fired':'0','neuron_t_rel':'-1',
        'neuron_spike_count':'0','neuron_spike_times':''}
cases = {}
for name, changes in {
    'baseline': {},
    'fired_without_spike': {'neuron_spike_count':'0','neuron_spike_times':'','neuron_t_rel':'-1'},
    'nonfinite_time': {'neuron_spike_times':'nan'},
    'early_target_claimed_fired': {'neuron_t_rel':'.001','neuron_spike_times':'.001'},
    'missing_times_count_1': {'neuron_spike_times':'','neuron_t_rel':'-1'},
    'single_stim_valid_target': {'stim_count':'1','isi0':'','isi1':'','isi2':'',
                                'neuron_t_rel':'.001','neuron_spike_times':'.001'},
}.items():
    cases[name] = [{**target, **changes}] + [copy.deepcopy(foil) for _ in range(7)]
cases['hidden_foil_spikes'] = [copy.deepcopy(target)] + [
    {**foil,'neuron_spike_count':'1','neuron_spike_times':'.001'} for _ in range(7)]
report = {'inputs': cases, 'source_sha256': {
    'historical': hashlib.sha256(historical).hexdigest(),
    'current': hashlib.sha256((SCRIPTS/'selectivity_metrics.py').read_bytes()).hexdigest()
}, 'results': {}}
keys = ['ok_audit','ok_audit_legacy','schema_ok','acc_strict','fa_strict','response_quality']
for name, rows in cases.items():
    report['results'][name] = {}
    for version, module in [('at_audit', old), ('current', now)]:
        result = module.classify(rows)
        report['results'][name][version] = {k: result.get(k) for k in keys}
path = OUT/'metrics-historical-current.json'
path.write_text(json.dumps(report, indent=2), encoding='utf8')
counterexamples = {}
for name, rows in cases.items():
    result = now.classify(rows)
    counterexamples[name] = {k: result.get(k) for k in keys}
    counterexamples[name]['last_pulse_ok'] = audit.last_pulse_ok(rows)
(OUT/'metrics-counterexamples.json').write_text(
    json.dumps(counterexamples, indent=2), encoding='utf8')
print(json.dumps(report['results'], indent=2))
