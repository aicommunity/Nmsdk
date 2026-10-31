# Состояние рефакторинга на 31.10.2026

План 0–12 остаётся активным. Полностью принят этап 0; остальные этапы имеют
незакрытые требования. Это продолжение [снимка 30.10](CurrentStatus-2026-10-30.ru.md),
а не переоценка исторических результатов по новым критериям.

## Отправная точка и незавершённая ветка

Принятый root develop: `8446ce2fc6775bb157cc4423665cba1319af228f`.
Gitlinks: PulseLib `086b04fb43bb57506558bfb6beba6250f61a6ce2`,
Bin `cbb3bf453d82f58672541ed8a42f7b5da54a5508`,
Rdk `c903b9bba4a31e604f9740ae6f6ed52a4e7de74a`.

Рабочая ветка `codex/timelearner-threshold-calibration` содержит native
candidate/proposal/assessment API, schema-2 наблюдения LTZone.Potential,
чтение raw observations, calibrated model export/import, независимый Python
proof audit, frozen scoring/report adapter и CLI анализа/select/confirm.
Она не объединена в develop: полная normal/ASan матрица и публикация её
первичных данных ещё не приняты. Наличие API не означает готовность всего
production calibration/PostTune controller.

## Оперативный статус после последней перепроверки

Реализованное в коде отделено от runtime acceptance. Нижний журнал сохраняет
последовательность проверок: его ранние «ещё выполняется» относятся к моменту
конкретной записи и не заменяют эту сводку.

| Контур | Авторитетное состояние |
|---|---|
| Potential baseline, PulseLib 7f17735 | 16 native, 29 independent и отдельные 8 частично перекрывающихся checks прошли; compact bundles опубликованы. Это собственный снимок. |
| Raw validator/assessment, PulseLib 25cf6a5 | 16/16 native и 35/35 independent прошли; 897 files / 8251508 bytes primary archive опубликован. Полная ASan приёмка открыта. |
| Signed threshold, PulseLib 479084f | 6/6 native и 6/6 Python прошли на Elder; 425 files / 810680 bytes опубликованы. Полный normal 16/16 gate завершён. Его reader a1 обнаружил ошибку glob; исправленный reader a2 прошёл 35/35 на тех же данных без нового Train. Опубликован bundle e8305ced. Отдельный ASan 6/6 native + 6/6 Python завершён с exit 0; это не полный ASan 16-case matrix. |
| Persisted observations, PulseLib fece852 | Normal 2/2 Classic/Branch при 2000 Гц с roundtrip/corruption checks прошёл; данные включены в normal bundle 9746ea4. ASan 2/2 прошёл; первичные данные опубликованы в a4984f1. |
| Calibrated state, PulseLib 353882b → ce7e81e | Normal 2/2 прошли на обоих снимках. Усиленный ce7e81e проверил import/export/Reset/frozen probes и отказы при неправильных bindings. Данные и модели опубликованы commit 9746ea4; ASan 2/2 прошёл на обоих снимках, включая усиленный ce7e81e. ASan bundle a4984f1 опубликован. |
| Frozen scorer/report, root b22c15fec | 9/9 checks прошли на normal ce7e81e (55.393 s); прежние 5/5 и 9/9 не складываются как уникальные tests. 35/35 compatibility checks прошли на старых native данных 25cf6a5, отдельно от нового 16-case gate. ASan 9/9 прошёл на ce7e81e; данные опубликованы в a4984f1. Это тот же scoped набор, а не полная mode/profile matrix. |
| Полные calibrated reports, root ff432f559 | M40 построил Classic/Branch: 4 предъявления двух паттернов × все сомы, 12 trial/soma pairs, 164 PNG и SVG/PDF. 3 report + 5 plotting checks прошли на normal и ASan данных. Git содержит 12 выбранных PNG и метаданные; полный cache — M40. Четыре графика просмотрены вручную. |
| Native grid transaction, PulseLib dcc266a → c36e272 | Normal 2/2 прошли на обоих снимках, включая native commit, rollback/cancel и clock/frequency guards. Independent 17/17 (8 transaction + 9 calibrated regressions) прошли; bundle 2dc5825 опубликован. ASan 2/2 native + 17/17 checks прошли (350520ae); ASan reports 27/27 прошли (838c1963). Production CLI/worker и явная связка экспортированной модели с полным CalibrationResult/RunManifest остаются открытыми. |
| develop | Новая calibration ветка не объединена. Только этап 0 принят целиком; весь план остаётся незавершённым. |

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

## Следующая проверка: persisted numeric boundary и Qt 5 owner import

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
