# Найденная причина остановки Branch N4 —12.11.2026

Все пять отклонённых input2 измерений содержали допустимый закреплённый пик. Прогнозное окно прошло правее него. В первой ошибке пик находится на sample604, окно начинается на605:разница0.5ms. Полная запись и omission controls подтверждают именно третий импульс; самый высокий пик второго импульса не подставляется вместо него.

[Методы, таблица всех пяти отказов, проверки2/2 и исходный replay](ValidationPlans/M40RecoveryN4WindowAnalysisA1-20261112/RESULT.ru.md). Это подтверждённый дефект области поиска измерителя; исходный Train остаётся неуспешным.

Синий — raw Soma1.SumPotential (CSV soma0), оранжевый — фактический вход отдельной пробы, фиолетовый — исходное прогнозное окно. В omit-2 отклик на третий импульс исчезает; в остальных controls сохраняется. В узком zoom вход уже закончился, поэтому он там равен нулю. Все8выбранных PNG просмотрены; полный кэш24figures остаётся на M40.

## Первая ошибка:обзор

![Group20 overview](../../../Reports/StructTrain/TimeLearner/RecoveryN4BranchWindowDiagnostics-20261112/group-000020-soma-000-overview.png)

## Граница окна в native-масштабе

![Group20 native edge](../../../Reports/StructTrain/TimeLearner/RecoveryN4BranchWindowDiagnostics-20261112/group-000020-soma-000-window-left-native.png)

## Последняя ошибка

![Group28 detail](../../../Reports/StructTrain/TimeLearner/RecoveryN4BranchWindowDiagnostics-20261112/group-000028-soma-000-detail.png)

[Исправление для нового запуска](ObservationDomainWindowFix-20261112.ru.md):измерять закреплённые basins в полном записанном домене, сохраняя принадлежность импульсу, физику, CapturedPerInput, допуски и бюджеты. Исправление требует отдельной серверной приёмки и нового cold Train; результаты исходного запуска не переписываются.
