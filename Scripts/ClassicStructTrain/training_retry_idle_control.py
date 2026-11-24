"""Preserve a pre-observation acquisition failure and repeat its diagnostic."""
from pathlib import Path
import sys
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import WORK,load,save
from training_order_live import main

folder=WORK/'runs/FO/order-live/learner-22-live-r3'
meta=load(folder/'process.json');assert meta['status']=='idle_timeout' and meta.get('finished_utc')
assert not (folder/'results.jsonl').read_text(encoding='utf8').strip(),'A scientific observation must not be replaced by this technical retry'
target=WORK/'interrupted-diagnostics/FO-learner-22-live-r3-pre-observation-idle'
assert folder.resolve().is_relative_to(WORK.resolve()) and target.resolve().is_relative_to(WORK.resolve()) and not target.exists()
target.parent.mkdir(parents=True,exist_ok=True);folder.rename(target)
save(target/'retention.json',{'original_directory':str(folder),'reason':'No training or evaluation observation was produced before the independent 660-second supervisor idle limit. Preserved as a technical acquisition failure; repeat uses unchanged binary, inputs and scientific per-attempt limits.','utc':datetime.now(timezone.utc).isoformat()})
main('learner')
