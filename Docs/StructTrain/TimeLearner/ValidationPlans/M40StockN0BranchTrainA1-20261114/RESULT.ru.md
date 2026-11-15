# Branch N0: Ns применялся, поиск завершился по времени

M40 s11-stock-n0-branch-train-m40-a1: production1/1 PASS2615.052с, outer completed/closed2637.7270542038605с, heartbeat errors0. Native process completed/closed2023.0980146862566с при исходном process limit2100с. Native search wall1800с и отдельный allowance300с на запуск/stop/export не менялись. [Test log](completed/worker/validation/unittest.log), [native process result](completed/worker/native-stock-n0-branch-train/Branch-stock-cold8-N0/runs/train/process/result.json), [whole-group closure](completed/process/whole-group-closure.json).

Научный исход budget_exhausted, reason native_training_time_budget_exhausted.42 измеренных candidates,9 timing-ready,0 jointly-ready;85 search probes,42 edits. Поиск работал только над input2 (третий закреплённый импульс). Ns действительно изменялся и измерялся в1..5, Rs оставался86M. Отказов наблюдения0; certificate=null, финальной all-input проверки нет. Это не PhysicalInfeasible и не доказательство недостижимости амплитуды для всех геометрий.

[Полный run index/DATA audit](completed/worker/native-stock-n0-branch-train/Branch-stock-cold8-N0/index.json), [оригинальный summary](completed/worker/native-stock-n0-branch-train/Branch-stock-cold8-N0/runs/train/native/train_stopped_summary.json), [actual native job](completed/worker/native-stock-n0-branch-train/Branch-stock-cold8-N0/runs/train/native/job.json). Сохранены89 logical groups/534 native trials/1922934 frames. Последняя полная anchor-группа search127/group89 не потреблена контроллером как candidate measurement; её нельзя добавлять в42 измеренных кандидата или считать сертификатом.

## Реально измеренный амплитудный поиск

|search|L0,L1,L2,L3|Ns2|amp residual|timing residual, s|
|---|---|---:|---:|---:|
|74|25,25,25,1|1|-0.0118549032499361|-0.014999999999986358|
|77|26,26,25,1|2|-0.00784092940896286|-0.015500000000088221|
|80|26,26,25,1|3|-0.0037754954250721617|-0.015499999999974534|
|83|26,26,25,1|1|-0.0118549032499361|-0.015000000000100044|
|86|26,26,25,1|4|0.0003079757232195002|-0.015499999999974534|
|89|26,26,25,1|5|0.004379160993298603|-0.015499999999974534|
|92|26,26,26,1|1|-0.011918946239878103|-0.0060000000000854925|
|95|27,27,27,1|1|-0.01197860573669629|0.0029999999999290594|
|98|28,28,28,1|1|-0.012034232941276701|0.012000000000057298|

При L=[26,26,25,1] соседние Ns3 и4 дали противоположные амплитудные остатки, оба вне1e-5. Ближайший из этих измеренных counts —4: residual+0.0003079757232195002, timing−0.015499999999974534с. Нецелое Ns между3/4 не является допустимым решением; интерполяция не выдаёт Exact. Первая Ns1 точка L=[25,25,25,1] имеет другой upstream bank, чем повтор Ns1/search83 при L=[26,26,25,1]; смешивать их как одну физическую scope нельзя.

При длинах26,27,28 зарегистрированы timing-ready точки с Ns1, но не новые Ns2..5. Проверка production BoundedTraining.cpp показывает конкретную причину: enqueue N0 neighbors требует improved относительно **общего best по всем геометриям**. Уже найденная Ns4/L25 имеет гораздо меньший нормированный амплитудный остаток, поэтому Ns1 следующей длины не улучшает global best и не запускает локальную нормализацию. Это ограничение порядка поиска, не ошибка формулы residual и не обоснование повышения tolerance/budget. [Постановка правки](../../N0GeometryNormalizationReview-20261114.ru.md) требует отдельного bounded per-geometry локального поиска и same-budget A/B; в этом исходном опыте код не менялся.

Terminal L=[38,38,38,1], Ns=[1,1,1,1], Rs=86M. Reported model revision87be6dbf500ff125fec276415e8f140b3c6e13d13fc83c5f6eeb5b99287b26b7. Это **другая модель**, чем локальный Ns4/L25 кандидат. Frozen Test использует actual terminal export; лучшие промежуточные parameters не подставляются скрытым overlay. Классификация этого N0-состояния пока не оценивалась.

Физика stock без LTMembrane,2000Гц;39 membranes/78 channels проверены, threshold и feedback connections сохранены. CapturedPerInput/anchorN−1, ampabs1e-5/relative0/min1e-6/sync.02; probes128/edits1280/candidates128/input/sweeps4/invalid4. [Постановка](../../StockNormalizationControl.ru.md). Python source69e985df6654ac64cc34571e6862119cf26b90c5, controlae2ae412f5bb8c267828202b9a92982378e6337a; прежний native SDK root74e5d206d4b619fcf81f77f11b54ebec7b8f0f6e/Pulse7c6c94785af0c83104d348bb3b733ed1f149c8a8, runtime105ccc46bf2d23aa093ee6ec5fb088d9f33faa8e572f8191869f8cc279377a8a.

Producer69f7d12d00201c4ae866dce48d8bf11a05ff3047, pack219969B SHA25641b5804e0256962f80622a4a6413515880a4f5264b4300dd966478eae19a0c68;33 raw Git blobs импортированы без JSON rewrite. [Весь primary собран](../M40StockN0BranchPrimaryA1-20261114/RESULT.ru.md); собственные временные графики N0 ещё ожидаются. Порог не подбирался, научный PASS из completed процесса не выводится; августовские визуальные4/8–6/8 сохраняют свой протокол.
