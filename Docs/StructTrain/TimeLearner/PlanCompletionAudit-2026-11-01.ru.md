Текущее состояние после последующих merge — [аудит04.11](PlanCompletionAudit-2026-11-04.ru.md).
Ниже сохранены исторические этапы и дополнения01–04.11 своих снимков.

## Дополнение04.11: проверен разбор границ stock-обучения

Feature [StockFailureBoundaryReports](StockFailureBoundaryReports.ru.md) исправляет
floating subtraction в diagnostic reader поздних окон и добавляет воспроизводимую
команду failure-report. На обоих workers прошли 12 data/regression checks;
на M40 — 4 текущие report checks. Проверены 20 probe/soma pairs, 1021 views,
25 дополнительных локальных видов; непосредственно просмотрены 12 выбранных
оригиналов. Дополнительные пики около 1.86e-5 стали читаемы без изменения
минимума 1e-6, исходных данных или training validity. Оба старых отказа сохранены.
Исследованы те же четыре cold conditions, без повторного запуска моделей;
это не классификация и не два независимых обучения. Изменения находятся в
feature с зависимостью от ещё не принятого в develop ModelSpec2 контура.
Полные этапы 1–12 остаются частичными; полностью завершён только этап 0.

## Дополнение04.11: принята семантика рабочего каталога Rdk

Rdk develop10e9d05a и root develop7c8d6e2f принимают сохранение явно заданного
до Init рабочего каталога. Пустое значение сохраняет прежний default. На обоих
workers проверены native/frozen/calibration, early refusals, duplicate launch,
неизменность runtime и обычный startup; все первичные артефакты доступны в Git.
[Точные SHA, проверки и ограничения](RdkStartupWorkDirectoryAcceptance-2026-11-04.ru.md).
Это адресное продвижение2/4/9/10. Полные исходные этапы1–12 остаются частичными;
полностью завершён только0. Console/ModelSpec2 transport feature проходит
отдельную приёмку; этот merge не принимает её полный C++ suite или science.

## Уточнение03.11: научная физика и границы результатов

Результаты новой N1 calibration5/8 и protocol study528 предъявлений относятся
к изменённому **двухвходовому integration-профилю**, а не к исходному stock
`NSPNeuronGen`: добавлена LTMembrane0.3nF, изменены DissociationTC и InhChannel
RestingResistance. Одновременно меняется место обратного действия спайка.
Использовать эти результаты как научное продолжение августовского четырёхвходового
графа было ошибкой постановки. Они сохраняются с фактическим scope;
инженерные storage/transfer проверки этого профиля также не отменяются.
[Происхождение, параметры и исправление постановки](ScientificProfileDrift.ru.md).

На основном stock-графе без LTMembrane проверены реальные initial/final child
physics и связи, в том числе после роста Branch. Первое cold обучение обеих
топологий завершилось `invalid_observation` из-за неоднозначного пика и не дало
обученной модели для классификации. Это не доказательство физической
невозможности обучения. Обнаружено ещё одно различие протокола: V2 использовал
порог образа0.0117, историческое обучение —100. Явная настройка construction
threshold и парное сравнение на одном runtime проверяются отдельно;
причинное объяснение неоднозначности порогом пока не подтверждено.
[Контракт, реальные scoped проверки и pending gates](InitialThresholdConstruction.ru.md).

Августовские визуально подтверждённые4/8–6/8 и их исторические replay остаются
результатами своих исходных условий. Новые profile/protocol ошибки не отменяют
те наблюдения. Полностью завершённым исходным этапом остаётся0.

## Дополнение03.11: два исторических Branch retry launchers удалены

Убраны Phase9/Phase10 br480 Python entrypoints без wrappers; manifest107 и
restored-Python negative fixture проверены production CLI на обоих workers.
Сверены20 members и380 exact Git source hashes каждого пакета. Два исторических
документа помечены без изменения исходных наблюдений. [SHA, source findings и
исправление текстового scope evidence](BranchRetryRetirement.ru.md).
Phase8 сохранён из-за действующих legacy consumers. Полная миграция и исходные
этапы1–12 остаются частичными; только исходный этап0 закрыт полностью.

## Дополнение03.11: ещё11 исторических Bin launchers удалены

SoftCold/OpenGaps/T2/T4 launcher retirement прошёл production migration105 и
restored-launcher negative gate на обоих workers. Все20 архивных members и380
source hashes каждого пакета независимо сверены. Обе skill/reference копии
согласованы с root CLI, status axes и текущим протоколом; исторические registry
таблицы сохранены. [Источники и SHA](SoftColdLauncherRetirement.ru.md).
Это продвижение9/12. Полная migration и исходные этапы1–12 остаются частичными.

## Дополнение03.11: исторические запускатели Reports

Удалены13 Reports job.py/runner.sh без wrappers;94 migration records прошли
production history CLI на обоих workers, восстановленный launcher отклонён.
Оба evidence архива и380 Git source hashes независимо сверены; остальные
primary payloads не изменены. [Контракт, SHA и ограничения](ReportLauncherRetirement.ru.md).
Это продвижение9/12; полная миграция, production orchestration и весь план
не закрываются. Полностью завершённым исходным этапом остаётся0.

## Дополнение03.11: scoped C₀ owner принят, полные этапы остаются частичными

Root develop0a495cefe /Pulse develop027070e8 принимают automatic ownership и
completed/stopped transport по normal43/26 и ASan43/26. Fresh recursive closure
17a4f61d подтверждает7 clean exact children и прежние tested Core trees.
[Полные SHA, артефакты и границы](C0Acceptance-2026-11-03.ru.md).
Это подтверждённый подэтап4/5/7. Public facade/witness/service/schema3/C-search,
полная physics/mode/dimension matrix, исторические/научные эксперименты и остальные
пункты исходного плана не принимаются этим corpus. Только исходный этап0 закрыт
полностью. Нижние pending/running записи сохраняют свою хронологию.

# Состояние полного плана TimeLearner — 01.11.2026

Дополнение03.11: удалены17 исторических Bin AsymRm pilot/finish/scale/sweep
launchers без wrappers;81 migration records и restored-Bin negative fixture
проверены production verifier на обоих workers. Восемь отчётов помечены
историческими, их исходное содержимое сохранено. [Приёмка и SHA](AsymRmLauncherRetirement.ru.md).
Это адресное продвижение этапов9/12, а не завершение всей миграции.

Дополнение03.11: [explicit C₀ native edits и transfer](C0Acceptance-2026-11-03.ru.md)
приняты адресно: normal9/14, independent reader24, ASan9/35/readers24, verified
actual mappings и766 members. Это не automatic C-trim ownership/search и не
вся матрица профилей; статусы исходных этапов0–12 не меняются. Отдельные
dataset clock/archive изменения не входят в этот принятый Core.

Последующее дополнение: [срез02.11 по полноте временных данных](CurrentStatus-2026-11-02.ru.md).
Обновление02.11: ASan163/163 и recording18/18 завершены, primary readers32/32;
сигналы совпали с normal temporal sources. Адресная приёмка search/scheduling/
diagnostic/ranking: [scope](SearchDiagnosticAcceptance-2026-11-02.ru.md). Состояния
исходных этапов0–12 этим адресным подэтапом не меняются.

Эта сводка описывает исходные этапы0–12, а не количество завершённых подэтапов.
Нормативный объём сохраняет [план](RefactoringPlan.ru.md). Полностью принят
этап0; остальные этапы выполнены частично. Научное8/8 не является условием
рефакторинга. Зелёный тест отдельного API не заменяет матрицу режимов.

Дополнение source provenance: [проверка references](SourceReferenceAudit.ru.md)
охватила96506 text entries/206 archives принятого Root422647a2d на двух workers,
с полностью одинаковым audit JSON.25 folders содержат references;22 требуют
dependency review, два являются диагностическими и один — fresh normal67 после
repair. Четыре крупных calibration transaction JSON остаются unknown. Это
адресный inventory, не подтверждение actual resource reads и не автоматическая
инвалидация научных измерений. Полный runtime impact audit остаётся открытым.

Дополнение02.11: адресно принят [поиск длины по измеренным задержкам](MeasuredLengthProposal.ru.md).
Normal fresh67/67 после Bin repair; ASan39 kernel+4 completed training cases
из сохранённого stdout+24/24 remaining XML, одинаковые67 имён без skips.
Первичный timeout7200s сохранён. Cold A/B не объявлен Exact; прежние positive
N1 controls сохраняют параметры/references и84 CSV на worker. Все16 selected
PNG directly reviewed, independent ASan rerender16/16 byte-equal; полные
временные отчёты240 trial-soma pairs и4146 PNG хранятся в M40 cache.
Old normal Bin provenance limitation остаётся открытым для прежних запусков.
Pulse merge a18bf543007c52a3ac7a6fbb148a48cb2c351de3 сохраняет tested Core.
Полные этапы6/7/11 и весь исходный план остаются частично выполненными.

Дополнительно source-reviewed девять shared inherited UContainer properties,
действующих на оба learner: [контракты и consumer anchors](InheritedPropertyContracts.ru.md).
На обоих workers9 records/8 hierarchy nodes byte-identical опубликованному
JSON. Activity вызывает Reset при выключении; TimeStep — частота; wall duration
ограничения могут менять child traversal. Это закрывает отсутствие inherited
source inventory, но не runtime/connected/save/load/profile матрицу этапов1/4.

Адресно принят [hot XML Load/Init/Reset](HotXmlReset.ru.md): normal32/32,
ASan32/32, readers18/16/16 на каждом worker,64 byte-identical crossworker CSV,
1476 temporal PNG в cache/26 directly reviewed originals. Scope — Classic/Branch,
N1/2/4/6,2000/20000Hz, Parameters-only/Parameters+State и описанные физические
fixtures. Это не вся lifecycle/profile матрица и не точный mid-probe checkpoint.
Отдельно на Elder воспроизведены4/4 отказа ModelArchive для длинных десятичных
значений публичной TrainingPattern: прежний Rdk matrix writer округлял до6 цифр.
[Исправление у владельца](ArchiveF64Precision.ru.md) принято адресно: floating
MDMatrix writer использует max_digits10. Unit10/archive16/XML32 пройдены на
обоих workers, normal regression21 без skips, readers23/16/16/18 на каждом.
Все24 transfer файла совпали по числовым массивам и semantic model/image
identities;64 XML CSV побайтно равны.262 PNG проверены автоматически,28 selected
оригиналов непосредственно просмотрены. Strict identity не ослаблена.
Ограничение actual mappings одного fast-exit normal unit-процесса сохранено;
его численные проверки не подменяют provenance. Полные этапы4/5/11 открыты.

Дополнение миграции: удалены оставшиеся5 исторических normsync Python и
standalone segsim.c. Manifest содержит36 retired records; Elder проверил
retrieval всех36, отсутствие путей и сохранность всех5 JSON. Receipt
58be4e41c2d095318d3260e634769f9b42d101b4 и границы проверки описаны в
[ScriptMigration](ScriptMigration.ru.md). Другие Docs/Bin/PulseLib/Reports
инструменты и полный этап9 остаются открытыми; численные результаты не менялись.

Дополнительно принят адресный контур [реальной N1-калибровки](PositiveN1Calibration.ru.md):
на каждом worker20 полных реально измеренных матриц /160 проб,4/4 reader checks;
20 temporal matrices /240 trial-soma pairs,3/3 report checks и28 непосредственно
просмотренных PNG. Лучший target-detecting кандидат обеих topology даёт5/8
(TP1/FP3/FN0/TN4). Строгая калибровка NonSeparable на конечной сетке, исходная
модель восстановлена; independent Test успешной калибровки отсутствует.
Это закрывает scoped проверку фактических порогов и отчётов, а не полный этап8.

Миграция root Docs shell:27 исторических entrypoints удалены в четырёх пакетах
с проверенными полными Git retrieval records. В TimeLearner audit Docs больше
нет tracked `.sh`; Python, Bin, Reports runner receipts и полный production
scheduler/CLI остаются открытыми. [Реестр/границы](ScriptMigration.ru.md).

Первый активный Bin analyzer [Branch dynamics](BranchDynamicsMigration.ru.md)
перенесён с6 прежними тестами в root package. Оба старых `.py` удалены;
20/20 адресных Python checks на каждом worker, archived full-module parity,
явная corruption-диагностика. Это частичная миграция и не новый C++/ASan прогон.

Адресно принята [finite validation десяти timing properties](TimingFiniteValidation.ru.md):
на обоих workers4 property+21 native regressions без skips; baseline84/120
неконечных назначений принятых ошибочно сохранён, после исправления120/120
отклонены. ASan regression повторён на том же runtime после timeout1800 s,
с бюджетом3600 s, не с ослабленными численными условиями. Полные этапы открыты.

Адресно приняты [production prepare/preflight](NativePreflight.ru.md): на каждом
worker14 положительных/6 отрицательных сценариев,2 one-tick Train controls,
20/20 reader/prepare checks и32 native размерных случая Classic/Branch×N0/N1×
N1/2/4/6×2000/20000Hz. Все46 initial graphs/parameters/config hashes и32 prepared
job hashes совпали между workers; preflight не вызвал Calculate. Actual runtime
captured parent-процессом; все52 ASan snapshots содержат libasan. Это scoped
приёмка команд, не полные этапы2/4/9/10 и не результат классификации.

## Снимки и пределы доказательств

Приняты адресно текущая source drift сверка217 learner properties и Git
проверка44 migration records на обоих workers; ещё6 исторических Phase12
shell удалены из Bin с полными retrieval records. Guard `runtime.source_closure`
теперь отклоняет неверный Git worktree даже при совпадении HEAD/status:
3/3 реальные Git fixtures на worker,2 воспроизведённых baseline отказа.
Обнаруженный Elder Bin alias сохранён в диагностике, существующие рабочие
копии не переписаны. Это ограничивает старую source provenance; численные
результаты сами по себе этим не опровергнуты. См. [source drift](PropertySourceDrift.ru.md),
[migration](ScriptMigration.ru.md), [worktree identity](SourceWorktreeIdentity.ru.md).
Ни один дополнительный полный этап0–12 этим пакетом не закрыт.

Последующее уточнение Elder Bin: отсутствовали все tracked files запрошенного
каталога. Отдельный owner-level repair восстановил их из точного Git commit
и исправил только per-worktree metadata; общий config/соседний checkout
проверены неизменными. Это не исправляет provenance прошлых запусков задним
числом. Адресный повтор measured-length gate67 начат после исправления;
ASan remainder24 выполняется после7200s timeout, где четыре training cases
успели пройти. Приёмка алгоритмического подэтапа остаётся открытой.
Область влияния прежнего Elder source на опубликованные provenance ещё
подлежит сквозной проверке. [Подробности](SourceWorktreeIdentity.ru.md).

Принятый сквозной live pipeline включён в корневой develop
1d4822af22e05b741e4a1c779cf99ba05cb0a1fa, PulseLib
f23d1b8dee908ddfdc549619b754875fc627ce9b, Bin
49adcd0208d0c8ab8d70e7cca47ae6e34b05145e и Rdk
027f7f8353608f83b55f3857a2f6c39138df4c65. Pulse Core соответствует фактически
проверенному019e5d17aa1d2dcc551dc71a32a85c383953c71a; Bin относительно
фактически использованного97dd1943a059e67888d56380c5409f3d3997d086 отличается
документацией. Это согласованная опубликованная closure, не новый численный прогон.

Подэтап codex/timelearner-n0-candidate-order принят адресно:31/31 native cases
и4/4 actual-data checks на обоих workers; дополнительно3+3 configured repeat
controls и temporal checks. Численный root942e5df4559467a9a19c56755f945ce6501e7780 /
Pulsec25db29404b544311a3256336c0c43991a384e12. PulseLib develop merge
38edfcad7983478a7e2ca736c32ae2703861c1fd сохраняет тот же functional Core.
Root acceptance merge8394a028a65afaacbe72f1ce741f26b309c4e3b7 опубликован
с exact gitlinks. Полный stage7 не закрыт;
[границы/источники](N0CandidateOrdering.ru.md), [журнал](CurrentStatus-2026-11-01.ru.md).

Следующий production N0 подэтап также проверен адресно: на каждом worker два
корпуса /28 реальных Console операций,7/7 reader checks для каждого протокола,
28 temporal reports и3/3 temporal checks для каждого протокола. Проверены
фактически измеренные Ns>1, фиксированные Rs/anchor и frozen handoff. Это
2inputs/2000Hz/identity/keep_done/fixed-or-grid, а не вся матрица вариантов.
Все16 full Train на двух workers — SearchUnresolved. Источники, limits окон
и scoped visual review: [N0 production](N0ProductionCoverage.ru.md).
Адресная [очистка серверов](ServerCleanup-2026-11-01.ru.md) завершена с receipts;
она не закрывает весь resource/scheduler контур этапов2/10.

## Сверка по исходным этапам

| Этап | Что действительно реализовано/проверено | Что ещё требуется для полного этапа |
|---|---|---|
|0. Начальное объединение|Merge commits, согласованные gitlinks, develop hints; последующие принятые подэтапы также объединялись children-first.|Этап принят. Для каждой новой feature сохраняется собственная приёмка и --no-ff merge.|
|1. Реестр доказательств/параметров|Есть опорные исторические commits, исходный inventory, дефекты и адресные evidence reports; отдельно source-reviewed10 control-property records с47 source references ([контракты](ParameterControlContracts.ru.md)) и ещё18 search/timing records с155 ссылками ([владельцы legacy/V2](ParameterSearchContracts.ru.md)); runtime-приёмка этих18 не заявлена.|Исходный semantic catalog211+6 уже существует. Актуализировать его consumers/helpers и runtime proofing по текущим ревизиям, учесть inherited Rdk properties; завершить поэкспериментный реестр с августа и закрыть review_required с доказательствами. [Сверка source slices](PropertySourceDrift.ru.md) не является runtime matrix.|
|2. Runtime|Изолированные deploy roots, runtime/build/source manifests, запуск с explicit ini, переносимые компактные primary bundles.|Доказать общий контур для всей матрицы targets/profiles/workers; соблюдать ресурсные ограничения, опубликованные closure и восстановимость всех научных результатов.|
|3. Наблюдения/scorer|Строгие IDs/completeness/finite/peak policies, реальные CSV, native summary/certificate аудит; явные отрицательные исходы и portable reports.|Распространить единый verdict на все активные исторические/новые аналитические пути, пройти всю размерность и corruption matrix.|
|4. Lifecycle/storage|Исправления Build/Init/Reset/frequency, storage-профили, native builders/editors, граф/readback и адресные growth/reuse/Copy/Load проверки.|Полная lifecycle×physics×frequency×dimension матрица, heterogeneous storage и сохранность индивидуальных Rs/C во всех поддержанных путях; multirate остаётся compatibility scope.|
|5. Export/import|ModelArchive, learned/recognition ownership, actual graph identity и реальный Train→Test с readback в принятой области.|Все виды моделей, связей, inhibition/heterogeneous physics и calibration/conversion provenance; независимый frozen Test. Не обещать mid-probe dynamic checkpoint.|
|6. Контроллер|Configured ControllerVersion=2 запускает общий NativeTrainingService через native scheduler; есть topology adapters и legacy controls.|Полный compatibility A/B и все режимы исходного плана. Текущее наличие общего контроллера не означает полноту поддержки всех configurations.|
|7. Алгоритмы|Bounded L/Ns/Rs, собственные CapturedPerInput targets, revision-bound измерения, individual resistance domains, fresh all-input final gate, N0 repeats.|Полная алгоритмическая/physical matrix, informed proposal policies, quantized/best-effort semantics и C-trim. Scoped исправление N0 принято по обеим server/ASan и repeat/temporal проверкам; [границы](N0CandidateOrdering.ru.md).|
|8. Conversion/PostTune/calibration|Immutable Solo→Recognition, native import, transactional candidate handling и live phase execution, cancel/rollback, persisted plans; реальные fixed/grid controls.|Остальные режимы/цели, target-reference/parallel-peak, optional C-trim, все модели, nonseparable/fallback semantics и независимая оценка.|
|9. Пакет/migration|В корне есть prepare/preflight/train/export/evaluate/calibrate/posttune/analyze/report/bundle/publish/history и поддерживающие модули; настоящий schema2 production pipeline проверен.|Расширить принятые prepare/preflight на остальные profiles/modes; завершить перенос активного специализированного анализа и удаление старых исполняемых scripts из Bin/PulseLib/Docs с Git migration manifest.|
|10. Очереди/provenance/publisher|Есть ConditionSpec/сериализация, process ownership/runtime checks, publisher и их адресные проверки.|Полная интеграция scheduler/leases/recovery/cancel/resources на двух workers, все fault cases publication и использование единого ConditionSpec всеми production cases. Наличие файлов не доказывает эту интеграцию.|
|11. Эксперименты|Есть реальные engineering Train→finalization→frozen evaluate controls и читаемые временные отчёты. Три свежих saved-state replay exact August closure воспроизвели4/8,5/8,6/8; passive observer CSV A/B совпал,7/7 reader checks на worker,96 PNG/15 directly reviewed ([источники/границы](HistoricalAugustReplay.ru.md)).|Настоящий historical cold Train и три frozen Test также приняты ([контроль](HistoricalAugustColdStart.ru.md)):4/8,5/8,6/8, полная serialized neuron identity, CSV и36 raw streams равны saved-state replay;7/7 temporal checks на worker. Это исходный same-matrix протокол. Legacy/V2, target в каждой позиции, ITI/reset-policy/independent Test и вся научная physical matrix остаются открытыми.|
|12. Документация|Подэтапы описаны с source SHA, primary artifacts и ограничениями; есть единая live-finalization спецификация.|Сквозное согласование всех root/submodule/config/ClDesc документов, semantic defaults и migration links. Старые аудиты сохраняются как снимки, не текущие спецификации.|

## Что подтверждает завершённый сквозной контроль

[NativeLiveFinalization](NativeLiveFinalization.ru.md) описывает общие lifecycle,
Cancel, plan codec и production schema2. Portable normal/ASan proofs содержат
по14 операций, codec и complete reader4/4; отдельные temporal proofs содержат
по14 reports и3 checks. Normal10 выбранных изображений1920×960 просмотрены;
ASan counterparts побайтно совпали с ними. Полная ручная приёмка cache не
заявлялась. Primary/model/metrics и выбранные рисунки опубликованы в компактном
Git, полные производные отчёты остаются на M40 Data.

Это scoped baseline Classic/Branch,N1,2inputs,2000Hz,fixed/grid,CalculateMode0/1.
См. [normal primary](../../../Reports/StructTrain/TimeLearner/s09-native-live-training-worker-normal-a2/README.md),
[ASan primary](../../../Reports/StructTrain/TimeLearner/s09-native-live-training-worker-asan-a1/README.md),
[normal temporal](../../../Reports/StructTrain/TimeLearner/s09-native-live-training-worker-visual-normal-a1/README.md)
и [ASan temporal](../../../Reports/StructTrain/TimeLearner/s09-native-live-training-worker-visual-asan-a1/README.md).
Повтор с ASan — инженерное соответствие, не независимая научная выборка.

Все4 full Train завершились SearchUnresolved. Во всех4 frozen same-matrix
парах TP0/FP0/FN1/TN1. Молчание target не является успешной классификацией.
Эти двухпаттерновые controls не воспроизводят и не опровергают августовские
визуальные4/8–6/8 в исходном протоколе без permutation/увеличенного ITI.

## Текущая последовательность приёмки

1. Production N0 подэтап объединён merge commit
   `674a7834f5440a7a07a17692fec6bf446731c0eb`; primary/temporal evidence
   завершены. Следующая алгоритмическая работа — реальные positive controls,
   размерности и physical cases для proposal policy, а не расширение claim
   по одному прохождению ограниченного negative corpus.
   [Контроль размерности](NativeDimensionControls.ru.md) принят merge
   `2b5af8c191b6ea20dff0f8b676e702db8c53c82f`: normal 16/16 и ASan 16/16;
   temporal приёмка завершена:
   16 dimension и 2 proposal reports с общими normal/ASan значениями,
   20 выбранных PNG прямо просмотрены. Полная ручная приёмка cache не заявлена.
   N=1 Exact здесь проверяет тождественную модель и
   свежий final gate; это не подтверждение успешного изменения геометрии.
   Дополнительный normal N0 контроль уже физически подтвердил timing-ready
   L2 → соседний Ns2 до L3 для Classic/Branch; ASan-аналог также подтверждён.
   Все четыре Train при этом SearchUnresolved; классификация не проверялась.
   [N1 refinement](MeasuredResistanceRefinement.ru.md) принят адресным root
   develop merge `ff98c7fef96eb4f947eca756528834877d14492d`.
   Актуальные normal a3 (40/40) и ASan a2 (32/32)
   сборки прошли адресные C++ gates. Одинаковые реальные cold N1 jobs дали
   Classic/Branch Exact на обоих workers против SearchUnresolved исходной
   finite mesh; по 2/2 reader checks. Proof commits: normal
   `bcbd30f1d87e352825e6c8400c5b929eff184ae5`, ASan
   `44858d7fb92a330470f50741fb862f9f8db23840`.
   Это первые положительные controls изменения L/Rs в данной V2 серии,
   при собственных reference amplitudes, 2000 Гц и двух входах.
   [Export/frozen контроль](PositiveN1Handoff.ru.md) этих моделей уже выполнен:
   по4 owned operations/128 trials/4 reader checks на worker, порог1 сохранён;
   Classic и Branch дают TP0/FP0/FN8/TN56. Полные192 trial/soma пары и3 report
   checks,22 выбранных PNG просмотрены. Это корректный перенос и отрицательное
   распознавание, не87.5% успешной детекции. Независимая оценка/калибровка и
   полная матрица остаются открытыми. Визуальная приёмка N1 Train подэтапа
   завершена:434 пары probe/soma в полных caches,6 production report checks,
   все24 выбранных PNG просмотрены в исходном1920x960; full-cache manual review
   не заявлена. PulseLib develop merge
   `d1c3df4cd0749e5869b977fb5e69417400ce1112` опубликован; Core совпадает
   с проверенным521df545. Root gitlink следует этому merge.
   Это не закрывает полный stage7 и не является historical V1 replay.
2. Продолжить алгоритмические и native physical gates этапов4–8; изменения
   математической задачи не подменяют исправление реализации.
3. Завершить production preflight/migration/scheduler/publication и исторический
   evidence/property review; это самостоятельные обязательные части.
4. Выполнить исторические и независимые контрольные эксперименты и итоговую
   сквозную сверку документации/матрицы. СерияD автоматически не возобновляется.

Только requirement-by-requirement доказательства всех строк исходного плана
позволят закрыть цель. Количество commits/tests не переводится в достоверный
процент завершения; приёмка отдельного сценария не закрывает весь этап.

Дополнение: проверка совместимости N0-шаблона перед приёмкой подэтапа. Исправление 0980f23309e099cb7cc73a1355a2dd25c7f788ab сохраняет полную конфигурацию при вызове подготовителя без новых факторов; раньше такой вызов ошибочно требовал повторного задания диапазона Ns. Проверено исходниками 54382334754986c574c7ccbcd5ded5b55f1b638e на Elder и M40: исходная ошибка воспроизведена через прежний публичный make_job; по 9 проверок для repeat=1/2, по 10 фактических Train-заданий на протокол регенерированы идентично, 1147 исходных файлов каждого корпуса не изменились. Численные прогоны и отрисовка повторно не выполнялись. Исходные отчёты с 7 проверками остаются отчётами своего снимка. Новые квитанции: Reports/StructTrain/TimeLearner/s07-n0-template-contract-normal-a2 (7aeb9655afdc3aec7ef607664393318fe290d1a3), s07-n0-template-contract-asan-a2 (0689def9d7a056bc9e9464d5ba647fcb8e30cbf9). Первые попытки настройки a1 завершились SyntaxError до выполнения проверок и также сохранены. Это приёмка совместимости подготовителя, а не положительный результат физического обучения и не закрытие полного этапа 7.

Подэтап миграции Docs Python (2 ноября): ещё4 разовых SoftCold/W1/W2 tools
удалены без wrappers; историческая taxonomy не пересчитывалась. На обоих
workers production verifier проверил48 migration records и отклонил Git
fixture с возвращённым старым файлом. Это metadata/Git приёмка, а не
численные/ASan tests и не закрытие полного этапа9.
[Обоснование и полные SHA](DocsPythonRetirement.ru.md).


## Дополнение02.11: structured schema1 Train exit

Исправлен production Python worker: exit2 с реальными stopped-state данными
training job schema1 ранее не анализировался. Новый run manifest schema2
разделяет process_error и data validity; старый schema1 не переоценивается.
На обоих workers maintained preflight-regression14 positive/6 negative/2
one-tick Train и28 reader/preparation/compatibility tests без skips.
Primary и exact compatibility inputs доступны в Git, hashes проверены.
[Источники и границы](StructuredTrainingExit.ru.md). Это частичное завершение
конкретного дефекта этапа10 и переноса active regression tool в этап9,
а не полный scheduler/publisher или весь исходный план0–12.

### Историческая запись wall-кандидата 486955b7 (до завершения integrated gate)

## Дополнение 2026-11-02: подтверждённые ограниченные изменения

Accepted root develop: `0c12a71757d4eb34412f043028f56edfa38ba974`.
Rdk develop: `eda206b6b35de451ae837473d731ba20e7c30bde`.
Закрыты normal/ASan native16, Math6 и reader7 для Activity/local-frequency
реальных fixtures. Все48 положительных проб /72 soma pairs сравнены между
workers; потенциалы совпали. Проверенные отчёты и границы находятся в
`InheritedPropertyRuntime.ru.md`, progress JSON и NormalAsanComparison.
Это частичное усиление этапов3/4/12, не весь lifecycle/storage или алгоритм.

В feature ветке wall-policy66/66 и строгий reader10/10 на обоих workers;
46 packets имеют объявленные разные исходы,4 Reset traces не считаются
закрытыми пробами. Full cache141 PNG на M40,18 выбранных просмотрены.
В develop эти изменения ещё не приняты: integrated74+Math6 выполняется,
публичный Console preflight и оставшаяся приёмка открыты. См.
`NativeWallSchedule.ru.md` / progress / VisualQA с точными SHA и job identities.

Статусы полного плана0–12 этим дополнением не повышаются до complete:
остаются полная история/evidence review, матрица lifecycle/storage/physics,
весь Train→Test и режимы финализации/калибровки, алгоритмы и статусы поиска,
legacy/V2 A/B, миграция оставшихся scripts, production scheduler/leases и
fault matrix публикации, независимые order/ITI эксперименты и сквозная docs.
Научного нового результата разделимой классификации здесь не получено.

Уточнение при объединении feature branches: integrated74+Math6 и public preflight уже завершены на обоих workers; их данные входят в StructuredTrainingExit.ru.md. Принятый root develop теперь44334e272de8429f29775512a860584c60350899. Объединение wall-policy и search-termination выполняется только в feature branch; оно не означает приёмку алгоритмических изменений в develop. Новое совместное состояние требует отдельной сборки и адресных gates.

## Подэтап 02.11: native gates, перенос и временные отчёты

В develop44334e272 принят maintained native-gate: positive2 и reader7 на обоих
workers; failed JUnit не становится PASS. Полный configured34 прежней search
feature завершился30/34 на обоих, с одинаковыми четырьмя ожиданиями сертификата
после sweep budget. Эти отрицательные gates сохранены. Исправленный diagnostic
transport4 + named Exact completed control1 прошёл5/5 на Elder, с равенством
frozen/fresh-process CSV; его ASan5 ещё работает.

Все32 закрытые training probes имеют48 soma/input пар и288 PNG в M40 Data;
24 selected original-resolution графика просмотрены. Normal/ASan32 CSV
идентичны, strict canonical packets идентичны; ledger связывает их с общим
visual cache. Git содержит сжатые primary, hashes и выбранные рисунки.
Это не классификация восьми паттернов и не полный ручной просмотр288 PNG.

Pulse fca7141/root07167d551 — совместный feature candidate, не принятый
алгоритмический develop. Его163 source-declared tests нужны после server build.
Явный Reset очищает control; граф проверяется отдельно, immutable stopped
export сохраняется до Reset. Допуски не расширялись.

Полностью закрытым этапом исходного плана остаётся только0. Этапы1–12 частичны:
полные evidence/property review и lifecycle/storage/physics, saved legacy и
весь Train→Test, legacy/V2 A/B и режимы алгоритмов, finalization/calibration,
миграция scripts, scheduler/leases и публикация со сбоями, научные order/ITI/
frozen матрицы и сквозная документация. SHA/отрицательные попытки/owned jobs:
SearchTermination.ru.md, SearchTermination.progress.json, SearchTerminationVisualQA.json.

Последующее уточнение: ASan5 также прошёл5/5, primary461cc58deda8f8d1b026fa3564591d1bd2882926
полностью проверен после Git fetch. Scoped transport root5e299dedf закрыт на
обоих workers. Новый combined root07167d551 всё ещё проверяется: Elder163
выполняется, M40 build выполняется. Общие статусы этапов0–12 не меняются.

Позднейший подтверждённый checkpoint: combined root07167d551 прошёл163/163
на Elder, JUnit readers7/7. Public Console на обоих:14+6+2, readers28/28;
данные и exact compatibility inputs опубликованы и проверены. Новый
saved-nonexact completed replay:4 модели/input0 +5 readers на worker,
model hash/certificate и весь golden CSV сохранены. Это не полная проверка
legacy training/recognition или всех входов. Полные SHA и ограничения —
SearchTermination.progress.json / LegacyCompletedReplay.validation.json.

ASan163-a1 прерван из-за ошибочного общего CI budget7200<9447.088s старого
inherited16 baseline. Частичные данные и -15 exit сохранены; новая ASan-a2
с21600s пока выполняется. Не принимать её заранее. Full payload/temporal
acceptance нового163 и широкая матрица планов всё ещё открыты. Stage0 остаётся
единственным полностью завершённым этапом0–12; версии2 в целом не присваивается
статус рекомендуемой по этим узким gates.

## Дополнение03.11: принятый scoped scientific checkpoint

Root develop merge `f879b3ded60c2ddca0be2fef15f794b04d9d87ad` принял
фиксированную N1 protocol series и temporal reports. Child closure остаётся
Pulse027070e8e1181380427edc9384641d08ed9943be,
Bin99f58da9296a794374cef679bbb878cb62af979a,
Rdkacc3de8d1af2480d61ddb723c3288f7e81003049. Новые feature изменения
initial-threshold, CandidateCursor и C-search этим merge не принимались.

Численные primary: `642f08ddca735d0a66755b20ce84decbfccf18f7`,528 complete
trials,5/5 readers. Полный renderer proof27ec82d40ae32a3238d2dfaee696cfabbaa65697:
792 trial-soma pairs,3/3 readers. Выбранные28 PNG из proof
f47fa0e0aabd24327a76011ada7b2edcf59f0d24 непосредственно просмотрены; hashes
и точная область ручной приёмки — N1ProtocolVisualQA.json. Полный image cache
на M40 Data, компактные первичные данные и выбранные изображения в Git.
Production workflow/report и соответствующие test source blobs после merge
побайтно равны проверенным снимкам29397614 и1a0b666eea211ef0a127f981564b9549bcce8579.

**Исправление научной постановки:** эта серия использует изменённый двухвходовый
integration profile с LTMembrane0.3nF, DissociationTC1ms и InhRm100MΩ.
Она не является stock четырёхвходовой моделью августа. Причинный эффект LT
по этим данным не выделен. Источник и разница topology/feedback —
ScientificProfileDrift.ru.md. Августовские рабочие4/8–6/8 не отменяются.

TP8/FN0 во всех основных условиях. FP24 при reset и continuous1.6s;
continuous0.4s FP10 Classic/15 Branch. Эти same-matrix данные не доказывают
независимую generalization, нулевой FP или успешность всех режимов обучения.
Stock preflight и первый отрицательный stock cold сохранены; новая версия
construction threshold и последующие stock controls пока в feature branch.

Это продвижение этапов3/9/11/12, а не их полное завершение. Полностью закрыт
только исходный этап0. Все исходные этапы1–12 сохраняют открытые требования:
полный property/evidence review, lifecycle/storage/physics и legacy/V2 A/B,
полные export/import/Train→Test и алгоритмические modes, PostTune/calibration,
остальная миграция скриптов, fault/lease/publication matrix, научные контроли
на stock моделях и сквозная актуализация документов. Fresh recursive checkout
последнего develop после этого merge также ещё требует отдельной проверки.

## Дополнение04.11: проверка физического model archive после construction

В feature codex/timelearner-initial-threshold проверены18 native cases на
Elder normal и M40 ASan. Доказательства60f5905c7b04ac41f16d405d2fe715f1e3eed174
иcd3a477ee03f5f75b2d71af83772ec6dce5dda1e опубликованы и объединены через
--no-ff. Подробности и независимые проверки: InitialThresholdConstruction.ru.md,
InitialThresholdArchiveNormalVerification.json и
InitialThresholdArchiveASanVerification.json. Каждый пакет содержит97
проверенных members;430 source hashes совпали с точными Git blobs.

Четыре новых Classic/Branch ×2000/20000Hz cases проверяют полный физический
граф и реальный scheduler response после export/import/Build/Init/Reset.
Construction threshold100 не стирает последующий instance threshold0.005.
Stock модель без LTMembrane. Training metadata явно not_trained; полного
calibrated recognition-state roundtrip ModelSpec2 эти cases не доказывают.
Ни этап4, ни5 не закрывается по этому узкому контракту. Pulse541 и root
feature пока не приняты в develop: требуются оставшиеся профильные gates.

H21 full213 на M40 подтверждён живым по PID3416749/start_ticks281000389;
его ожидание не является повторным запуском. Полный80-pair temporal report
stock stopped diagnostic ожидает завершения этого owned процесса. Численные
32 пробы опубликованы отдельно (c8381cfc3ecbf446ae1f59175c794ef547dcc93d),
обученные классификаторы и научная сходимость ими не заявляются.

На момент проверки Elder имел31GiB свободно, M40 root84GiB и Data423GiB;
два текущих native задания работали. Причина нехватки места не подменяется
диагнозом SSH. Новые тяжёлые отчёты размещаются на Data; primary/model/history
не удалены. Исходная классификация этапов остаётся:0 завершён,1–12 частичны.

Дальнейший full-calibrated-package gate04.11 выявил отказ ещё до калибровки:
на обоих workers4/4 cases завершили Train maximum_sweeps_exhausted, включая
оба исходных schema1 контроля. Доказательства470a9251af14e50f47e89815edafe5b6d7471513
и29da1f5bc1dfdd401d8bceb97cc7650f537dd5b5 опубликованы; все154/153 members и
431 hashes исходников проверены, фактический ASan mapping сохранён.
Подтверждённый физический archive18 gate этим не отменяется, но calibrated
transport не выполнен. Причина неверного выбора контроля: короткий endpoint
LearnedBoundary с ISI.08 не является ранее Exact production N1 job с ISI.03
и другой областью поиска. Нужен точный schema1/schema2 production replay;
увеличение tolerances или подмена отсутствующего source certificate исключены.
CalibratedModelSpec2.progress.json фиксирует закрытые workers, prerequisite
reader refusals и оставшуюся задачу. Изменения остаются feature/WIP.
