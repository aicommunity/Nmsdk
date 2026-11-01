set -uo pipefail
cd "/home/user/timelearner-refactor/source-n0-combined-a3"
export TIMELEARNER_N0_REPEATS_DIR="/home/user/timelearner-refactor/readbacks/s07-n0-repeats-normal-a2/native"
export TIMELEARNER_FULL_PROBE_REPORT_DIR="/home/user/timelearner-refactor/readbacks/s09-n0-full-probe-reports-a1"
export TIMELEARNER_DOMAIN_EVIDENCE_DIR="/home/user/timelearner-refactor/readbacks/s07-domain-physics-normal-a1/native"
export TIMELEARNER_PROBE_PLOT_DIR="/home/user/timelearner-refactor/readbacks/s07-n0-combined-a3/figures"
export PYTHONDONTWRITEBYTECODE=1
"python3" -u - <<'PY' > "/home/user/timelearner-refactor/readbacks/s07-n0-combined-a3/python.log" 2>&1
import json,subprocess,unittest,xml.etree.ElementTree as ET
from pathlib import Path
out=Path("/home/user/timelearner-refactor/readbacks/s07-n0-combined-a3")
root="2b7267526c834484be12549f3614d3d967b4bc9b"
bin_sha="34a9e60d0b8e38522e1cce4d59378b6a9bda7844"
files=["ClDesc/PulseLibrary/ru-RU/"+name+".xml" for name in ("NNeuronTimeLearner","NNeuronTimeLearnerBranch")]
readbacks=[]
for name in files:
    content=subprocess.check_output(["git","-C","/home/user/timelearner-refactor/source-order-fixed-a1/Bin","show",bin_sha+":"+name])
    ET.fromstring(content)
    assert "search.n0_candidate_repeats" in content.decode("utf-8")
    (out/Path(name).name).write_bytes(content)
    readbacks.append(name)
import os,hashlib
native=Path(os.environ["TIMELEARNER_N0_REPEATS_DIR"])
summaries=list(native.glob("*_training_summary.json"))+list(native.glob("*_xml_summary.json"))
assert len(summaries)==8, "expected eight native summaries"
domain=next(iter(sorted(Path(os.environ["TIMELEARNER_DOMAIN_EVIDENCE_DIR"]).glob("*_domain_preview.json"))))
assert json.loads(domain.read_text())["kind"]=="native_resistance_domain_evidence"
(out/"input-provenance.json").write_text(json.dumps({"native_summary_count":8,"domain_file":str(domain),"domain_sha256":hashlib.sha256(domain.read_bytes()).hexdigest(),"native_input_root":"42d1b58803d6b2060bd8993b60f17c0d74577d5b","note":"domain evidence is from separate prior published physics control"},indent=2)+"\n")
modules=["test_n0_repeat_evidence","test_process_runner","test_publisher","test_condition","test_runtime","test_probe_reports","test_plotting","test_analysis_cli","test_full_probe_report_evidence"]
suite=unittest.defaultTestLoader.loadTestsFromNames(["Scripts.StructTrain.TimeLearner.tests."+m for m in modules])
result=unittest.TextTestRunner(verbosity=2).run(suite)
record={"kind":"timelearner_combined_n0_infrastructure_gate","schema_version":1,"root":root,"bin":bin_sha,"xml_readbacks":readbacks,"tests":result.testsRun,"skips":len(result.skipped),"failures":len(result.failures),"errors":len(result.errors),"modules":modules,"scientific_verdict":None,"scope":"Combined production Python paths and two ClassDesc readbacks; prior native A2 results reused without rerunning model"}
(out/"validation.json").write_text(json.dumps(record,indent=2)+"\n")
raise SystemExit(0 if result.wasSuccessful() and not result.skipped else 1)
PY
status=$?
printf '%s\n' "$status" > "/home/user/timelearner-refactor/readbacks/s07-n0-combined-a3/process-exit-status.txt"
exit "$status"
