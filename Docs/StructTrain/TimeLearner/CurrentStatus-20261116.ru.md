# Статус полного плана TimeLearner — 16 ноября 2026

Проверка 14:13 МСК (11:13 UTC). Полностью принят исходный этап 0; этапы 1–12 частичны. Это не оценка «1/13 работы»: во всех остальных этапах есть реализация и адресные приёмки, но остаются требования исходного плана. Цель целиком активна. Научные 8/8 не являются условием завершения рефакторинга.

Принятый root develop: 3c2882c82a0317cf56120c19a3d0d0c58cffa0ba. PulseLib 23d039e44f927eb8040473845d3c391270d9d15e, Bin 8cb6dba07b30432272984c8ce3136b48ad06f064, Rdk de4134235c0dcb8b91fd9a43b267348ad1a163ca. Новые подэтапы — отдельные ветки и --no-ff merge; пользовательский E:/Science-Repo/nmsdk-git не изменяется.

## Последние научные результаты

| Эксперимент | Подтверждённый результат | Что он не доказывает |
|---|---|---|
|[Moderate Branch N1](N1ModerateRecoveryScientificReport-20261116.ru.md)|Один локально jointly-ready input2; следующий input1 ambiguous, общего сертификата нет. Actual низкопороговый Test: TP1/FP6/FN0/TN1, target до последнего входа.|Сходимость всей модели и успешную классификацию.|
|[Stock/PSI2.5 matched cold](PresynapticColdScientificReport-20261116.ru.md)|Оба новых Train останавливаются на ambiguous input1 после одного локально готового input2. Исходный PSI A1 — ошибка окна; исправленный A2 принят на реальных данных.|Общую бесполезность PSI или физическую недостижимость цели.|
|[PSI actual threshold](PresynapticRecognitionScientificReport-20261116.ru.md)|Повтор baseline100 точен; единственный объявленный threshold0.189057455929736 даёт TP1/FP6/FN0/TN1. Independent Elder replay принят.|Independent scientific evaluation или завершённое обучение.|
|[Fast cold3600/7200](FastN1BracketScientificReport-20261116.ru.md)|Первые19 scalar candidates совпадают; итог19/28. У7200 input2 локально достигает исходных допусков, но оба Train budget_exhausted.|Финальную свежую готовность всех входов.|
|[Fast terminal7200 recognition](FastN1RecognitionScientificReport-20261116.ru.md)|Baseline100 молчит; actual threshold0.0560090535350351: TP1/FP3/FN0/TN4. Target event0.2535с раньше последнего входа0.49с. Все16 окон полны, модель frozen.|Классификатор с малым числом FP:3/4 положительных ответов ложные.|
|[Fast cold21600](FastN1FullTrainingScientificReport-20261116.ru.md)|31 scalar candidate,66 полных групп и1 partial. Первые28 кандидатов совпадают с7200. На terminal L=[201,201,121,1] group67 остановлена своим300с wall limit; она измеряла anchor input3. Input1 наL201 ещё не измерен. Сертификата нет.|Провал input1 наL201, физическую невозможность или исчерпание общего21600с лимита.|
|[Новый terminal21600 frozen8](FastN1FullTrainingRecognitionScientificReport-20261116.ru.md)|Восемь полных valid наблюдений, model frozen, production1/1 и закрытие процессов подтверждены. Threshold100: TP0/FP0/FN1/TN7. Primary489 members/28.00MB опубликован.|Успешную детекцию: target пропущен. Новый низкопороговый итог пока неизвестен.|

Августовские визуально подтверждённые4/8–6/8 сохраняют силу в исходном протоколе. Изменённые порядок/ITI и современные отрицательные проверки не отменяют этих наблюдений. При Train нужен максимум закреплённого импульса; раздельная ранняя вершина допустима, слияние остаётся ambiguous. Test рассматривает весь отклик и фактические native spikes.

## Что принято в последнем подэтапе

- [Fast threshold independent replay](FastN1ThresholdIndependentReplayAcceptance-20261116.json): Elder1/1, все1333 members восстановлены; все8 исходных и повторных baseline waveforms сравнены напрямую. Это независимая проверка тех же данных.
- [Fast Soma/LT temporal scope](FastN1CommonTemporalAcceptance-20261116.json): baseline936PNG, actual candidate1403PNG. Сохранены побайтно432 прежних baseline Soma и983 обычных candidate PNG. Дополнительно просмотрены46 выбранных оригиналов. Полный ручной просмотр галерей не заявляется.
- [Cold21600 primary и32-view comparison](FastN1FullTrainingComparisonAcceptance-20261116.json) опубликованы. Четыре новых Train overview просмотрены. Прежние native edge views показывают края окна; новая проверка увеличений около recorded response maximum выполняется отдельно.
- [Новый frozen8 primary](FastN1FullTrainingFrozenAcceptance-20261116.json) опубликован: полная модель, входы, CSV, manifests, события и controls. Независимое восстановление на Elder уже проверило489 logical members/488 regular после одного подтверждённого glog alias; полный DATA/scorer/render job ещё выполняется.

## Сверка исходных этапов

| Этап | Статус | Выполнено / остаётся |
|---|---|---|
|0. Начальное объединение|Принят|Согласованные develop/gitlinks и merge commits.|
|1. Доказательства и параметры|Частично|Исторические anchors и реестры есть; semantic/effective-factor review, inherited properties и unknowns не закрыты.|
|2. Изолированные сборки/runtime|Частично|Runtime/manifests/учёт процессов работают; полная resource/build/fault matrix открыта.|
|3. Наблюдения/scorer|Частично|Strict IDs, finite/completeness и реальный аудит проверены; все применимые legacy adapters/режимы ещё не приняты.|
|4. Lifecycle/storage|Частично|Реальные native fixtures/effective graph/physics checks; вся fresh/reuse/Copy/Load/Build/growth/heterogeneous матрица открыта.|
|5. Export/import|Частично|Полное состояние, Train→Test, boundary continuation работают; вся физика/связи и independent corpus replay не приняты.|
|6. Общий контроллер|Частично|Общий native service, configured controller, Classic/Branch adapters работают; legacy/V2 A/B, остаточное дублирование и multirate открыты.|
|7. Алгоритмы|Частично|Measured bounded L/Ns/Rs search, revision-bound observations и fresh final gate реализованы. Полная matrix/C-search и проблема merged responses открыты; общего сертификата в текущих cold опытах нет.|
|8. Conversion/PostTune/calibration|Частично|Versioned solo/recognition, транзакции, actual threshold/frozen проверки; все режимы/rollback/interruption/independent evaluation не приняты.|
|9. Пакет/миграция|Частично|Корневой CLI и357 migration entries проверены; complete=false, часть Bin-инструментов/callers остаётся.|
|10. Runner/provenance/publish|Частично|Owned groups/leases, ConditionSpec и fail-closed публикация; полная fault/effective-factor matrix открыта.|
|11. Научная матрица|Частично|Исторические replay/cold, современные Train/Test и графики есть; итоговое legacy/V2/order/ITI/reset/physics сравнение открыто.|
|12. Документация|Частично|Текущая сводка отделена от исторических отчётов; финальная root/PulseLib/Bin/config/ClDesc сверка и миграция не завершены.|

## Подтверждённые текущие задания

| Worker | Job / owned PID | Состояние на11:13 UTC |
|---|---|---|
|M40|s11-fast-full-training-threshold-m40-a1 /2389747|Жив. Реальный baseline repeat100 и один заранее объявленный threshold для новой terminal21600; итог неизвестен.|
|M40|s11-fast-full-training-peak-report-m40-a1 /2452731|Жив. Read-only сравнение7200/21600 с native zoom около вершины; source c60560a38eeda634947ae5cd3ef3872ee4258b6f.|
|Elder|s11-restored-full-training-frozen8-report-elder-a1 /1858341|Жив. Независимые DATA/scorer и полный Soma/LT report новой frozen8 после byte-exact restore; source c60560a38eeda634947ae5cd3ef3872ee4258b6f.|

## Следующая научная работа

1. Завершить уже работающий actual threshold Test terminal21600 по [объявленному протоколу](FastN1FullTrainingRecognitionProtocol-20261116.ru.md). Опубликовать результат независимо от качества, без второго порога ради улучшения счёта.
2. Принять независимый frozen8 replay и новые графики; просмотреть выбранные оригиналы. Это анализ уже полученных данных, не новый Train.
3. Разобрать ограничение300с измерительной группы на длинной структуре и объявить следующий конечный бюджет до запуска. Не считать это физическим пределом и не ослаблять математические допуски. После изменения общей модели нужен свежий контроль затронутых входов и финальная проверка всех входов.
4. Завершать исходную режимную/физическую/order/ITI/reset матрицу, миграцию и документацию. Число инженерных PASS не измеряет готовность классификатора. Надёжного срока получения успешного распознавания пока нет.

Техническая очистка истории завершена. Тяжёлые primary, модели и полные галереи — /media/user/Data/Nmsdk-StructTrainExpArchive на M40; [Samba](//10.245.1.12/Nmsdk-StructTrainExpArchive). В Git только код, настройки, документы и компактные refs. [Подробная карта реализации](ImplementationStatus.ru.md), [исходный план](RefactoringPlan.ru.md), [исходный аудит](PlanCompletionAudit-2026-10-25.ru.md).
