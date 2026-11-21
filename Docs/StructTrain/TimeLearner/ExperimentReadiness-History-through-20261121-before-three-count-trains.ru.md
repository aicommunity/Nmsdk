> Исторический снимок до освобождения места на Elder и запуска третьего Train.
> Для текущего состояния используется ExperimentReadiness.ru.md.

# Научные результаты TimeLearner и готовность — 16 ноября 2026

Текущий запуск: два настоящих Train — Classic M=4 на M40 и Branch M=4 на
Windows; оба с нормализацией числом синапсов, итог ещё неизвестен.
[Постановка и фактические проверки](MatchedClassicCountTraining-20261121.ru.md).
На Elder подтверждены исходный граф и действие Ns2; длинный Train ждёт места,
полный архив прежнего Classic Train уже перенесён на M40, исходники сохранены. Нижеследующие датированные
состояния работающих заданий относятся к своим снимкам.


Подтверждён реальный Same-Matrix результат **7/8 с обнаружением target: TP=1, FP=1, FN=0, TN=6**. Он получен на M40 и точно воспроизведён на Elder с теми же сохранённой моделью и порогом. Исходный Train не завершился с общим сертификатом сходимости. [Все8 положений target проверены](FastN1FrozenOrderScientificReport-20261116.ru.md): каждый порядок дал TP1/FP1/FN0/TN6 в reset-per-trial. ITI и continuous stream пока не приняты.

Полный исходный план активен: полностью принят этап0, этапы1–12 частичны. Численные исходы, качество распознавания и приёмка реализации учитываются отдельно. [Сверка полного плана](CurrentStatus-20261116.ru.md), [подробная карта реализации](ImplementationStatus.ru.md), [исходный план](RefactoringPlan.ru.md).

## Подтверждённые современные результаты

| Модель и опыт | Фактический исход | Область вывода |
|---|---|---|
|[Fast N1 terminal21600, actual threshold](FastN1FullTrainingRecognitionScientificReport-20261116.ru.md)|TP1/FP1/FN0/TN6, threshold0.054353792695896797. Target event0.493с, последний вход0.490с. Единственный FP уrow4 до последнего входа.|Одна остановленная модель, исходные8 паттернов, reset_per_trial, полные2с окна, Same-Matrix. Общего TrainingCertificate нет.|
|[Реальный повтор этой модели на Elder](FastN1FullTrainingElderNativeRepeat-20261116.ru.md)|Те же TP1/FP1/FN0/TN6. Все4001 отсчётов каждого из8 откликов равны M40, max absolute difference0.0; native baseline phase закрыта.|Новое исполнение сохранённой модели на втором сервере. Повторного обучения и независимой scientific partition нет. Вся серия64 принята1/1, native/controller/collector закрыты; в каждом порядке TP1/FP1/FN0/TN6.|
|[Fast N1 terminal21600, исходный threshold100](FastN1FullTrainingRecognitionScientificReport-20261116.ru.md)|TP0/FP0/FN1/TN7, полное молчание.|Accuracy7/8 здесь означает пропуск target и не подтверждает успешную детекцию.|
|[Fast N1 terminal7200](FastN1RecognitionScientificReport-20261116.ru.md)|Actual threshold0.0560090535350351: TP1/FP3/FN0/TN4, target event0.2535с раньше последнего входа0.490с.|Другая terminal-модель и отдельно выбранный один порог. Сравнение с terminal21600 не является причинным A/B при фиксированном пороге.|
|[Умеренный Stock Branch N1](N1ModerateRecognitionScientificReport-20261116.ru.md)|Actual Same-Matrix TP1/FP6/FN0/TN1; target до последнего входа.|Успешный классификатор полного паттерна не подтверждён.|
|[PSI2.5 Branch N1](PresynapticRecognitionScientificReport-20261116.ru.md)|Actual threshold0.189057455929736: TP1/FP6/FN0/TN1; оба target event до последнего входа.|Результат конкретной остановленной модели. Он не доказывает общую бесполезность PSI.|

У Fast terminal21600 false response rate1/7=14.29%, precision1/2=50%. Меньшее число FP и более поздний target event — наблюдаемые свойства этого опыта; перенос на другие паттерны и протоколы требует новых проверок. Ни целевой ответ, ни FP не выводятся из offline sweep непороговых CSV: приведены реальные native spikes после фактической установки объявленного порога.

[Холодный Train terminal21600](FastN1FullTrainingScientificReport-20261116.ru.md):31 scalar candidate, один локально jointly-ready input2. Общее wall21600с не исчерпано; остановила группа с300с wall limit. Последняя незавершённая группа измеряла anchor input3 на L[201,201,121,1], а не input1. Отсутствующее измерение input1 нельзя подменять остатком при L124. Локальная готовность одного входа до последующих правок модели не заменяет свежую финальную проверку всех входов.

## Что выполняется

Последняя проверка live handles —16.11.2026 около16:10UTC. Сбой наблюдения или потеря VPN не означают остановку задания и не разрешают дублирующий запуск.

| Worker | Исходный job и owned/native PID | Подтверждённое состояние |
|---|---|---|
|M40|s11-fast-bracket-groupwall600-m40-a1;2814832/2822759 закрыты|[OOM при native лимите4 GiB](FastN1GroupWall600OOM-20261116.ru.md), process_error. 759 raw пар сохранены; финальная модель и scalar summary отсутствуют. Новый Train/Test не запущен.|
|Elder|s11-frozen-order-native-elder-a2;2352165 закрыт|[Вся серия64 завершена и опубликована](FastN1FrozenOrderScientificReport-20261116.ru.md). Все8 положений target: TP1/FP1/FN0/TN6, один и тот же phasea-row-4. Графики всех64 ещё готовятся.|

[Декларация нового Train](FastN1GroupWall600Preparation-20261116.json), [протокол order A2](FrozenDiagnosticOrderLaunch-20261116.ru.md). Работающие source/runtime/output bindings не обновляются. На Elder закрыты оба native этапа, родительский controller и коллектор; полная приёмка64 и primary опубликованы. На M40 аварийный Train и его коллектор закрыты; валидация коллектора не меняет исход Train.

## Что можно читать и смотреть

- [Основной Fast terminal21600 научный отчёт](FastN1FullTrainingRecognitionScientificReport-20261116.ru.md): actual результаты всех8 паттернов, фактические spike/input timestamps, ссылки на Soma с входными импульсами и native LT details. Все16 baseline/candidate observations полны и модель frozen; primary58.74MB и actual candidate report1287PNG опубликованы. Вручную просмотрены18 выбранных originals всех8 паттернов, а не вся галерея.
- [Train7200/21600 и увеличения записанных максимумов](FastN1FullTrainingScientificReport-20261116.ru.md): полные/omission/repeat кривые, неполная terminal group явно показана как неполная. Новый40-view выпуск принят;8 новых peak details просмотрены,32 прежних PNG сохранены.
- [Независимый replay всего threshold primary на Elder](FastN1FullTrainingThresholdIndependentReplayAcceptance-20261116.json):1423 logical members, production DATA/scorer1/1, исходные и повторные baseline waveforms равны. Это повторный анализ тех же данных; [native повтор8](FastN1FullTrainingElderNativeRepeat-20261116.ru.md) отдельно подтверждает новое исполнение модели.
- [Stock/PSI cold comparison](PresynapticColdScientificReport-20261116.ru.md) и [PSI actual recognition](PresynapticRecognitionScientificReport-20261116.ru.md): принятые отрицательные результаты, ограничения и временные графики. Они завершены; прежние записи «ожидается» относятся к более ранним снимкам.

Графики строятся по записанным временным рядам с реальными входными импульсами и событиями LT. Полные окна сохраняются; дополнительные positive-Y детали явно сообщают о clipping отрицательного recovery. Native детали показывают не менее8px на timestep. Для текущего Fast3 используется обычный LTZone.Potential; LTMembrane отсутствует. Значения потенциалов указаны в model units, SI не подтверждена.

## Следующие научные проверки и ограничения

1. Проверить и исправить сохранение большой модели после подтверждённого OOM groupwall600 при native лимите4 GiB. Декларировать отдельно память native и controller, проверить пик памяти экспорта и checkpoint завершённых границ. До приёмки не повторять шестичасовой Train. Финальной модели аварийного запуска нет, Test по шаблону запрещён.
2. Завершить новую читаемую галерею всех64 уже принятых order A2 наблюдений. Классификации по каждому положению и полный primary опубликованы; дополнительно проверить timing на новых кривых. Fixed threshold/model по этим результатам не подбирать заново.
3. Отдельными заранее объявленными протоколами проверить ITI и reset_per_trial/continuous stream, затем независимый frozen Test. Одна Same-Matrix матрица не создаёт независимой оценки обобщения. Детерминированные повторы одной модели не считаются независимыми обучениями.
4. Завершать legacy/V2 A/B и обязательную матрицу исходного плана: N0/N1, физика/storage, размеры, частоты, bounds/quantization, inhibition/reset, C-trim/PostTune/calibration и infrastructure fault cases. Текущие engineering SDK PASS не закрывают эту область.

При Train выбирается максимум закреплённого импульса; раздельная ранняя вершина с хвостовым влиянием допустима, настоящее слияние остаётся ambiguous. При Test рассматриваются весь наблюдаемый отклик и фактические spike events, с отдельным анализом времени относительно последнего входа. Прогноз задержки и максимум всей пачки не заменяют назначение пика при обучении.

Августовские визуально подтверждённые4/8–6/8 остаются рабочими наблюдениями своего исходного протокола. Порядок и увеличенный ITI тогда не проверялись; современные результаты их не отменяют. [Исторический cold replay](HistoricalAugustColdStart.ru.md). SeriesD автоматически не возобновляется. Научный результат8/8 не является условием завершения рефакторинга.

## Хранение и история сводки

Тяжёлые primary, модели и полные галереи хранятся только в /media/user/Data/Nmsdk-StructTrainExpArchive на M40, [общий доступ](//10.245.1.12/Nmsdk-StructTrainExpArchive). В Git — код, декларации, текстовые отчёты и компактные проверяемые refs; root branches остаются целостными без доступа к архиву. [Политика и восстановление](ExternalExperimentArchive.ru.md).

[Предыдущий текст сводки сохранён как исторический снимок](ExperimentReadiness-History-through-20261116-before-fast7.ru.md). Его результаты и ссылки не удалены; старые текущие статусы не описывают сегодняшние задания. Для полного состояния реализации используется одна [поддерживаемая сводка](CurrentStatus-20261121.ru.md).
