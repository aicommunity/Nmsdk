# Состояние рефакторинга на 31.10.2026

План 0–12 остаётся активным. Полностью принят этап 0; остальные этапы имеют
незакрытые требования. Это продолжение [снимка 30.10](CurrentStatus-2026-10-30.ru.md),
а не переоценка исторических результатов по новым критериям.

Текущий подэтап: отдельная физика weight probe threshold и свежие реакции
конечной модели. Source root 800ca40e / PulseLib 09f72c7: normal 20/20 native
(126.287 s), ASan 20/20 (834.511 s), без skips. Более поздний production source
6787071f / PulseLib 56707d7: по 5 codec и 10 reader checks на обоих workers.
Console cases и visual reports ещё проходят приёмку; proof пока не опубликован.
Первый normal Console supervisor=1 вызван ошибочным ожиданием отрицательного
Branch outcome в проверочном сценарии: сам Branch run valid/calibrated при
0.006293579947234118, на двух calibration patterns. Maintained validator
проверяет применение факторов/данные/A-B bytes, не предписывает научный исход.
Configured learner hooks/phase dispatch и обязательная полная матрица открыты.
[Подробности](NativePostTuneController.ru.md#результат-адресных-gates-3110-и-исправление-ожидаемого-исхода).

[Read-only сверка Elder Bin/M40](../../../Reports/StructTrain/TimeLearner/s02-elder-bin-inventory-20261031/README.md)
сохранена через Git (два gzip receipts, 90162 bytes), все hashes после merge
проверены. Missing-by-inventory не доказывает глобальной уникальности.
Исторические данные не переносились и не удалялись. На Elder отдельно очищен
воспроизводимый static-link cache старых неактивных runtime: 789 путей .a,
9.484 GB logical / около 3.05 GB реально освобождено; 224 executable hashes
не изменились. Это cache cleanup, не заявление о дублировании всех файлов.
Receipt пока находится в серверном readback и войдёт в compact proof.

Ранее проверенный подэтап: InterruptOwnerLifecycle отдельно прерывает PostTune/calibration
перед Reset/Default/teardown без доступа к owner и реентерабельного rollback.
Root ba33ee20 / PulseLib 979aea4: Elder normal завершён — 16/16 lifecycle cases
(69.737 s), 12/12 прежних fixed/codec regressions (68.354 s), 8/8 independent
reader checks (53.229 s), без skips. [Normal proof](../../../Reports/StructTrain/TimeLearner/s08-native-phase-lifecycle-interrupt-normal-a1/README.md):
146 members / 1536012 compressed bytes; все hashes проверены после merge.
Два полных portable source snapshots / 84 artifact entries сохранены.
Все 10 прежних fixed parent/roundtrip JSON побайтно совпали с original normal
proof; отдельная compatibility receipt опубликована.
[ASan proof](../../../Reports/StructTrain/TimeLearner/s08-native-phase-lifecycle-interrupt-asan-a1/README.md):
16/16 lifecycle cases (422.196 s), 12/12 regressions (409.622 s), 8/8 reader
(44.282 s), без skips; 149 members / 1554148 bytes. Leak detection выключен.
Все 10 прежних ASan fixed JSON также побайтно не изменились. Оба архива и полные
artifact inventories перепроверены после merge. Actual test executable/dependencies
дополнительно зафиксированы после тестов; это не pre-run/owned-process attestation
первоначальных native invocations, и Console manifest не заменяет test-binary identity.

[Visual proof](../../../Reports/StructTrain/TimeLearner/s08-native-phase-lifecycle-visual-normal-a1/README.md):
16 отчётов, 20 завершённых trial-soma реакций; partial/unobserved пробы остаются
диагностикой. После восстановления Git primary прошли 8 reader checks (47.353 s).
Полный cache M40 Data: 1055 files / 87879026 bytes; Git: 130 metadata members /
129076 compressed bytes и 8 выбранных PNG. Все hashes проверены; выбранные
PNG просмотрены в 1920×960, полный cache/PDF/SVG не принят.

Адресный bool-контракт uninitialized UContainer::Calculate проверен на
исправленном fixture root 0fca58516941184549fb08ea23fa973e2ebdd30c / Rdk
6084bfa703ebbe0d85d2a588dfe8f79c74cd1144: Elder normal 15/15 (8.373 s),
M40 ASan 15/15 (45.143 s), без skips. Исправление меняет только ранний bool;
пропуск children до Init, callbacks и штатный расчёт после Init сохранены.
Старый Rdk c903 на том же исправленном test (root f34067c6) воспроизвёл
ровно один assertion failure — false до Init. Process returncode=1 ожидаем
для отрицательного контроля и не является успешным model run.
Вызовы проведены через owned production process runner, actual test runtime
captured before/after, loaded files captured; full lifetime attestation не заявлена.
[Normal proof](../../../Reports/StructTrain/TimeLearner/s04-uninitialized-bool-fixed-normal-a3/README.md):
161 members / 740316 compressed bytes;
[ASan proof и отрицательный контроль](../../../Reports/StructTrain/TimeLearner/s04-uninitialized-bool-fixed-asan-a3/README.md):
181 members / 761828 bytes. Все archive/member hashes и inventories проверены
после --no-ff merge; в каждом proof два полных portable source snapshots /
84 artifact entries. Rdk develop merge 027f7f8353608f83b55f3857a2f6c39138df4c65
доступен в origin, точный root gitlink обновлён. Полный этап 4 не закрыт.
Первый fixture ошибочно включал Reset от Activity=false в интервал наблюдения;
его failed runs сохранены и не принимаются как passing evidence.
[Подробности и ограничения](Stage04-Progress.ru.md#уточнение-native-проверки-3110).

Configured learner hooks/phase dispatch пока не подключены. Нельзя объединять
AutoCalibrate, PostTrainMid и silent probe threshold в один флаг. У Branch
PostTune=false всё ещё входит в отдельную parallel-peak calibration phase,
даже при AutoCalibrate=false; это не готовый frozen-threshold протокол.
[Уточнённый контракт](CalibrationPropertyContracts.ru.md#дополнение-3110-api-и-независимые-владельцы-фаз)
сохраняет различия, важные также для интерпретации исторических результатов.

Проверен подэтап native PostTune с фиксированным порогом: PulseLib
`03d1ea86a0a9f0d7b861adb62bf7798a9c1a1c59`, normal source root
`3d922ba2c3e433b15bdbe5d008036ec0a5e3191f`, ASan source root
`38cd68a022814782eff667bedd60bdfe9a6950bc`. На Elder прошли 12/12 native
cases (67.946 s), на M40 — 12/12 (401.903 s): четыре codec cases и восемь
fixed-threshold controls для Classic/Branch, roundtrip, последующей отдельной
калибровки, budget/cancel/Reset. Leak detection выключен. В каждой сборке
два настоящих owned Console schema-1 A/B сохранили побайтно transaction и
конечную модель соответствующего исходного production bundle. Новые 9/9
reader/packaging checks проверяют реальные сохранённые данные; это не новые
независимые обучения и не полная матрица.

Выбор весов возвращает `weights_selected`, сохраняет порог и training outcome,
не создаёт threshold candidate или calibration proof. Silent target остаётся FN.
Raw `calibration_status=fixed` задаёт политику; при `recovery_required` derived
аудит возвращает `unverified`, поскольку восстановление live owner не доказано.
[Normal bundle](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-fixed-normal-a2/README.md):
134 members / 1158144 compressed bytes; [ASan bundle](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-fixed-asan-a1/README.md):
117 members / 1154916 bytes. Все archive/member hashes повторно проверены
после локального merge. Production fixed job добавлен позднее в 2d6ab1a0, его приёмка описана ниже.
Learner properties пока к fixed API не подключены. Оба optional-mode guards
сохраняются. Отдельный configured phase plan, безопасное продолжение и полная
mode/profile/frequency matrix остаются открытыми.

Исправлена ошибка упаковки normal fixed proof: глобальный фильтр каталога
`source` исключил 60 необходимых файлов `runs/*/input/source` из commit
`d447fc2eafa5461ffafecc37e8f11703f012b7eb`. Commit
`655af8a4ee7e132ef7754181398bd6b709cd9392` сохраняет все прежние 71 member
побайтно и добавляет потерянные primaries и repair receipts. Уникальные данные
не терялись, native simulation не перезапускалась. Новый production gate
`verify_packaged_run_closure` проверяет включённые run manifests, точное множество
их файлов и bytes/hashes; обе fixed упаковки содержат два portable snapshots /
84 artifact entries. Это integrity gate, не доказательство научной полноты.

Shared codec предыдущего подэтапа также проверен под ASan:
[109 members](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-codec-asan-a1/README.md),
3/3 native cases и два byte-exact owned Console A/B. Normal proof:
[103 members](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-codec-normal-a1/README.md).
Все 18 исходных job declarations и numeric bindings проверены. Отдельный
[ASan N0](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-controller-n0-asan-a1/README.md)
завершён: 2/2 native (3351.650 s), 12/12 reader (136.129 s), 220 members /
3604452 compressed bytes. [Normal N0](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-controller-n0-normal-a1/README.md):
2/2 native (459.529 s), 12/12 reader (157.913 s), 220 members / 3601844 bytes.
Оба N0 снимка: два входа, 2000 Гц, без приёмки остальных профилей и частот.

Fixed visual A3 завершена: 12 отчётов / 32 полные trial-soma реакции,
1530 cache files / 125632076 bytes на M40 Data. Все cache SHA256 проверены;
в Git сохранены 122 metadata members / 145084 compressed bytes и 12 PNG.
[Bundle](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-fixed-visual-normal-a3/README.md)
проверен после merge; все 12 PNG просмотрены в 1920×960. Обзор и первый zoom
содержат фактические входные импульсы, оси/легенды/потенциал читаются. Полный
cache, PDF/SVG и научный результат не приняты. Fixed roundtrip target остаётся FN;
последующая отдельная calibration дала Classic calibrated, Branch nonseparable.
A1 выявила неполную исходную упаковку до рендеринга; A2 не получила immutable
commit исправленного input в analysis clone; A3 fetch-ит оба commit явно.
10/10 evidence/plot checks прошли за 27.621 s; native rerun не выполнялся.

Production fixed job проверен на root 2d6ab1a059005af30bc3d55a78c2192e6cbd9813 /
PulseLib 4fecae12116e64534d84d0275e934b101b74cec6. В каждой сборке прошли
шесть настоящих owned Console operations: legacy, explicit v2 calibrate и fixed
для Classic/Branch. Fixed: оба weights_selected; calibration: Classic calibrated,
Branch search_unresolved. Legacy и explicit v2 calibrate сохранили transaction
и model bytes исходных normal/ASan корпусов. Это две topology fixtures, а не
полная матрица. Scientific verdict остаётся null.

[Normal proof](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-fixed-console-normal-a1/README.md):
3 preflight checks (7.200 s), 4 final worker checks (42.897 s), четыре реальных
некорректных Console jobs отклонены до создания native output. 317 members /
1535108 compressed bytes. [ASan proof](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-fixed-console-asan-a1/README.md):
3 preflight checks (5.996 s), 4 final worker checks (35.309 s), те же четыре
реальных отрицательных задания; 322 members / 1566548 bytes. Leak detection
выключен. Final worker suite включает повтор трёх preflight checks, а не четыре
дополнительных независимых теста. Новый shared design validator прошёл 4/4
legacy portable tests на всех 18 исходных runs (124.647 s) на M40.

Обе упаковки проверяют все шесть run snapshots и 252 artifact entries;
все member hashes повторно проверены после локального --no-ff merge.
Новый production fixed job не подключает learner-property phase dispatch:
оба optional-mode guards остаются. Настройка фаз, безопасное продолжение,
полная mode/profile/frequency matrix, единый ConditionSpec и полный publisher
остаются открытыми. Все шесть новых ASan run-bound reports построены:
62 полные trial-soma реакции, 2979 cache files / 304534961 bytes на M40 Data.
[Compact visual metadata](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-fixed-console-visual-asan-a1/README.md):
210 members / 674200 compressed bytes, все hashes проверены после merge.
Новые PNG в этот bundle не копировались; его полная ручная визуальная приёмка
ещё не получена. Ранее просмотренные 12 roundtrip PNG относятся к своим пробам
и не выдаются за проверку этих новых 62 реакций.

Новая команда `report --format posttune-run` (root `4c497f41d`) связывает
графики с production run manifest. Все 18 normal production reports завершены:
59 полных матриц, 178 trial-soma pairs, 8437 файлов в кэше M40 Data.
3 binding/coverage checks + 5 plotting checks прошли без skips (13.076 s).
Повтор на root `7e8d97f3f`, включая backend guard обоих PostTune entry points:
8/8, 12.419 s. [Compact bundle](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-console-visual-normal-a1/README.md)
содержит 422 metadata members / 335060 bytes и 12 PNG; все hashes проверены
после Git merge. Все 12 PNG просмотрены в 1920×960; полный cache, PDF/SVG и
научный результат этим не принимаются. У foil выбранная zoom-002 показывает
межимпульсный спад; импульсы видны на overview и других плитках полного кэша.

На Elder после проверки Git primary manifest, повторной проверки всех 907
архивных members на M40 и отсутствия активных читателей удалены только 214
побайтно совпадающих native cache files старого normal A2, 739918187 bytes.
[Receipt](../../../Reports/StructTrain/TimeLearner/s02-storage-dedup-elder-20261031-a1/README.md)
фиксирует рост free bytes с 406204416 до 1146679296. Архив Git и полная
копия M40 сохранены; уникальные primary data не удалялись. Новые объёмные
задания на Elder до дальнейшего освобождения места не запускать.

Затем новый N0 normal bundle восстановлен из Git на M40: 220 файлов /
604878849 bytes проверены дважды. После отдельной проверки source manifest
и отсутствия активных readers с Elder удалены ещё 206 дублирующих native
файлов / 604854174 bytes. Git archive, полная M40 copy и Elder terminal logs
сохранены. Free bytes выросли до 1745907712; новая квитанция включена в тот же
раздел duplicate-only cleanup. Это не разрешение удалять уникальные трассы.

Production publisher schema 2 проверен на настоящем visual bundle fd4f9f2b:
восемь репозиториев, сначала семь детей, потом корень, затем повторная проверка
remote refs. A1 проверял visual inventory; A2 — также исходный lossless primary
bundle. [Квитанции](../../../Reports/StructTrain/TimeLearner/s10-production-closure-publication-a1/README.md)
опубликованы тем же publisher в fb6baacd с тремя inventories (visual/primary/receipts).
Все 20 members receipt archive проверены после Git merge. Первоначальный push
visual producer был ручным: новая проверка идемпотентна и не означает миграцию
всех producers, ConditionSpec или scheduler. Этап 10 остаётся частичным.

## Отправная точка и незавершённая ветка

Принятый root develop: `8446ce2fc6775bb157cc4423665cba1319af228f`.
Gitlinks: PulseLib `086b04fb43bb57506558bfb6beba6250f61a6ce2`,
Bin `cbb3bf453d82f58672541ed8a42f7b5da54a5508`,
Rdk `c903b9bba4a31e604f9740ae6f6ed52a4e7de74a`.

Рабочая ветка `codex/timelearner-threshold-calibration` содержит native
candidate/proposal/assessment API, schema-2 наблюдения LTZone.Potential,
чтение raw observations, calibrated model export/import, независимый Python
proof audit, frozen scoring/report adapter и CLI анализа/select/confirm/run.
Она не объединена в develop: полная матрица режимов/частот/физик ещё не принята.
Есть проверенный isolated native calibration worker и scoped cold Train/export/evaluate; весь Train→Test pipeline
и PostTune controller этим автоматически не принимаются.

Новый контур: [NativePipelineWorker](NativePipelineWorker.ru.md). Текущая ветка
`codex/timelearner-native-posttune` продолжает TL-037 и содержит immutable
PostTune candidates. Старый ASan regression runtime остаётся закреплён на
e3fe5340 / PulseLib 39810a7; обновление его source/build разрешено только после
terminal 0. Новые кандидаты normal проверены отдельно на root 149a1af0 / PulseLib
de51a21. Ветка создана от develop с --no-ff merge сохранённых prerequisites.

## Ранний оперативный снимок 31.10 (история)

Статусы ожидания в этом и следующих хронологических разделах относятся к моменту
записи. Актуальные scoped results, полные SHA и ограничения находятся в начале
файла; ранние постановки сохраняются как журнал и не являются второй актуальной
спецификацией. Требования полного плана остаются обязательными.

Реализованное в коде отделено от runtime acceptance. Нижний журнал сохраняет
последовательность проверок: его ранние «ещё выполняется» относятся к моменту
конкретной записи и не заменяют эту сводку.

| Контур | Авторитетное состояние |
|---|---|
| Native PostTune measured controller | Root 44a1598a / PulseLib c8a1995: normal 10/10 native (501.475 s) и 19/19 independent (192.578 s), 24 actual parent transactions, пять Rs modes, три metric selections, real threshold confirmation, budget/cancel/foreign-trial controls. ASan A2 завершён: 10/10 native (3733.602 s), 19/19 original reader (158.845 s); strict-container reader e9f3cc852 на тех же ASan данных — 20/20 (159.205 s), без нового native запуска. ASan bundle опубликован в 89410878: 686 members / 7195636 bytes, все member hashes локально сверены; включает mechanical scope A/B и receipt раннего queued cancellation. Leak detection off; полная matrix, learner properties/continuation и production Console ASan ещё открыты. [Подробности и ограничения](NativePostTuneController.ru.md). |
| Отчёты нового PostTune-контроллера | M40 A1 остановился на пустом `{}` calibration; renderer исправлен. A2 прошёл 12 parent-reader checks, но неверное имя дополнительного модуля дало exit 1. Recovery A3 root e9f3cc852 завершён: 20/20 reader (174.978 s), 24 reports / 61 completed matrices / 184 trial-soma pairs, 4 новых + 5 plotting checks (20.592 s). Проверены hashes всех 8668 cache files. Bundle d94309d8 содержит 455 metadata members / 445980 bytes и 16 selected PNG; все members локально сверены, все 16 PNG просмотрены. Полный cache/PDF/SVG manual QA и новые Console waveforms не приняты. Sparse-index/HTTPS push failures сохранены, ни native, ни render при публикации не повторялись. |
| Production PostTune Console | Binary root ffd5b15a2 / Python 74f49a5f0: normal A2 завершён, 18 PostTune jobs (9 Calibrated / 7 SearchUnresolved / 2 BudgetExhausted), 6 calibration regressions, 2 дополнительных CLI jobs, 2 tick-stop и 4 native strict-parser controls. 4/4 PostTune checks (135.837 s), latest b884691c4 — 4/4 (136.718 s); 8/8 calibration worker checks (148.170 s). Отдельный provenance class первоначально пропущен без fixture; 4/4 восстановлены отдельно (19.011 s), без native rerun. Bundle 3c1751f9: 1146 members / 5936272 bytes, все локально сверены; полная Data M40 копия 962905002 bytes проверена. Первый A1 отвергнут loader guard до native старта. ASan Console отдельно собран и запущен на M40 (`s08-native-posttune-console-asan-a1`, supervisor 3504498). Learner property dispatch, continuation, N0/full matrix и новая visual acceptance остаются открытыми. |
| Общий recognition transaction scope | Механический root efb25123 / PulseLib fbf6b73: normal и ASan A/B фактически проходят по 2 grid + 8 ownership cases на каждом бинарнике и 4 independent checks на каждый ownership набор; 28 CSV pairs и 8 JSON exact. Первый A1 пропустил 8 cases и не принят как 10/10; отдельный recovery сохранён. Этот gate не подменяет испытание нового shared-scope PostTune/calibration handoff. |
| Научное поведение классификации | [Отдельная сводка](ClassificationResults-2026-10-31.ru.md): старый calibrated контроль Classic/Branch N1 даёт TP1/FP0/FN0/TN1 на одной паре; ранние 20 fixed-threshold PostTune evaluations — TP0/FP0/FN1/TN1 (молчание). Более новый измерительный controller/Console подтверждает калибровку той же пары в девяти controls; вклад структурного обучения не установлен при source Train=search_unresolved. Software PASS не означает восьмипаттерновую классификацию; robustness и независимая серия ещё не подтверждены. |
| Native PostTune candidates | [Typed immutable edits](NativePostTuneCandidates.ru.md): normal root 149a1af0 / PulseLib de51a21 — 5/5 native, 4/4 old conversion regressions, 8/8 independent checks; 20 candidates в пяти режимах, четыре paired native soma/input traces CanonRmin. A1 имеет три сохранённых ошибочных test expectations, исправление Core не требовалось. ASan 5/5 native (526.211 s), 4/4 regressions и 8/8 reader (26.405 s) прошли, все четыре CSV byte-identical normal; bundle b5f41edd: 264 files / 349112 bytes. Все 40 Console operations и 4/4 independent checks прошли (6870d987, 1814 files / 2974464 bytes). Двадцать frozen reports / 60 trial-soma pairs плюс 4 paired reports / 6 pairs опубликованы compact metadata и 18 selected PNG, все выбранные рисунки просмотрены; полная visual acceptance false. Измерительный driver уже реализован и проверен normal gate ниже; его расширенная приёмка, public V2 Train dispatch и continuation остаются открытыми. |
| Potential baseline, PulseLib 7f17735 | 16 native, 29 independent и отдельные 8 частично перекрывающихся checks прошли; compact bundles опубликованы. Это собственный снимок. |
| Raw validator/assessment, PulseLib 25cf6a5 | Normal 16/16 native и 35/35 independent прошли; 897 files / 8251508 bytes primary archive опубликован. Длительный ASan gate root ad975bbe теперь завершён: 16/16 native и reader 1ef44e2 — 35/35 (548.849 s), оба terminal 0. ASan primary опубликован в 7c1abb0: 899 файлов / 8251032 bytes; локально проверены все member hashes. Visual acceptance этого старого gate открыта. Этот старый снимок не подменяет full-matrix приёмку последующих signed/calibrated/worker версий. |
| Signed threshold, PulseLib 479084f | 6/6 native и 6/6 Python прошли на Elder; 425 files / 810680 bytes опубликованы. Полный normal 16/16 gate завершён. Его reader a1 обнаружил ошибку glob; исправленный reader a2 прошёл 35/35 на тех же данных без нового Train. Опубликован bundle e8305ced. Отдельный ASan 6/6 native + 6/6 Python завершён с exit 0; это не полный ASan 16-case matrix. |
| Persisted observations, PulseLib fece852 | Normal 2/2 Classic/Branch при 2000 Гц с roundtrip/corruption checks прошёл; данные включены в normal bundle 9746ea4. ASan 2/2 прошёл; первичные данные опубликованы в a4984f1. |
| Calibrated state, PulseLib 353882b → ce7e81e | Normal 2/2 прошли на обоих снимках. Усиленный ce7e81e проверил import/export/Reset/frozen probes и отказы при неправильных bindings. Данные и модели опубликованы commit 9746ea4; ASan 2/2 прошёл на обоих снимках, включая усиленный ce7e81e. ASan bundle a4984f1 опубликован. |
| Frozen scorer/report, root b22c15fec | 9/9 checks прошли на normal ce7e81e (55.393 s); прежние 5/5 и 9/9 не складываются как уникальные tests. 35/35 compatibility checks прошли на старых native данных 25cf6a5, отдельно от нового 16-case gate. ASan 9/9 прошёл на ce7e81e; данные опубликованы в a4984f1. Это тот же scoped набор, а не полная mode/profile matrix. |
| Полные calibrated reports, root ff432f559 | M40 построил Classic/Branch: 4 предъявления двух паттернов × все сомы, 12 trial/soma pairs, 164 PNG и SVG/PDF. 3 report + 5 plotting checks прошли на normal и ASan данных. Git содержит 12 выбранных PNG и метаданные; полный cache — M40. Четыре графика просмотрены вручную. |
| Native grid transaction, PulseLib dcc266a → c36e272 | Normal 2/2 прошли на обоих снимках, включая native commit, rollback/cancel и clock/frequency guards. Independent 17/17 (8 transaction + 9 calibrated regressions) прошли; bundle 2dc5825 опубликован. ASan 2/2 native + 17/17 checks прошли (350520ae); ASan reports 27/27 прошли (838c1963). Связка модели с полным grid через RunManifest и isolated CLI добавлены ниже; общий Train/export/evaluate pipeline остаётся открытым. |
| Владение калибровочной пробой, PulseLib b167d7a → fad7aed | Baseline: 0/6 воспроизвели три дефекта обоих learner. Исправленный root 0b89622 прошёл normal 8/8 (47.989 s) и ASan 8/8 (310.405 s), включая normal grid flow и удержание старого context token. Reader 322b118 прошёл 4/4 на каждом наборе (19.848 / 17.200 s). Lossless primary bundles опубликованы: normal 56b64713, ASan 5998cc72. Это scoped ownership acceptance; source training search_unresolved, production worker и полная матрица остаются открытыми. |
| Production calibration worker, PulseLib a5671e9 | Normal root 8aae62d и ASan root b103835 выполнили по шесть Console jobs Classic/Branch N1/2000 Hz: Calibrated, NonSeparable, BudgetExhausted для каждого owner. Portable reader 819f0d9 прошёл по 6/6 (137.657 / 201.645 s), включая два настоящих owned CLI run на worker. Более ранний reader 0d8494b прошёл перекрывающиеся 6/6 (100.727 / 172.595 s). Controls 29c15a6: 2/2 на worker; provenance/runtime 4244160: 11/11 на worker. Все первичные bundles опубликованы: normal d663fd43 + d879109a, ASan 1d248c88. Общий Train/export/evaluate scheduler и полный PostTune/mode/profile matrix остаются открытыми. |
| Production calibration visual reports, root 9c2fe4c | M40 проверил 437 Git-bundle members и построил 10 reports, 22 complete matrices, 66 trial/soma pairs. 19/19 checks прошли (16 provenance/runtime/plotting + 3 report). Metadata archive 98940 bytes, выбранные PNG опубликованы в 8636b892; ещё три input/rise tiles добавлены в b787779f без нового рендеринга. Все 11 selected PNG просмотрены в исходном размере; полная visual acceptance false. |
| Native cold Train/export/frozen evaluate, root d5ef1fa | Normal и ASan: по 4 случая / 12 native фаз, Classic/Branch × N0/N1 при 2000 Гц; все training outcomes search_unresolved, все complete frozen observations valid, модель неизменна. Normal primary опубликован (211 файлов / 371128 bytes). Owned CLI reader cfb09d3: 12/12 операций и portable audits; controls c8bb72b: 6/6 без skips (12.967 s), включая реальный one-tick incomplete Test. ASan CLI c8bb72b: те же 12/12. Owned bundles опубликованы: normal 8b4282f6 (633 файла / 758980 bytes), ASan 63a06e41 (794 / 1118296). Усиленные controls b839e879: 7/7 normal/ASan (18.248 / 45.504 s), включая остановленный cold Train и запрет его recognition export. All-pattern fixed evaluation reports 2eea76a: 4 матрицы / 12 пар, 5 plotting checks, 8 selected PNG просмотрены; полный cache на M40. Новые calibration-grid figures остаются открытыми; вся mode/profile/frequency matrix и этапы не приняты. |
| TL-037 legacy inference attempt, PulseLib 39810a7 | Baseline normal/ASan: шесть expected failures из восьми, включая false Success/mid=0.25 при непосещённом foil; две NaN controls прошли. Fixed normal root e3fe5340: 12/12 native (220.780 s), 5/5 primary audits (4.165 s), 4 physical free-runs Classic/Branch × 2000/20000 Гц. Bundle 37678c32: 156 файлов / 1080412 bytes, все hashes проверены. ASan 12/12 завершён (1555.310 s), stronger reader 6/6 (5.101 s); все четыре CSV byte-identical normal. Normal дополнительные 37/37 прошли (318.086 s), 6/6 peak-replay checks (5.867 s). Visual/render 11/11 + late peak 6/6, 11 selected PNG просмотрены; полный cache 8573 files на M40. Дополнительные 37 ASan regressions завершились: 37/37, 2120.226 s, terminal 0; bundle 61fde19b содержит 448 files / 779744 bytes, все member hashes локально проверены. Их полная waveform visual acceptance и весь этап 8 остаются открытыми. |
| develop | Новая calibration ветка не объединена. Только этап 0 принят целиком; весь план остаётся незавершённым. |

Дополнение: production Console ASan A1 завершился terminal 0 на M40:
18 PostTune и 6 прямых calibration jobs, дополнительные CLI/tick-stop/strict
controls; 4/4 PostTune reader (112.103 s), 8/8 calibration worker (234.799 s)
и 4/4 provenance (15.333 s), без skips. Source binary ffd5b15a2, Python 74f49a5f0.
ASan primary bundle опубликован в 88c47ddf: 1089 members / 6054552 bytes;
все member hashes локально сверены после Git transport.
Его producer применил production staging/helper и committed-blob verification;
финальный push root остаётся manual. Этот факт не закрывает waveform reports,
N0/profile/frequency/dimension matrix, learner dispatch или весь этап 8.

Начат следующий адресный gate N0: source fe45166a1, тот же реальный native
fixture, обе топологии, 2000 Гц, два входа, исходные физика/допуски. Elder
`s08-native-posttune-controller-n0-normal-a1`, supervisor 1623116. Это не новая
научная серия; до native/reader terminal outcomes N0-проверка не принята.

Исправление publication prerequsite: [schema 2 artifact closure](GitArtifactPublication.ru.md)
source 1113fd0fe прошёл 16/16 Git tests на каждом worker (Elder 4.560 s,
M40 12.811 s). Receipts ebf7a635 / 0e0dcc8b; проверяются committed bytes,
selected ignored/sparse files, явный push transport без изменения origin,
symlink/duplicate/traversal и исходные objects при git replace. Producers этих
receipts применили staging/verifier, но root push был manual. Полная миграция
всех producers и весь этап 10 остаются открытыми.

Хранение normal Console corpus: Git primary archive 3c1751f9 не изменён. Все
1146 members / 962905002 bytes восстановлены из Git и сверены на Data M40:
`/media/user/Data/TimeLearnerRefactor/readbacks/s08-native-posttune-console-offload-normal-a2/data`.
Затем на Elder удалены только 1031 byte-identical cache files / 923722340 bytes
из трёх завершённых result directories, с проверкой полного набора и открытых
читателей. Receipt опубликован в 41835674; уникальные primary не удалены.
Свободно стало 2.3 GiB вместо 1.4 GiB. Исходные absolute paths в frozen
process records сохраняют исторический смысл; portable reanalysis использует
новую Data M40 копию либо распаковку Git archive.

Production worker: [контракт и CLI](NativeCalibrationWorker.ru.md),
[normal primary](../../../Reports/StructTrain/TimeLearner/s08-calibration-worker-normal-a1/README.md),
[normal controls/runtime flags](../../../Reports/StructTrain/TimeLearner/s08-calibration-worker-controls-normal-a1/README.md),
[ASan primary](../../../Reports/StructTrain/TimeLearner/s08-calibration-worker-asan-a1/README.md),
[все временные графики и selected QA](../../../Reports/StructTrain/TimeLearner/s08-calibration-worker-report-normal-a1/README.md).
Архивы содержат соответственно 437 / 116 / 543 файла, занимают
2861700 / 190588 / 3073972 bytes. Raw observations, модели и исходные CSV
доступны в Git; полный PNG/SVG/PDF cache — на M40.

Normal/ASan подтвердили одинаковые physical revisions Classic
00d2a426b0686efba5da9ea5d2378d8008e5fb9b19dc1fb347bf9d2c4584ddd1 и Branch
c07c70fb7841e84a8968e95772c734856150d5eff5244c953f1bcd313e8f9893,
пороги и все полные fresh-confirmation observations. Это deterministic fixture
с двумя паттернами, не независимые retrains, не августовский replay и не Exact:
source Train сохраняет search_unresolved. Schema-1 model proof не содержит
весь grid; новая полная привязка проверяется через RunManifest/transaction.

Первая normal Console build попытка завершилась из-за отсутствующего include
публичных accessor declarations GetStorage/GetEnvironment; native тогда не
исполнялся. После исправления прошли шесть jobs. Normal provenance-a4 прошёл
11/11, затем metadata export остановился из-за выключенного compile database.
Экспорт включён после завершения jobs, без пересборки/повтора тестов, с проверкой
неизменных executable/app-ini hashes. Исходный exit 1 и recovery receipt сохранены.
Старые runtime manifests не подменены: RelWithDebInfo/linker flags и четыре
compile-unit rules записаны отдельно. ASan flags подтверждены actual compile
database; leak detection выключен. Поздний полный plugin census ещё не реализован.
Текущий PulseLib 0c6d057 добавляет только документацию поверх кода a5671e9.

Завершение отдельной длительной ASan серии подтверждено по terminal files,
четырём phase XML, native-validation.json и reader validation, а не по факту
исчезновения PID. Runtime fingerprint e9810faff355e1a92441328dc452a07d67b71453519a7379008b1e2ee4fc1315
относится к root ad975bbeb5df18555d94329d3ee95f321921c171 / PulseLib
25cf6a5bfadc0ee72182cb924f1d0730cf6dc71b. Native gate покрывает N1 potential
2000/20000 Hz, N0/N1 threshold candidates обеих топологий на обеих частотах,
fresh destination и recognition conversion controls. Старый source/build/runtime
сохранён; перед новым использованием этого каталога требуется публикация его
самостоятельного primary bundle. Современный worker acceptance выше имеет
другие root/PulseLib commits и собственные primary data.

Ownership bundles: [normal](../../../Reports/StructTrain/TimeLearner/s08-calibration-ownership-normal-a1/README.md)
и [ASan](../../../Reports/StructTrain/TimeLearner/s08-calibration-ownership-asan-a1/README.md).
Они хранят 249 / 236 файлов в сжатых архивах 1674164 / 1612044 bytes,
включая первичные source CSV/модели, raw observations, native XML/logs и runtime
receipts. На baseline все шесть controls действительно упали; старый reader-a1
с ошибкой обращения к duration не принят, исправленный reader-a2 проверял те
же native данные без повторного Train. ASan publisher сначала завершился 128
из-за отсутствия HTTPS credentials; тот же commit 5998cc72 затем опубликован
через настроенный Git SSH с проверкой remote SHA. Приняты именно native/reader
gates, а не первоначальный неуспешный publisher. Текущая правка PulseLib
0dc84fb — только документация поверх проверенного кода fad7aed.

[Ownership visual receipt](../../../Reports/StructTrain/TimeLearner/s08-calibration-ownership-report-normal-a2/README.md)
опубликован в fdcc9028; четыре выбранных PNG добавлены в 71e17496. M40 построил
шесть полных candidate/confirmation matrices: 18 trial/soma pairs; ещё три
complete externally consumed probe/soma pairs получили диагностические графики.
9/9 checks прошли (четыре ownership и пять plotting regressions), это повтор
частично перекрывающихся checks, а не девять новых независимых экспериментов.
Все графики имеют native input overlay, overview и 100-tick zoom без decimation;
полные PNG/SVG/PDF остаются cache на M40. Четыре selected overview просмотрены
в исходном размере: подписи, входы и пики читаемы. Полный visual acceptance false.
Первая попытка renderer использовала system Python без matplotlib; вторая
прошла проверки/рендеринг, но остановилась при git add вне sparse patterns.
Использованы существующий plotting-venv и адресный git add --sparse; отказы
и исходные runner/logs сохранены в harness-attempts.tar.xz. Прогоны native
и построение готовых графиков при исправлении публикации не повторялись.

Дополнительная проверка реализации `ce7e81e002c802412ce50c1f2b2f76ffa7215b2a`
(root `0f53ab4ec420b921f766cbd78a7fd10d248b8a86`) связывает proof не только
с model hash/frequency, но и с реальными soma bindings и LTZone path/class.
Неверный descriptor или лишние soma channels теперь отклоняются и native import,
и Python auditor. Для этой добавки a2 native 2/2 и reader 9/9 gates прошли на normal и ASan снимках; это не полная ASan матрица всех режимов.

[Syntax evidence](../../../Reports/StructTrain/TimeLearner/s08-calibrated-syntax-m40-a2/README.md)
содержит 22 metadata/log files в 7332-byte архиве, commit
`7e4a1f7002bb25846664d8fcdc5faa6f186fbf6f`. Первая попытка harness ошибочно
разместила private PulseLib вне Libraries/Nmsdk-PulseLib: 4 API units прошли,
2 learner units подхватили старые headers через relative includes. После
исправления layout все 6 прошли без изменения исходников. Это syntax-only,
без link/runtime/ASan acceptance. Первоначальный push по HTTPS завершился 128
из-за отсутствия credentials; тот же commit опубликован через Git SSH,
remote branch SHA проверен, исходный failure log сохранён.

Старая isolated ASan попытка root 88b48711a / PulseLib dd35368 завершилась
5/6 native cases: единственный failure — незарегистрированное имя генератора.
Это не полный PASS и не ASan finding; исправленный снимок проверяется отдельно.

Reader fix root `d5c74bad03f46cc66d5b1271ea923f05bce5c0b5`: glob
`*_threshold_proposal.json` раньше включал новые `*_signed_bounds_threshold_proposal.json`
в четыре базовых случая и падал в setUpClass. Теперь допускаются ровно четыре
базовых файла и либо полный набор четырёх signed-domain файлов, либо его
отсутствие в legacy snapshots. Неизвестные/неполные наборы не игнорируются.
Общий math test проверяет оба домена по тем же actual frames. Собственный
35-test reader `s08-threshold-signed-full-audit-normal-a2` прошёл на ранее
успешном native gate; а1 и его диагностика сохранены как неуспешная попытка.
[Signed full normal bundle](../../../Reports/StructTrain/TimeLearner/s08-threshold-signed-full-normal-a1/README.md)
содержит 942 файла в 8271552-byte архиве; producer и reader snapshots указаны раздельно.

[Calibrated normal bundle](../../../Reports/StructTrain/TimeLearner/s08-calibrated-normal-a2/README.md)
опубликован commit `9746ea4ba908b3030762fd6c276809142f27b8ce`: 581 файл,
1797464 bytes lossless primary archive с source CSV, обеими версиями моделей,
raw proof, gates и готовыми frozen evaluation specs/metrics.
[Visual bundle](../../../Reports/StructTrain/TimeLearner/s08-calibrated-report-normal-a2/README.md)
опубликован commit `5feb102f26df96188ed20d7a9d0076eb679b69b5`:
12 выбранных PNG и 26740-byte metadata archive; полный cache не загружен в Git.
Git-only перенос на M40 проверил все 581 member hashes; метрики воспроизведены.

В этом двухпаттерновом контроле исходное обучение обеих моделей завершилось
с `search_unresolved`; подтверждение калибровки не меняет этот статус.
Обе reset-per-trial пары удовлетворяют criterion.
В последующих preserve-dynamics пробах target даёт outside spike и FN;
суммарно TP=1,FN=1,TN=2,FP=0, accuracy=3/4. Позиция/порядок и reset policy
не разделены: причинный эффект одного reset этим не доказан. Это не August replay
и не восьмипаттерновая матрица. Model/threshold hashes остаются frozen.

Первый normal report attempt использовал system Python без matplotlib и завершился
с exit 1. `ff432f5599982b6a7495d6c9a9feaad2e692a273` добавил Agg/PIL preflight
до создания выходного каталога во всех четырёх renderer entry points;
отрицательный контроль проверяет отсутствие partial report при missing backend.
Повтор использовал существующий M40 plot-venv-a1, runtime/interpreter versions
сохранены. Старый queued ASan report остановлен до генерации (143, причина записана)
и заменён исправленным a2. Новый ASan report завершён: те же 3 report + 5 plotting
checks прошли. Native jobs не прерывались. Полный cache хранится на M40;
ручная visual acceptance всех ASan графиков не заявляется.

[Calibrated ASan bundle](../../../Reports/StructTrain/TimeLearner/s08-calibrated-asan-a2/README.md)
опубликован commit `a4984f1baeb1bb74b3e2cbbc938ec76f5c231f03`: 1171 файл,
3093212 bytes. Включены persistence, обе версии calibrated native proofs,
source CSV, модели, девять reader checks, frozen specs/metrics и report metadata.
Normal и ASan модели имеют одинаковые semantic revisions и результаты 3/4.
Это scoped воспроизводимость двух fixtures, не независимые случайные обучения.

## Журнал проверок и уточнений за день

1. Разрешённая очистка тяжёлых производных отчётов завершена в origin и 14
   корневых Git-копиях с сохранением файлов, восьми stash и резервных bundles.
   Истории сабмодулей не переписывались. Проверены изменённые trees, свежий
   recursive checkout и старые → новые root SHA.
   [Отчёт](../../../Reports/StructTrain/TimeLearner/s10-root-history-cleanup-a1/README.md).
2. В обычном native candidate gate a2 прошли 12/12 cases. Independent reader
   подтвердил derivation и primary source CSV; последующие pure-data selection
   проверки сохранили NonSeparable для исходного двухпорогового набора.
   ASan a2 не принят: два 20-кГц source setups исчерпали 600-секундный wall budget.
   Для новых transport/calibration fixtures явно объявлены 1800 секунд;
   математические допуски и production default не менялись.
3. В новом potential gate на обоих workers прошли Classic/Branch N1 при 2000 Гц.
   Независимый reader `6d9bf22fc4f32ea404abd0a6dd6abe09c795841d` воспроизвёл
   bracket из настоящих LTZone frames и исходного learned-state CSV proof.
   Предложенные пороги: Classic 0.003336969230622544, Branch 0.006293579947234118.
   Общий timing scorer подтвердил отдельные свежие reset-per-trial пробы обоих
   кандидатов. CLI reader `2528cf27d89ab1b8c0646deb2e3f79f756435aa9` реально
   выполнил select/confirm этих двух случаев на Elder. Это новый dispersed
   двухпаттерновый контроль; не историческая восьмёрка и не общая разделимость.
4. Первый 20-кГц potential gate обнаружил ошибку fixture: предел 10000 тиков
   обрывал ожидание полного растянутого foil window, оставляя executor busy.
   В `2f773b934e6285655875b024fdc6e2f6aff3efd9` ожидание вычисляется из duration
   и frequency. На момент снимка исправленный Classic 20 кГц прошёл на Elder;
   Branch и оставшиеся фазы ещё проверяются. Старый M40 a1 остановлен явно после
   подтверждения этого дефекта; SIGTERM и owned PID записаны отдельно. Его exit 1
   не является ASan finding или полным результатом матрицы. Новый ASan a2
   запущен после завершения старого задания, в отдельном runtime.
5. Candidate renderer реально построил четыре Branch N1 2000-Гц предъявления
   с наложенными actual input samples; прошли 3/3 readback проверки. Сохранены
   общий Y-scale, overview и увеличенные окна не менее восьми пикселей на tick.
   Выбранные target overview/detail просмотрены; весь 178-файловый cache этим
   просмотром не объявляется визуально принятым.
   [Компактный отчёт](../../../Reports/StructTrain/TimeLearner/s08-threshold-candidate-report-pilot-a1/README.md):
   82 primary/metadata files в архиве 342668 bytes и три выбранных PNG.

Подробности API, ограничений и CLI: [NativeThresholdCalibration](NativeThresholdCalibration.ru.md).
Python результаты `native_execution_verified=false` не заменяют native gate.
Незавершённые gates не являются PASS; их артефакты ещё должны быть опубликованы
в Git перед приёмкой и child → root merge.

Последующее уточнение 31.10: все четыре potential cases на Elder теперь прошли
при 2000/20000 Гц. Reader `6b03832182e281d6d1c7534a84ba7b300035ec75` прошёл
8/8 проверок без skips/errors/failures, включая CLI, source/proposal/candidate
links и restoration records. Для всех четырёх случаев получено `confirmed`
по полным первичным reset-per-trial данным; fixture затем восстанавливает исходную
модель, а не устанавливает native calibrated state.
[Переносимый пакет](../../../Reports/StructTrain/TimeLearner/s08-threshold-potential-normal-a3/README.md)
сохраняет 308 primary/metadata files в lossless архиве 5730080 bytes, исходные
CSV и готовые CLI descriptors. Полные legacy-фазы 16-case gate и ASan a2
проверяются отдельно. Это дополнение не завершает этап 8.

Позднее завершён и сохранён [полный normal gate](../../../Reports/StructTrain/TimeLearner/s08-threshold-full-normal-a1/README.md):
16/16 native и 29/29 independent tests, без skips/errors/failures. Отдельные 8/8
proposal/link checks частично повторяют семь тестов первого reader; это не 37
уникальных проверок. В архиве сохранены legacy primary data и неуспешные
попытки с их настоящими причинами, без переименования в PASS.

После этого baseline добавлен новый validator raw observations и native
response assessment (root ad975bbeb / PulseLib 25cf6a5). Он уже собран и прошёл
два 2000-Гц potential-контроля на Elder; 20-кГц/legacy/ASan и независимый readback
нового Core ещё выполняются. Старый normal gate не является проверкой этого
последующего изменения. Native calibrated commit/export по-прежнему открыт.

Последующий полный normal gate этого изменения завершился: root
`ad975bbeb5df18555d94329d3ee95f321921c171`, PulseLib
`25cf6a5bfadc0ee72182cb924f1d0730cf6dc71b` — 16/16 native cases;
независимый reader root `1ef44e2e6c5ce40339f9aeaa5e4426810e36844b` —
35/35 Python tests без failures/errors/skips. Проверены 64 native response
assessments, включая primary и полные наборы. Их
[переносимый Git-пакет](../../../Reports/StructTrain/TimeLearner/s08-threshold-assessment-normal-a1/README.md)
опубликован commit `de019b2b14f4b7cf6efb4e6220e1838257da0e5f`:
897 файлов в lossless архиве 8251508 bytes, с размерами и SHA256 каждого файла.
ASan этого изменения
ожидает завершения предшествующего задания, без изменения его активного runtime.

Новый signed-threshold contract (`88b48711a51dbcdb079d2386bac9d699885cb533`,
PulseLib `dd353680407e903b7dcb0b1e55dda9eacc17fcef`) пока не принят.
Попытка Elder `s08-threshold-contract-normal-a1` завершилась с 1/6 PASS:
storage aliases проверены, но четыре candidate/potential cases встретили
`unknown_threshold_candidate_algorithm`, а isolated IaF control —
незарегистрированное имя `NConstGenerator`. Причины: `auto` сохранил
`QJsonValueRef` на временный объект вместо значения; тест использовал C++ имя
вместо storage-образа. Исправления: PulseLib
`479084f4c35d61f60ef9b37eb0da246bc8dec87a`, root
`0afbf97c4ba9df4591eebe9a41fb916e02d1903e`, образ `NCGenerator`.
Повторная попытка `s08-threshold-contract-normal-a2` выполняется отдельно;
неуспешная попытка сохраняется и не считается PASS. Изолированная ASan-сборка
первого снимка выполняется в собственных source/build/runtime на диске Data M40;
она не подменяет проверку исправленного снимка.

Уточнение после завершения повтора: `s08-threshold-contract-normal-a2` прошёл
6/6 native и 6/6 independent Python checks, без skips/errors/failures, на root
`0afbf97c4ba9df4591eebe9a41fb916e02d1903e` / PulseLib
`479084f4c35d61f60ef9b37eb0da246bc8dec87a`. Подтверждены фактические storage
defaults/типы, isolated IaF signed crossing, Classic/Branch N1 при 2000 Гц,
8 signed и 4 legacy-v1 model roundtrips, 2 signed-bound proposals.
Это ограниченный normal gate, а не полная IaF/profile или ASan приёмка.
Повтор ASan исправленного снимка ожидает освобождения его отдельного build/source;
основная длительная ASan-серия продолжается независимо.

[Пакет signed normal gate](../../../Reports/StructTrain/TimeLearner/s08-threshold-contract-normal-a2/README.md)
опубликован commit `cc9b53faccaef8ff3b8bfe2abab2e921b088752c`: 425 файлов,
810680 bytes lossless archive, включая реальную диагностику неуспешной a1.
Новая полная normal-матрица исправленного снимка 0afbf97c4 поставлена отдельно:
`s08-threshold-signed-full-normal-a1` (16 native cases), затем
`s08-threshold-signed-full-audit-normal-a1` (35 independent checks того же reader).
Она охватывает 2000/20000 Гц, N0/N1 и регрессии native ownership/conversion;
до завершения и публикации не считается PASS. Последующие изменения документации
не изменяют зафиксированный code/runtime snapshot этих заданий.

Следующее изменение — native чтение сохранённых проб с повторной проверкой
raw samples/events и независимой request. Код PulseLib
`fece852167f617f0166b6ea794daae9a7beda47a`, root test commit
`61886fb803a65bf9eec89435f3634e601ad4c159`; документированный снимок
`158727b7275e3d3c702bdeb78f98f2d489a5d11f` / PulseLib
`efd343a9add299c60410e93caec07eb9b3513266`. Поставлены отдельные задания
`s08-calibration-persistence-normal-a1` и `s08-calibration-persistence-asan-a1`
на Classic/Branch N1 при 2000 Гц. Они ожидают освобождения соответствующего
source/build; до терминального результата не считаются PASS.
Это prerequisite для calibrated model import, но сам final calibrated
commit/export и production transaction ещё не реализованы.

Следующий code snapshot реализует native calibrated export/import:
root `fc36f38bdf2b204cb448ba6971425c4ec26890f1`, PulseLib
`353882b0391cb40d193599350f8b5dbac1df21e2`. Это proof выбранного candidate
с двумя успешными полными матрицами search/fresh confirmation, а не проверка
всей сетки или independent Test. Сохраняются raw observations и requests;
import пересчитывает proof и сверяет весь пакет, сохраняет физический model hash,
solo proof и recognition certificate=null. Calibration status отделён от
числового порога. Добавлены native import/export/Reset/frozen-probe и reject
controls; их normal/ASan задания поставлены после persistence gates.

Root `14949e46ee91f9df658b9951656fd789875cfe55` добавляет независимый Python
reader/CLI proof и 5 tests на actual packages. Reader gates
`s08-calibrated-state-audit-normal-a1` / `s08-calibrated-state-audit-asan-a1`
ожидают соответствующих native gates. Пока это code-implemented,
runtime-unverified добавка: accepted calibrated export, production transaction,
full PostTune, frozen evaluation scorer нового формата и весь этап 8 не закрыты.

Frozen scorer/direct trial audit/report adapter теперь реализованы в root
`b22c15fec9038185b38c47e7889736e39ac30734`. Они проверяют calibrated proof,
оценивают последующие actual probes и запрещают reuse calibration run ID;
независимость Test автоматически не присваивается. Новые 9-test reader gates
`s08-calibrated-frozen-audit-{normal,asan}-a1` ожидают native outputs. Отдельный
35-test gate `s08-calibrated-scorer-regression-normal-a1` уже выполняется на
сохранённых предыдущих native данных для проверки compatibility scorer.

На M40 поставлен `s08-calibrated-frozen-report-a1`, root
`590526997b7afd244c93292277b3ef862fba23c5`: после native и 9-test reader acceptance
он построит два полных отчёта всех четырёх последующих probes Classic/Branch
и выполнит 3 проверки первичных данных/покрытия/масштаба/хешей. Полные рисунки
остаются кэшем на Data; это не публикация больших PNG/SVG/PDF в Git.
До окончания gates и публикации артефактов эти изменения runtime-unverified.

## Остаток полного плана

| Этап | Что ещё требуется для полной приёмки |
|---|---|
| 0 | Принят; для новых этапов сохраняется --no-ff child → root workflow. |
| 1 | Закончить исторический реестр с августа и review волн аудитов; связать semantic catalog с полной runtime/mode coverage. |
| 2 | Сквозной immutable runtime настоящего experiment runner, полный переносимый scientific run bundle; адресные runtime tests уже существуют. |
| 3 | Распространить единый строгий scorer и expected-trial contracts на все активные experiment/analysis пути; закрыть весь размерный и corrupted-data контроль. |
| 4 | Полная lifecycle/storage/growth/reuse/Copy/Load и heterogeneous/profile/frequency матрица, включая ограничения multirate. |
| 5 | Полная production model transfer матрица всех режимов, calibration provenance и independent frozen Test; имеющиеся native export/import fixtures не закрывают весь этап. |
| 6 | Завершить общий controller/adapters во всех заявленных режимах и compatibility A/B; configured native API уже реализован. |
| 7 | Полная N0/N1, ambiguous/invalid, quantization, bounds и shared Branch матрица; optional C-trim и final repeatability по плану. |
| 8 | Завершить native calibration transaction/commit/rollback и final calibrated export, все PostTune modes и реальную frozen independent оценку; текущие candidate/proposal APIs являются подэтапом. |
| 9 | Полный production CLI preflight/prepare/train/export/calibrate/evaluate, job specs и завершённая миграция с удалением старых tools; calibrate select/confirm пока является анализом измерений. |
| 10 | Сквозная scheduler/lease/PID/recovery и fail-closed публикация настоящих jobs на двух workers; текущие process/publisher/ConditionSpec проверки не закрывают всю интеграцию. |
| 11 | Исторический saved-state replay, cold retrain, legacy/V2 A/B, реальные permutations/ITI/reset policies и вся матрица моделей. |
| 12 | Актуализация всех затронутых root/submodule/config/ClDesc документов и сквозная проверка единственности актуальной спецификации после миграции. |

Серия D не возобновляется автоматически. Августовские визуально подтверждённые
4/8–6/8 остаются рабочими наблюдениями исходного протокола. Научные 8/8 не
являются условием завершения рефакторинга. Изменения порога не переносят
сертификат solo Exact на новую recognition модель.

## Историческая постановка: persisted numeric boundary и Qt 5 owner import

Root b82fb74f15353b1bafd3a1df09334860ad4ad12b добавил JSON serialize/parse
перед native import finite threshold candidates, включая -0.0. Baseline gate
на Elder завершён: 2/2 native Classic/Branch прошли после JSON serialize/parse.
Подтверждённого signed-zero дефекта нет. ModelIdentity уже
канонизирует знак нуля; это дополнительная проверка, а не установленный дефект.

В owner import PulseLib dd7cd4fd9982682403bc7799e61c0527f7d461d2 исправлен
QJsonValueRef из временного QJsonObject при чтении calibration.threshold.
Qt 5 non-const operator[] возвращает proxy: auto сохранял ссылку на объект,
уничтоженный в конце выражения. Явный QJsonValue владеет значением.
Исправленный root `8cfd72eb17c8b762eea590afa6018dfa363f932a` прошёл на Elder
6/6 native (145460 ms) и 6/6 independent checks (11.818 s), без пропусков.
Reader принимает либо полный исторический набор eight signed controls, либо
полный новый twelve-file набор с четырьмя negative-zero controls; частичные
наборы отклоняются. На M40 ASan job PID 3087746 использует отдельный runtime
и не меняет старый 20-кГц процесс. До terminal acceptance его PASS не заявляется.
Прежние успешные проверки не доказывают отсутствие undefined behavior.

Перед сборкой на Elder выявлен недостаток места. Для двадцати дублирующихся
статических библиотек в неактивных runtime проверены полные SHA256 и размер;
дубли заменены hardlinks на сохранённые идентичные файлы. Освобождено
215742184 bytes. Первичные данные не удалены; inventory и receipt сохранены
в baseline readback. Каталоги активных экспериментов не затрагивались.

[Normal JSON/owner evidence](../../../Reports/StructTrain/TimeLearner/s08-threshold-json-owner-normal-a1/README.md)
опубликован commit `f42c1911fe8ac602ae921e933caf5c45117ac9fb`: 426 файлов,
829348-byte архив. Восемнадцать package audits относятся к baseline/final
данным, а не к восемнадцати независимым обучениям. ASan нового снимка
остаётся отдельной незавершённой проверкой.

## Native grid transaction: проверенный normal подэтап

Реализован `NativeThresholdCalibrationTransaction<Owner>`: preflight полного
объявленного design, immutable source, budget prefix, native import/lifecycle,
очередь проб без вложенного Calculate, измеренный выбор, независимый rebuild
и свежая confirmation, commit с export readback либо возврат source package.
Текущий standalone model proof всё ещё содержит selected-candidate confirmation,
а весь grid хранится отдельно в transaction report. Это ограничение явно
помечено, не подменено флагом grid_selection_verified.

Первый normal root `6f116ef54281a36fe5161ff3041f4eee27e3af7b` / PulseLib
`dcc266aa1213fc88d9ee6d49b7230128f1c35326`: 2/2 native, 184034 ms;
reader `aaf59e69006a0583dd4ffbedb208c70e7c76c906`: 17/17, 146.297 s.
Следующий root `c83f0ca4c7f11cb1957d690f7297fdbaaf110c8a` / PulseLib
`c36e27273b194752b3ad78184b8205c351bf3ce2`: 2/2 native, 193261 ms;
reader `b1b8f0611c818afc0128ff7b04193b5ecac25191`: 17/17, 142.189 s.
Вторая версия дополнительно связывает driver с storage/environment/frequency
и монотонным model clock. Внешние Reset/clock/frequency изменения не разрешают
перезаписать чужой контекст: результат RecoveryRequired с явной причиной.

[Normal bundle](../../../Reports/StructTrain/TimeLearner/s08-calibration-grid-normal-a2/README.md)
опубликован commit `2dc5825fbb76e5a95408507d10b644b0571d3302`: 431 файл,
2351604 bytes. Включены оба снимка, source CSV/модели, raw matrices, runtime
и native XML/logs, independent readers, 12 transaction records и четыре
context-guard records текущей версии. Калибровка не меняет исходный
`search_unresolved`. Это N1/2000 Hz двухпаттерновые engineering controls,
не независимый Test и не августовское воспроизведение.

Из того же Git-bundle M40 строит отчёты всех 16 records: все 10 завершённых
матриц должны дать 30 trial/soma pairs с фактическими input pulses и полными
overview/zoom/series. Renderer/CLI — root
`4b714c75730de140ba713c4bf09e06fc9d6db7b7`: 27/27 checks прошли за
163.700 s, включая 5 report, 5 plotting и предыдущие 17 evidence checks.
Полный cache содержит 1448 файлов. Метаданные и выбранные рисунки опубликованы
в 3c785fec6bd321559608cbb93eac009cfefd6907; последующая подборка full-response/
peak панелей — 6a8fa9fb884879298d8ad4e7fbdaa43af5a19e57. Visual acceptance
всей коллекции не заявляется.

Renderer `01faa730d4decf7c82ae0ea48c42fa622f41817f` дополнительно подписывает
actual LT spike markers прямо в PNG/SVG/PDF и series legend. Перестроены те же
16 отчётов / 10 матриц / 30 trial-soma pairs; 10/10 затронутых report/plot checks
прошли за 15.606 s. Неизменённые 17 evidence checks и численное обучение ради
легенды не повторялись. Обновлённая подборка сохраняет 16 PNG, включая Classic
soma2, и заменяет прежние last-input-only панели общими видами с полным пиком.
Предыдущие версии доступны в истории Git, bulk cache остаётся на M40.

ASan attempt s08-calibration-grid-asan-a2 завершился 1 до запуска native tests:
проверка compiler flags искала несуществующий NativeCalibrationTransaction.cpp
вместо фактических owner/test compilation units. Это ошибка запускателя,
не ошибка обучения и не ASan finding. Исправленный a3 использует те же
неизменяемые source commits, проверяет реальные owner/candidate/test flags
и исполняет отдельный native gate. Старый 20-кГц ASan runtime не менялся.

Предыдущий JSON/Qt5-owner подэтап тоже получил ASan acceptance: 6 native +
6 independent checks, [bundle](../../../Reports/StructTrain/TimeLearner/s08-threshold-json-owner-asan-a1/README.md)
commit `4d7051915400a193a9ecd3c3203b53bc1f22b020`, 302 файла / 669704 bytes.
Это Qt6 ASan regression, а не заявленное воспроизведение Qt5 dangling proxy.

Для сборки Elder дополнительно дедуплицированы только побайтово проверенные
статические библиотеки неактивных runtime: 281 путь заменён hardlinks на
сохранённые экземпляры, около 2.66 GB расчётно освобождено. Inventory/receipt
находятся в normal bundle; уникальные primary data не удалялись.

Полный этап 8, production CLI/worker, full PostTune, standalone grid-proof
сохранение, полная mode/profile/frequency matrix и независимые эксперименты
остаются открытыми; новая feature ветка не объединена в develop.

Обновлены профильные заметки PulseLib/Bin с явным разделением legacy snapshots
и native driver. PulseLib e8b004653d8ca03fb76d29357d21c6fe59c2b235 меняет
только документацию: Core tree совпадает с проверенным c36e272 (dedba1ad).
Bin 9af8a5c7cbcd94c76930b2b9928f2c307a98143b также содержит только правки
документации. Runtime evidence остаётся привязан к фактически собранным
commits c83f0ca4c / c36e272 / 5e9d3784, без подмены происхождения.

## Завершённая scoped ASan/visual приёмка grid driver

ASan root c83f0ca4c / PulseLib c36e272: 2/2 native, 1411630 ms.
Independent reader b1b8f0611: 17/17, 125.484 s.
[ASan primary bundle](../../../Reports/StructTrain/TimeLearner/s08-calibration-grid-asan-a3/README.md)
commit 350520aec8905eceee385b816004d0cecdbc4306: 230 файлов,
1196712 bytes. Ошибка flags harness a2 сохранена отдельно; native tests
исполнены исправленным a3. Leak detection выключен.

[ASan all-pattern reports](../../../Reports/StructTrain/TimeLearner/s08-calibration-grid-report-asan-a1/README.md)
commit 838c19639d899bba55f857dd9bb187d88b19b8b9: 16 reports, 10 матриц,
30 trial/soma pairs; 27/27 checks, 142.008 s. Git содержит 108 metadata
members в 70380 bytes и два выбранных PNG; полный cache — M40. Model revisions,
пороги и raw fresh-confirmation observations совпали с normal контролем.
Это deterministic повторяемость, а не независимые научные обучения.

[Normal visual bundle](../../../Reports/StructTrain/TimeLearner/s08-calibration-grid-report-normal-a1/README.md)
обновлён в 387d400eac055d8d8916dc493b523d47386724f6: 107 metadata members /
69784 bytes, 16 выбранных PNG. Четыре текущих панели просмотрены вручную
в исходном размере; два выбранных ASan counterparts побайтово идентичны
проверенным normal PNG. Полная visual acceptance 1448-file cache не заявлена.

Дополнительный receipt 8dfacdb23a12d919166fa8ad4269742c5a64a606 проверяет
именно реально работающий процесс старого assessment job, а не только
сохранённый baseline runtime. Hash /proc/PID/exe совпал с его собственным
pre-run manifest; старый runtime/source/build не изменялись. Старый полный
ASan gate продолжает отдельную серию и не считается завершённым по этим двум
новым fixtures.

Следующий обязательный блок: production native worker/CLI и RunManifest,
явно связывающий модель, полный CalibrationResult/grid report и исходные
данные проверяемыми SHA. Предпочтителен связанный immutable run bundle,
сохраняющий метод выбора, данные, порог и confirmation; текущее отсутствие
полного grid в standalone model proof не разрешает терять provenance.
Полный PostTune и mode/profile/frequency matrix остаются открытыми.

До расширения приёмки добавить adversarial regression очереди: внешний
потребитель забирает результат пробы, ставит чужую пробу или импортирует
тот же package без owner Build/Reset. Пока приняты owner Reset, clock и
frequency guards; владение очередью/instance в этих дополнительных сценариях
не доказано. Проверить запрет чужого Take/rollback и отсутствие зависания,
используя готовые source archives без нового Train. Это следующий проверочный
сценарий, а не заявление о воспроизведённом runtime-дефекте.

## Замыкание нового cold pipeline подэтапа

Normal/ASan interoperation дополнительно использовал две фактические cold N1
модели: full-grid calibration → frozen Test. По четыре owned фазы и portable
audits на worker прошли. Обе объявленные сетки дали NonSeparable; это результат
конкретного grid/protocol, не утверждение о невозможности любого порога.
Source training SearchUnresolved сохранён; положительный calibrated model path
на этой новой cold паре и графики новых calibration-grid probes остаются открытыми.

Опубликованы normal 3c087349 (231 файл / 619464 bytes) и ASan de48870a
(231 / 635736); оба архива и все member hashes проверены после Git fetch.
Они также сохраняют усиленные b839e879 controls 7/7, включая реальный
one-tick cold Train и запрет recognition export диагностической модели.
Предыдущие 6/6 и новые 7/7 перекрываются; это не 13 уникальных проверок.

Docs-only PulseLib 9068da76494667acc990713d273a2bacae64f49b сохраняет Core
проверенного a5671e96 без изменений. Bin 1e9a1389cc37e1a4e54b860184eac3ae25b310d1
уточняет границу legacy PostTune и нового worker. Новые gitlinks не подменяют
фактические source closures опубликованных бинарников. Все перечисленные
server jobs/publishers имеют terminal 0; общая приёмка этапов 1–12 открыта.

Полный fixed-evaluation cache: M40
`/media/user/Data/TimeLearnerRefactor/readbacks/s09-native-pipeline-report-normal-a2/reports`.
Git содержит только compressed primaries, metadata и восемь selected PNG;
все восемь просмотрены, полная visual acceptance остаётся false. Elder root
filesystem при последней проверке имел около 475 MiB свободного места; перед
новой сборкой нужна отдельная инвентаризация и освобождение подтверждённых
дубликатов/кэшей. Уникальные исходные результаты не удалять.

## Историческая постановка: TL-037 legacy inference

Ветка codex/timelearner-posttune-observation создана от develop с --no-ff merge
проверенных calibration/transport prerequisites. Полный этап 8 открыт.
[Повторная сверка и постановка](LegacyPostTuneObservation.ru.md) отличает
старые уже исправленные findings от остаточного saved-matrix inference пути.
На обоих workers baseline d8e2ad16 / PulseLib ded4b558 воспроизвёл 6 failures
из 8: stale Result, stale sample evidence и false Success при непосещённом foil;
две NaN controls прошли. PulseLib 39810a7 исправляет новый attempt scope.
Full physical fixture A1 использовал неверный native-owned dispatch и остановлен
с сохранением cancellation receipt; это не algorithm/ASan failure. Исправленный
A2 root e3fe5340 проверяет 12 адресных cases через настоящий legacy scheduler;
проверки ещё выполняются, source/build работающих jobs не меняются.

Перед сборками Elder подтверждённо дедуплицированы только неактивные static
archive duplicates: 1238 путей / 955 unique inodes до операции; свободное место
выросло с 209297408 до 7338950656 bytes. Первичный inventory A2 остановился
на /proc sshd permission до изменений. Исправленный A3 проверяет тип процесса
до чтения exe, останавливается при обнаружении native/build activity и перед
каждым hardlink повторно сверяет полные SHA. Исходники, первичные результаты
и native executables не удалялись. Оба receipts будут опубликованы вместе
с baseline evidence.

## TL-037: normal/ASan addressed gate и visual receipt

Addressed A2: normal 12/12 (220.780 s), ASan 12/12 (1555.310 s), без
failures/errors/skips; ASan leak detection выключен. Additional normal
regressions: 37/37, 318.086 s, на том же A2 binary без пересборки. Это две
разные native invocation, не один общий 49-case процесс. Core source остаётся
39810a7; позднейший PulseLib d3dd2a4 меняет только documentation.

Normal strengthened reader a153c052: 6/6, 5.867 s; ASan — 6/6, 5.101 s.
Оба sample peaks пересчитываются из каждого реального CSV отсчёта, подделка
конечного peak при finite/observed flags отвергается. Все четыре ASan CSV
побайтово совпали с normal; metadata packets равны семантически. Это
deterministic correspondence и основание повторно использовать normal
waveform cache, не независимые научные повторения.

Published receipts: [normal regressions/peak reader/ClDesc metadata](../../../Reports/StructTrain/TimeLearner/s08-posttune-observation-regression-normal-a1/README.md)
9f5a3a178 (460 files / 777832 bytes), [ASan A2](../../../Reports/StructTrain/TimeLearner/s08-posttune-observation-fixed-asan-a2/README.md)
ed4c9a947 (111 / 1004100). Все member hashes проверены после Git fetch.

[Visual metadata и selected QA](../../../Reports/StructTrain/TimeLearner/s08-posttune-observation-report-normal-a1/README.md)
4572e32b: 11 rendering/data/plot checks, 728.200 s; late stronger peak reader
6/6, 4.663 s, без повторного рендеринга. Четыре полных physical runs, оба
паттерна и шесть soma channels: 12 pattern/soma pairs. Cache содержит 8573
файла PNG/SVG/PDF/HTML/primary/metadata на M40 Data; Git хранит 29 metadata
members / 348764 bytes и 11 selected PNG. Все 11 просмотрены в исходном
1920×960, подписи/входы/волны читаемы. Full-cache visual acceptance false.

Source cache: `/media/user/Data/TimeLearnerRefactor/readbacks/s08-posttune-observation-report-normal-a1/reports`.
Legacy producer не записывает model identity или spike times: они явно unknown,
а validity/complete на графике относится к полноте записанных данных, не к
V2 calibration proof или физическому settling. Между 2000/20000 Гц совпадение
амплитуд не требуется и не заявляется. Сходимость и научный 8/8 не получены
из этих диагностик. Отдельная 37-case ASan regression ещё выполняется на
закреплённом A2 runtime; исходники/build/runtime не обновлять до terminal.
Полный transactional PostTune, C-trim и обязательная mode/profile matrix открыты.
