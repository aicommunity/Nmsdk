# Состояние полного плана TimeLearner — 01.11.2026

Эта сводка описывает исходные этапы0–12, а не количество завершённых подэтапов.
Нормативный объём сохраняет [план](RefactoringPlan.ru.md). Полностью принят
этап0; остальные этапы выполнены частично. Научное8/8 не является условием
рефакторинга. Зелёный тест отдельного API не заменяет матрицу режимов.

## Снимки и пределы доказательств

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

## Сверка по исходным этапам

| Этап | Что действительно реализовано/проверено | Что ещё требуется для полного этапа |
|---|---|---|
|0. Начальное объединение|Merge commits, согласованные gitlinks, develop hints; последующие принятые подэтапы также объединялись children-first.|Этап принят. Для каждой новой feature сохраняется собственная приёмка и --no-ff merge.|
|1. Реестр доказательств/параметров|Есть опорные исторические commits, исходный inventory, дефекты и адресные evidence reports; отдельно source-reviewed10 control-property records с47 source references ([контракты](ParameterControlContracts.ru.md)).|Завершить семантический review всех публичных параметров/defaults/setters/owners/modes и поэкспериментный реестр с августа; закрыть review_required с доказательствами.|
|2. Runtime|Изолированные deploy roots, runtime/build/source manifests, запуск с explicit ini, переносимые компактные primary bundles.|Доказать общий контур для всей матрицы targets/profiles/workers; соблюдать ресурсные ограничения, опубликованные closure и восстановимость всех научных результатов.|
|3. Наблюдения/scorer|Строгие IDs/completeness/finite/peak policies, реальные CSV, native summary/certificate аудит; явные отрицательные исходы и portable reports.|Распространить единый verdict на все активные исторические/новые аналитические пути, пройти всю размерность и corruption matrix.|
|4. Lifecycle/storage|Исправления Build/Init/Reset/frequency, storage-профили, native builders/editors, граф/readback и адресные growth/reuse/Copy/Load проверки.|Полная lifecycle×physics×frequency×dimension матрица, heterogeneous storage и сохранность индивидуальных Rs/C во всех поддержанных путях; multirate остаётся compatibility scope.|
|5. Export/import|ModelArchive, learned/recognition ownership, actual graph identity и реальный Train→Test с readback в принятой области.|Все виды моделей, связей, inhibition/heterogeneous physics и calibration/conversion provenance; независимый frozen Test. Не обещать mid-probe dynamic checkpoint.|
|6. Контроллер|Configured ControllerVersion=2 запускает общий NativeTrainingService через native scheduler; есть topology adapters и legacy controls.|Полный compatibility A/B и все режимы исходного плана. Текущее наличие общего контроллера не означает полноту поддержки всех configurations.|
|7. Алгоритмы|Bounded L/Ns/Rs, собственные CapturedPerInput targets, revision-bound измерения, individual resistance domains, fresh all-input final gate, N0 repeats.|Полная алгоритмическая/physical matrix, informed proposal policies, quantized/best-effort semantics и C-trim. Scoped исправление N0 принято по обеим server/ASan и repeat/temporal проверкам; [границы](N0CandidateOrdering.ru.md).|
|8. Conversion/PostTune/calibration|Immutable Solo→Recognition, native import, transactional candidate handling и live phase execution, cancel/rollback, persisted plans; реальные fixed/grid controls.|Остальные режимы/цели, target-reference/parallel-peak, optional C-trim, все модели, nonseparable/fallback semantics и независимая оценка.|
|9. Пакет/migration|В корне есть train/export/evaluate/calibrate/posttune/analyze/report/bundle/publish/history и поддерживающие модули; настоящий schema2 production pipeline проверен.|Единый prepare/preflight для всей матрицы, завершение переноса активного специализированного анализа и удаление старых исполняемых scripts из Bin/PulseLib/Docs с Git migration manifest.|
|10. Очереди/provenance/publisher|Есть ConditionSpec/сериализация, process ownership/runtime checks, publisher и их адресные проверки.|Полная интеграция scheduler/leases/recovery/cancel/resources на двух workers, все fault cases publication и использование единого ConditionSpec всеми production cases. Наличие файлов не доказывает эту интеграцию.|
|11. Эксперименты|Есть реальные engineering Train→finalization→frozen evaluate controls и читаемые временные отчёты.|Августовский saved-state replay, cold retrain, legacy/V2, target в каждой позиции, ITI/reset-policy/independent Test и вся научная physical matrix.|
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

1. Включить принятый N0 подэтап с точными child gitlinks; regression/repeat/
   temporal evidence завершены, полная алгоритмическая матрица остаётся открытой.
2. Продолжить алгоритмические и native physical gates этапов4–8; изменения
   математической задачи не подменяют исправление реализации.
3. Завершить production preflight/migration/scheduler/publication и исторический
   evidence/property review; это самостоятельные обязательные части.
4. Выполнить исторические и независимые контрольные эксперименты и итоговую
   сквозную сверку документации/матрицы. СерияD автоматически не возобновляется.

Только requirement-by-requirement доказательства всех строк исходного плана
позволят закрыть цель. Количество commits/tests не переводится в достоверный
процент завершения; приёмка отдельного сценария не закрывает весь этап.
