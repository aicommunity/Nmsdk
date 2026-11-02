# Состояние полного плана TimeLearner — 01.11.2026

Эта сводка описывает исходные этапы0–12, а не количество завершённых подэтапов.
Нормативный объём сохраняет [план](RefactoringPlan.ru.md). Полностью принят
этап0; остальные этапы выполнены частично. Научное8/8 не является условием
рефакторинга. Зелёный тест отдельного API не заменяет матрицу режимов.

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
