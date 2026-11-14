# Независимый полный Classic cold4 replay принят

Elder-1 s11-classic-cold4-primary-replay-elder-a2: production1/1 PASS380.545с, outer completed/closed399.3964905147441с, heartbeat errors0. [Test log](completed/worker/validation/unittest.log), [controller](completed/controller-result.json), [whole-group closure](completed/process/whole-group-closure.json). Sourceea7d796e32c90003c51010769a860d6494544e1b, control4cbc2dd6d366775d8558fb4845ff095c02cb8c14.

Из Git восстановлен весь исходный Classic N1 cold4 primary29,285,000B, SHA256dd633d3743f082fdb524bb07ec6c0c92197a1eb1ffb3fa2b784316cc146fdd4e. Проверены910 logical members/589,944,520 expanded bytes, сохранены908 regular files. Два redundant glog aliases проверены на побайтовое равенство сохранённым целям и пропущены через явный dereferenced-glog-aliases-v1 adapter; исходная symlink topology не аттестуется.

Production analyze_search_history/audit_run_manifest прочитал исходные manifests без переписывания JSON/абсолютных путей. Исходный M40 native каталог на Elder отсутствует. Подтверждены Classic/N1/N4, invalid_observation/ambiguous,14 measured candidates/0 jointly-ready,5 отдельных recoveries на L54/52/50/48/45, отсутствие финальной all-input проверки и научного сертификата. Один реально извлечённый CSV повреждён, повторный production audit отверг его с pipeline_run_artifact_changed. Первичный архив/модель вGit не менялись.

[Полный proof и сохранённый search report](completed/worker/tmp/classic-cold4-primary-replay.json). Restore/analysis не являются новым нейронным исполнением: native_execution_attested=false, new_model_execution=false. Временный распакованный корпус удалён штатным TemporaryDirectory после проверки; исходный fixture-архив сохранён. Исходные14/0 и августовские4/8–6/8 не переоцениваются другими критериями.

[A1 отказал до теста по capacity preflight](unlaunched-a1/launch.log); [его request](unlaunched-a1/request.json) сохранён. A2 резервирует640MiB output вместо768MiB: известный корпус589,944,520B плюс81,144,120B запаса, прежний свободный floor1GiB сохранён. Это расчёт дисковой квоты reader, не изменение научных budgets. Перед A2 было1,773,699,072B свободно.

Producer88b18982273df8e9f27add09a9a31ed35e01754e, pack77556B SHA2561bb4cb39360594d75757e6ec83c9a96c0239ea7849e74cc6623e666d92da61b5;25 исходных Git blobs импортированы без JSON rewrite. [Научный отчёт](../../ClassicCoupledCold4ScientificReport-20261114.ru.md), [публикация primary](../M40N1CoupledClassicPrimaryA1-20261114/RESULT.ru.md). Полная матрица этапов2/3/5/11 остаётся открытой.
