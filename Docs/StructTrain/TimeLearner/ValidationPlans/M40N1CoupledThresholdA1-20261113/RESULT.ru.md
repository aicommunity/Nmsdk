# Реальный fixed-threshold опыт: данные приняты, классификация плохая

M40 s07-n1-coupled-threshold-m40-a1: production1/1 PASS2379.098s, outer completed/closed2410.941907689s, heartbeat errors0. Native baseline100 completed/closed190.03793791122735s; native candidate completed/closed249.22456999728456s. Это приёмка выполнения и доказательств, не положительный scientific verdict.

| Условие | TP | FP | FN | TN | Ответившие foils |
|---|---:|---:|---:|---:|---:|
|Исходный порог100|0|0|1|7|0/7|
|Фиксированный0.03578062022182049|1|5|0|2|5/7|

Все16observations complete/valid, по4001sample в2s окне, reset-per-trial. Baseline replay побайтово совпал с исходными8 массивами samples/model_before. Модель frozen внутри каждого условия; между условиями изменён только заявленный диагностический порог. Source stopped-state SHA2568ab8e4d9bfbc935ff2e5b888e14f611397036869beb2a6188bc2790eb2a40b98,120430340B, остался неизменным.

Порог выбран до настоящего spiking candidate по finite правилу midpoint(target LT maximum, highest strictly lower foil LT maximum). Nonspiking margin−0.012079873648321415; proxyFP5 не подменяет фактические данные, даже при совпадении pattern counts. Настоящие события: target0.262; foil2:4.4965; foil4:8.256; foil5:10.497/10.74; foil6:12.2745/12.3115; foil7:14.675/14.712. Foils1/3 молчат. Из9events только1 относится к target. Target event на228ms раньше последнего actual input0.49s; whole-window TP не означает распознавания завершённой пачки.

Training остаётся invalid_observation/ambiguous, certificate=null; используется actual terminal state, без template fallback, warm retrain или изменения target. Нет calibration certificate или independent Test. Model revision baseline0612d586ce9b1403e5a57ee86703f87db2ea6c1a51d9bc798e38e997fa9dea60, candidate543d0d886a1181ea672eefe6d0aee1cf6a254129ee7e7c290452e50ad36e3f82: threshold входит в identity. Исторические августовские4/8–6/8 этим другим stopped-state опытом не отменяются.

[Actual result/metrics](result/result.json), [declared proposal](result/proposal.json), [test log](completed/worker/validation/unittest.log), [baseline manifest](result/runs/baseline100/run-manifest.json), [candidate manifest](result/runs/candidate/run-manifest.json). Source SDK root74e5d206d4b619fcf81f77f11b54ebec7b8f0f6e/Pulse7c6c94785af0c83104d348bb3b733ed1f149c8a8, runtime105ccc46bf2d23aa093ee6ec5fb088d9f33faa8e572f8191869f8cc279377a8a. Python controller/source563b21fb501f341da5453349d9ce1b0d80c33423, control143dd3956252ac8d8d821649b5403f0db0023e78.

Все826regular files+2aliases закрытого job упакованы collector92.162860682s; compact primary69.875324MB, SHA256ae966e7fdd8c507d240d1a73e54d9fff741828dc2d753af465fcf41c69e5600b. [Полный primary сохранён вGit](../M40N1CoupledThresholdPrimaryA1-20261114/RESULT.ru.md); [временной отчёт всех8patterns](../M40N1CoupledThresholdReportA1-20261114/RESULT.ru.md) принят1/1; все32 selected originals просмотрены и сохранены вGit. Full PNG/SVG/PDF cache остаётсяM40. Новый архив ещё не проходил independent restore.

Producer7542366dc10f91955990e54dd696c2d75d4decaf, pack131278B SHA2561375138ad4814df74e7e7a806c47435564809a930374cf70422d96fcc16710f0. Ни результат исходного обучения, ни математические допуски/бюджеты не менялись ради этих counts.
