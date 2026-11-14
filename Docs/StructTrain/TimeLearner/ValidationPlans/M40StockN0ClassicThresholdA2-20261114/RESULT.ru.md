# Classic N0 fixed-threshold A2: реальные native results

Production1/1 PASS, outer completed3273.8191498247907с, все процессы закрыты, operation_passed=true, heartbeat errors отсутствуют. Baseline100 реально повторён и побайтово совпал по waveform с исходным; predefined threshold0.012765548843211696 совпал с predecessor proposal. Candidate TP1/FP4/FN0/TN3, target0.503с после фактического последнего input0.49с. Все16 observations complete/valid, model/source graph frozen.

[Научный разбор](../../ClassicN0ThresholdScientificReport-20261114.ru.md), [literal result](completed/worker/tmp/threshold-study/result.json), [candidate manifest](completed/worker/tmp/threshold-study/runs/candidate/run-manifest.json), [evaluation](completed/worker/tmp/threshold-study/runs/candidate/native/evaluation.json), [unit](completed/worker/validation/result.json), [closure](completed/process/whole-group-closure.json), [integrity](integrity.json). Producer b562efa413665e557956a0b80cc4c5bb62075064; pack SHA256 b1f386711fb6c7053b8e271dbef597ba82990263fdfd67c374257e72dafa81a5.

training_completed=false, calibrated=false, independent_evaluation=false, scientific_verdict=null. Это оценка прежнего stopped state, без нового Train и без geometry fix; плохая разделимость остаётся научным результатом.
