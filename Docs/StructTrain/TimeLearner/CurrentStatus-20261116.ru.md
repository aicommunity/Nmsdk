# Статус полного плана TimeLearner — 16 ноября 2026

Проверка 2026-11-16T18:42:22Z; состояния живых заданий указаны по последнему серверному наблюдению. Полностью принят исходный этап 0; этапы 1–12 частичны. Это не оценка «1/13 работы»: во всех остальных этапах есть реализация и адресные приёмки, но остаются требования исходного плана. Цель целиком активна. Научные 8/8 не являются условием завершения рефакторинга.

Принятый до этого evidence-подэтапа root develop: 79722b18c40063f9dda3e3107ecbd5a43b60e17b. PulseLib 23d039e44f927eb8040473845d3c391270d9d15e, Bin 8cb6dba07b30432272984c8ce3136b48ad06f064, Rdk de4134235c0dcb8b91fd9a43b267348ad1a163ca. Новые подэтапы — отдельные ветки и --no-ff merge; пользовательский E:/Science-Repo/nmsdk-git не изменяется.

## Последние научные результаты

| Эксперимент | Подтверждённый результат | Что он не доказывает |
|---|---|---|
|[Moderate Branch N1](N1ModerateRecoveryScientificReport-20261116.ru.md)|Один локально jointly-ready input2; следующий input1 ambiguous, общего сертификата нет. Actual низкопороговый Test: TP1/FP6/FN0/TN1, target до последнего входа.|Сходимость всей модели и успешную классификацию.|
|[Stock/PSI2.5 matched cold](PresynapticColdScientificReport-20261116.ru.md)|Оба новых Train останавливаются на ambiguous input1 после одного локально готового input2. Исходный PSI A1 — ошибка окна; исправленный A2 принят на реальных данных.|Общую бесполезность PSI или физическую недостижимость цели.|
|[PSI actual threshold](PresynapticRecognitionScientificReport-20261116.ru.md)|Повтор baseline100 точен; единственный объявленный threshold0.189057455929736 даёт TP1/FP6/FN0/TN1. Independent Elder replay принят.|Independent scientific evaluation или завершённое обучение.|
|[Fast cold3600/7200](FastN1BracketScientificReport-20261116.ru.md)|Первые19 scalar candidates совпадают; итог19/28. У7200 input2 локально достигает исходных допусков, но оба Train budget_exhausted.|Финальную свежую готовность всех входов.|
|[Fast terminal7200 recognition](FastN1RecognitionScientificReport-20261116.ru.md)|Baseline100 молчит; actual threshold0.0560090535350351: TP1/FP3/FN0/TN4. Target event0.2535с раньше последнего входа0.49с. Все16 окон полны, модель frozen.|Классификатор с малым числом FP:3/4 положительных ответов ложные.|
|[Fast cold21600](FastN1FullTrainingScientificReport-20261116.ru.md)|31 scalar candidate,66 полных групп и1 partial. Первые28 кандидатов совпадают с7200. На terminal L=[201,201,121,1] group67 остановлена своим300с wall limit; она измеряла anchor input3. Input1 наL201 ещё не измерен. Сертификата нет.|Провал input1 наL201, физическую невозможность или исчерпание общего21600с лимита.|
|[Новый terminal21600 recognition](FastN1FullTrainingRecognitionScientificReport-20261116.ru.md)|Baseline100: TP0/FP0/FN1/TN7. Actual единственный threshold0.054353792695896797: **TP1/FP1/FN0/TN6**. Target через3мс после последнего входа; FP уrow4 до последнего входа. Все16 полны/valid/frozen, процессы закрыты. Primary58.74MB/1423members и1287PNG report опубликованы;18 выбранных оригиналов всех8 паттернов просмотрены.|Общую сходимость Train, independent evaluation или устойчивость к порядку/ITI.|

|[Fast groupwall600, новый cold](FastN1GroupWall600OOM-20261116.ru.md)|Native process_error, kernel oom-kill при4 GiB после21793.547с. Сохранены759 пар raw JSON/CSV; конечной модели и scalar summary нет. Полный аварийный primary опубликован.|Сходимость, валидный BudgetExhausted или качество новой конечной модели.|

Августовские визуально подтверждённые4/8–6/8 сохраняют силу в исходном протоколе. Изменённые порядок/ITI и современные отрицательные проверки не отменяют этих наблюдений. При Train нужен максимум закреплённого импульса; раздельная ранняя вершина допустима, слияние остаётся ambiguous. Test рассматривает весь отклик и фактические native spikes.

## Что принято в последнем подэтапе

- [Fixed-physics mode preflight](FixedPhysicsModePreflight-20261116.ru.md):6/6 M40, все процессы закрыты;3 ранее допускавшихся C-search jobs воспроизведены production-генераторами и теперь отклоняются до дорогого Train. Структура и SHA обычных деклараций сохранены; C0 history и общий C-search API разрешены. Elder A1 получил capacity refusal до тестов, повтор отложен до закрытия order64. Native математика и текущие опыты не менялись.
- [Fast threshold independent replay](FastN1ThresholdIndependentReplayAcceptance-20261116.json): Elder1/1, все1333 members восстановлены; все8 исходных и повторных baseline waveforms сравнены напрямую. Это независимая проверка тех же данных.
- [Fast Soma/LT temporal scope](FastN1CommonTemporalAcceptance-20261116.json): baseline936PNG, actual candidate1403PNG. Сохранены побайтно432 прежних baseline Soma и983 обычных candidate PNG. Дополнительно просмотрены46 выбранных оригиналов. Полный ручной просмотр галерей не заявляется.
- [Cold21600 primary и32-view comparison](FastN1FullTrainingComparisonAcceptance-20261116.json) опубликованы. Четыре новых Train overview просмотрены. [Новый40-view выпуск принят1/1](FastN1TrainingResponseZoomAcceptance-20261116.json): восемь native response-max zoom добавлены и просмотрены,32 прежних PNG побайтно сохранены. Это масштаб рисунка, не изменение assigned-impulse measurement.
- [Новый frozen8 primary](FastN1FullTrainingFrozenAcceptance-20261116.json) опубликован: полная модель, входы, CSV, manifests, события и controls. [Независимый Elder DATA/scorer/report принят1/1](FastN1FullTrainingFrozenTemporalAcceptance-20261116.json):489 logical members/488 regular после одного подтверждённого glog alias,1009PNG,16 выбранных оригиналов всех8 паттернов просмотрены. Процессы закрыты.

## Сверка исходных этапов

| Этап | Статус | Выполнено / остаётся |
|---|---|---|
|0. Начальное объединение|Принят|Согласованные develop/gitlinks и merge commits.|
|1. Доказательства и параметры|Частично|Исторические anchors и реестры есть; semantic/effective-factor review, inherited properties и unknowns не закрыты.|
|2. Изолированные сборки/runtime|Частично|Runtime/manifests/учёт процессов работают; полная resource/build/fault matrix открыта.|
|3. Наблюдения/scorer|Частично|Strict IDs, finite/completeness и реальный аудит проверены; все применимые legacy adapters/режимы ещё не приняты.|
|4. Lifecycle/storage|Частично|Реальные native fixtures/effective graph/physics checks; вся fresh/reuse/Copy/Load/Build/growth/heterogeneous матрица открыта.|
|5. Export/import|Частично|Полное состояние, Train→Test, boundary continuation работают; вся физика/связи и independent corpus replay не приняты. [В новом persisted candidate89.5% compact JSON занимает архив обучения](FrozenModelStateSizeReview-20261116.ru.md); разделение payload и history открыто.|
|6. Общий контроллер|Частично|Общий native service, configured controller, Classic/Branch adapters работают; legacy/V2 A/B, остаточное дублирование и multirate открыты.|
|7. Алгоритмы|Частично|Measured bounded L/Ns/Rs search, revision-bound observations и fresh final gate реализованы. Полная matrix/C-search и проблема merged responses открыты; общего сертификата в текущих cold опытах нет.|
|8. Conversion/PostTune/calibration|Частично|Versioned solo/recognition, транзакции, actual threshold/frozen проверки; все режимы/rollback/interruption/independent evaluation не приняты.|
|9. Пакет/миграция|Частично|Корневой CLI и357 migration entries проверены; complete=false, часть Bin-инструментов/callers остаётся.|
|10. Runner/provenance/publish|Частично|Owned groups/leases, ConditionSpec и fail-closed публикация; полная fault/effective-factor matrix открыта.|
|11. Научная матрица|Частично|Исторические replay/cold, современные Train/Test и графики есть; итоговое legacy/V2/order/ITI/reset/physics сравнение открыто.|
|12. Документация|Частично|Текущая сводка отделена от исторических отчётов; финальная root/PulseLib/Bin/config/ClDesc сверка и миграция не завершены.|

[Elder current SDK принят154/154](ElderCurrentFastN1SdkAcceptance-20261116.json), все35 native groups закрыты. [Новый протокол fixed-model order: contract5/5](FrozenDiagnosticOrderPreparation-20261116.json); native64 приёмка ещё не получена. Приёмка алгоритмов по всем исходным режимам остаётся открытой.

[Независимый replay нового threshold primary принят1/1](FastN1FullTrainingThresholdIndependentReplayAcceptance-20261116.json):1423/1420,3 proven content aliases, исходные/повторные baseline waveforms равны; no new native execution. [Native baseline8 на Elder завершён](FastN1FullTrainingElderNativeRepeat-20261116.ru.md): TP1/FP1/FN0/TN6, все восемь полных waveform точно равны M40 (max absolute difference0.0). Оба native process baseline8/study56 закрыты; parent controller ещё выполняет итоговую проверку. Это новое исполнение сохранённой модели, не повторное обучение. Приёмка всей серии64 и полный новый native primary пока не получены.

## Подтверждённые текущие задания

| Worker | Job / owned PID | Последнее подтверждённое состояние |
|---|---|---|
|M40|s11-fast-bracket-groupwall600-m40-a1 /2814832|Все процессы закрыты. Native process_error/SIGKILL, kernel oom-kill при4 GiB; итоговая модель/summary не сохранены. Сохранены759 пар проб,758 complete/valid и1 incomplete/invalid по raw flags. Полный неуспех опубликован: [OOM report](FastN1GroupWall600OOM-20261116.ru.md). Новый Train/Test не запущен.|
|Elder|s11-frozen-order-native-elder-a2 /2352165|Все8 baseline и56 study записаны; оба native-процесса закрыты. Parent Python-controller ещё проверяет полные модели и наблюдения. Baseline8 точен: TP1/FP1/FN0/TN6. Итоговые rotation counts и полная приёмка64 пока не опубликованы.|

Threshold Test завершён и принят1/1; [самодостаточный primary и научные метрики](FastN1FullTrainingThresholdScientificAcceptance-20261116.json) опубликованы. Коллектор и actual Soma/LT report закрыты, report1/1;18 выбранных оригиналов просмотрены.

[Production подготовка group wall600 принята5/5](GroupWallPreparationAcceptance-20261116.json). [Новый cold job](FastN1GroupWall600Preparation-20261116.json) запущен после полного закрытия threshold Test, controlsd54c51feec61d27b6b693ea1d8764e3df240ee0a. От terminal21600 job отличаются только run_id и group wall300→600; общий21600с, вся математика и native runtime прежние. Его научный результат пока неизвестен.

## Следующая научная работа

1. Устранить подтверждённый OOM сохранения groupwall600: native leaf имел4 GiB, а не8 GiB внешнего controller. Сначала проверить память и сохранение большой модели/контрольной границы; затем повторять объявленный cold-протокол. Текущий аварийный запуск не имеет финальной модели, поэтому его нельзя переносить в Test или оценивать как завершённое обучение.
2. Довести уже работающий [Elder order A2](FrozenDiagnosticOrderLaunch-20261116.ru.md) до завершения rotations и публикации полного нового primary; actual same-order control8 уже пройден. Модель и threshold0.054353792695896797 фиксированы до новых проб; никаких новых порогов по результатам перестановок.
3. Проверить порядок, ITI, reset и оставшуюся режимную/физическую матрицу по отдельным протоколам. Same-Matrix7/8 относится только к исходным восьми паттернам и reset-per-trial.
4. Завершать исходные этапы1–12, включая legacy/V2 A/B, миграцию и документацию. Число инженерных PASS не измеряет готовность классификатора. Надёжного срока получения устойчивой классификации пока нет.

Техническая очистка истории завершена. Тяжёлые primary, модели и полные галереи — /media/user/Data/Nmsdk-StructTrainExpArchive на M40; [Samba](//10.245.1.12/Nmsdk-StructTrainExpArchive). В Git только код, настройки, документы и компактные refs. [Подробная карта реализации](ImplementationStatus.ru.md), [исходный план](RefactoringPlan.ru.md), [исходный аудит](PlanCompletionAudit-2026-10-25.ru.md).
