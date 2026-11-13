# Classic N4/N1: холодное обучение с recovery4, 14 ноября 2026

Холодное обучение завершилось со статусом **invalid_observation: rejected_candidate_window:ambiguous**. Получены14 допустимых измеренных кандидатов, но ни один не выполнил одновременно временной и амплитудный допуски. Общего сертификата обучения нет; классификация этой модели не оценивалась. Это отрицательный результат конкретного протокола, а не доказательство физической невозможности обучения или опровержение августовских визуальных4/8–6/8.

## Условия и полнота

Classic,4 входа, нормализация N1,2000Гц; stock-физика **без LTMembrane**. Проверены52 мембраны/104 канала, штатные threshold и feedback connections сохранены. Цель CapturedPerInput, опорный вход N−1, абсолютный амплитудный допуск1e−5, относительный0, SyncTolerance0.02с. Максимум при обучении относится к закреплённому импульсу: более высокий максимум всей пачки его не заменяет.

Ограничения native поиска:1800с wall time,128 поисковых проб,1280 изменений,128 кандидатов на вход,4 sweeps и4 восстановления после невалидной пробы. Отдельно разрешены300с на завершение процесса. Эти бюджеты не увеличивались. Прежний Classic с recovery16 является другим протоколом; его нельзя выдавать за same-budget A/B. Сопоставление с последним Branch recovery4 также не заменяет legacy/V2 A/B и полную матрицу физических режимов.

Native Train завершён за1272.6064461749047с. Production/DATA/physical проверка1/1 PASS1946.809с, внешний процесс completed/closed1970.9424482989125с, heartbeat errors0. PASS здесь означает успешную проверку исполнения и данных. Сохранены42 полные группы,252 native пробы по3601 отсчёту, всего907452 frames.

[Исходный результат и execution/job](ValidationPlans/M40N1CoupledClassicCold4A1-20261114/RESULT.ru.md), [весь compact primary](ValidationPlans/M40N1CoupledClassicPrimaryA1-20261114/RESULT.ru.md), [история измерений](../../../Reports/StructTrain/TimeLearner/ClassicCoupledCold4-20261114/figures/search-history.json), [выбор групп](../../../Reports/StructTrain/TimeLearner/ClassicCoupledCold4-20261114/figures/selection.json).

## Измеренные кандидаты и причина остановки

Зафиксированы38 поисковых проб и18 изменений. Пять отказов input0 относятся к L54,52,50,48,45; остальные длины1. Первые4 отказа сопровождались cursor_advanced, пятый — invalid_budget_stop. Это разные реально предъявленные структуры, а не повтор одной точки. Отвергнутые наблюдения не включены в14 измеренных кандидатов.

| Выбранная группа | Структура L, Rs всех входов86M, Ns=1 | Наблюдение |
|---|---|---|
|40, search70, epoch17|[13,1,1,1]|Ближайший по времени из реально измеренных кандидатов; оба допуска нарушены|
|14, search18|[54,1,1,1]|Первый отвергнутый кандидат: ambiguous|
|42, search74|[45,1,1,1]|Последний отвергнутый кандидат: ambiguous, остановка по invalid budget|

Для группы40 свежий anchor — группа39/search69. Временной остаток −0.36299999999999955с, амплитудный −0.010436733241943275. Назначенный пик0.005344708384487862 на0.1415с от начала пробы: ранняя отдельная вершина. При omit-0 она исчезает, при omit-1 сохраняется. Поздняя более высокая вершина не подставляется вместо неё. Это соответствует разрешённой пользователем отдельной ранней вершине при влиянии хвоста соседнего отклика; допустимость измерения не означает сходимость.

Для групп14 и42 выбранная область первого широкого максимума имеет no_necessary_input / highest_window_basin_peak_has_ambiguous_necessity. По объявленному критерию исключений максимум нельзя однозначно закрепить за input0; measured maximum остаётся null. Эти данные не дают права объявлять Exact, принудительно назначать общий максимум или делать вывод PhysicalInfeasible.

Терминальное состояние: L=[45,1,1,1], Rs=[86M,86M,86M,86M], Ns=[1,1,1,1]. Оно отличается от показанного измеренного L13. Model revision35d849faa2aaea5d2620f0fd59d9934c77760b7fde0dd49d3284539f69f68263, certificate=null, финальной общей проверки нет.

## Временные графики

В каждом оригинале шесть панелей: полная пачка до исключений, omit-0..3 и повтор полной пачки. Синим показан записанный потенциал соответствующей сомы, оранжевым — фактические входные импульсы. Время отсчитывается от начала каждой native пробы, окно0..1.8с. Все6 панелей одного изображения имеют одинаковый Y; между группами и сомами Y может различаться — сравнивайте числовые шкалы. Единицы потенциала native, SI не подтверждены.

Оригиналы2880×2880 пригодны для просмотра с увеличением. Обзор показывает форму волн и наложение входов; точность до отдельного native tick по картинке не заявляется. Имена soma-000..003 и заголовки soma0..3 используют нулевую индексацию.

Группа40, soma0: отдельная ранняя вершина и более высокий поздний максимум.

![Группа40: soma0, полная пачка и исключения](../../../Reports/StructTrain/TimeLearner/ClassicCoupledCold4-20261114/figures/group-000040-soma-000-overview.png)

Группа14, soma0: первый ambiguous-кандидат.

![Группа14: soma0, полная пачка и исключения](../../../Reports/StructTrain/TimeLearner/ClassicCoupledCold4-20261114/figures/group-000014-soma-000-overview.png)

Группа42, soma0: последний ambiguous-кандидат.

![Группа42: soma0, полная пачка и исключения](../../../Reports/StructTrain/TimeLearner/ClassicCoupledCold4-20261114/figures/group-000042-soma-000-overview.png)

| Группа | soma0 | soma1 | soma2 | soma3 |
|---|---|---|---|---|
|40|[оригинал](../../../Reports/StructTrain/TimeLearner/ClassicCoupledCold4-20261114/figures/group-000040-soma-000-overview.png)|[оригинал](../../../Reports/StructTrain/TimeLearner/ClassicCoupledCold4-20261114/figures/group-000040-soma-001-overview.png)|[оригинал](../../../Reports/StructTrain/TimeLearner/ClassicCoupledCold4-20261114/figures/group-000040-soma-002-overview.png)|[оригинал](../../../Reports/StructTrain/TimeLearner/ClassicCoupledCold4-20261114/figures/group-000040-soma-003-overview.png)|
|14|[оригинал](../../../Reports/StructTrain/TimeLearner/ClassicCoupledCold4-20261114/figures/group-000014-soma-000-overview.png)|[оригинал](../../../Reports/StructTrain/TimeLearner/ClassicCoupledCold4-20261114/figures/group-000014-soma-001-overview.png)|[оригинал](../../../Reports/StructTrain/TimeLearner/ClassicCoupledCold4-20261114/figures/group-000014-soma-002-overview.png)|[оригинал](../../../Reports/StructTrain/TimeLearner/ClassicCoupledCold4-20261114/figures/group-000014-soma-003-overview.png)|
|42|[оригинал](../../../Reports/StructTrain/TimeLearner/ClassicCoupledCold4-20261114/figures/group-000042-soma-000-overview.png)|[оригинал](../../../Reports/StructTrain/TimeLearner/ClassicCoupledCold4-20261114/figures/group-000042-soma-001-overview.png)|[оригинал](../../../Reports/StructTrain/TimeLearner/ClassicCoupledCold4-20261114/figures/group-000042-soma-002-overview.png)|[оригинал](../../../Reports/StructTrain/TimeLearner/ClassicCoupledCold4-20261114/figures/group-000042-soma-003-overview.png)|

Все12 выбранных обзорных PNG просмотрены вручную: подписи, шкалы, входы, шесть полных окон и формы откликов читаются. Полная галерея24PNG с overview/detail, SVG/PDF не проверялась вручную целиком. Исходный manifest visual_acceptance_complete=false сохранён без изменения; область этой ручной приёмки зафиксирована отдельно в [RESULT](ValidationPlans/M40ClassicCoupledTrainingReportA1-20261114/RESULT.ru.md). Дополнительный временной zoom не заявляется.

Это графики **обучающих и omission-проб**, а не тест всех классификационных паттернов. При будущем Test нужны отдельные полные окна всех паттернов и контроль неизменности модели.

## Воспроизводимость и ограничения

SDK root74e5d206d4b619fcf81f77f11b54ebec7b8f0f6e, Pulse7c6c94785af0c83104d348bb3b733ed1f149c8a8, runtime SHA256105ccc46bf2d23aa093ee6ec5fb088d9f33faa8e572f8191869f8cc279377a8a. Фактически исполненный native job SHA256d5cd229d8387ede1277e84d2a74cfe88624a001781f104f2d2ba75a6cfb566ae; это не hash внешнего prepared job.

Primary архив29,285,000B, SHA256dd633d3743f082fdb524bb07ec6c0c92197a1eb1ffb3fa2b784316cc146fdd4e,910 logical members. Независимый полный restore именно этого нового Classic-архива ещё не принят.12 выбранных исходных PNG занимают6,345,434B, контрольные суммы в [selected-originals.json](../../../Reports/StructTrain/TimeLearner/ClassicCoupledCold4-20261114/figures/selected-originals.json). Полный воспроизводимый cache: /media/user/Data/TimeLearnerRefactor/readbacks/s07-classic-coupled-training-report-m40-a1/worker/tmp/Classic-coupled-cold4-training-report.

Report-only production render1/1 PASS437.503с, внешний процесс completed/closed464.964194748085с, heartbeat errors0. Новый Train, Test, калибровка и изменение модели для рисунков не выполнялись. [Контроль и исходные receipts](ValidationPlans/M40ClassicCoupledTrainingReportA1-20261114/RESULT.ru.md).

Следующее научное решение должно опираться на различие двух случаев: допустимая отдельная ранняя вершина L13 и неоднозначный широкий максимум L54/L45. Увеличение recovery budget само по себе не исправляет принадлежность пика. Полная сходимость, распознавание и устойчивость к порядку/ITI остаются открытыми; этапы1–12 целиком не закрыты.
