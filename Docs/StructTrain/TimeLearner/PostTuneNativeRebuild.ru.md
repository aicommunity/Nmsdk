# PostTune: реконструкция фактического графа

Рабочая ветка `stage08/posttune-native-rebuild` основана на develop и включает
через merge prerequisite recognition transport. Подэтап не завершает весь
PostTune, калибровку или этап 8.

## Подтверждённый риск старого пути

`NNeuronTimeLearnerBranch::RebuildCableForPostTuneProbes` удалял neuron и создавал
его заново из класса. Единственный captured parent C заменялся на 1e-9, если
отсутствовал. Затем выполнялись uniform overrides, ApplyElementDefaults и
повторный «wake-pass» Build. Такой путь не переносит полную heterogeneous
child physics и обученные индивидуальные значения. Возвращаемый helper status
в EnterPostTunePhase игнорировался.

## Рабочая замена

Общий `ReconstructNativeLearnerNeuron` использует production
`ClonePhysicalGraphForEdit`: native Save/Load/Build/Init фактического графа,
явные stimulus ports, полную semantic identity и свежую физическую динамику.
Это не динамический checkpoint. Dataset и storage images не заменяются.

Перед заменой проверяются внешние listeners. Старый объект остаётся занят в
storage до успешного attachment, восстановления порядка owner и identity
readback. При ошибке attachment возвращаются прежний объект и owner order;
новый освобождается штатно с BreakLinks. При невозможности rollback результат
явно Failed/modelMayHaveChanged, а не фиктивный успех. Caller обновляет alias
Neuron также после rollback.

Branch после реконструкции применяет обычную маршрутизацию PostTune и Reset
dataset/neuron перед пробой. Parent C не подставляется, общая физика не
перезаписывается. Не добавляются Calculate, Default или «пробуждающие» Build.
Неуспешная реконструкция останавливает PostTune как SetupFailure с Complete=false.
Bool Build/Calculate/Reset не используются как протокол ошибок обучения.

## Проверки и оставшиеся ограничения

Подготовлены production integration cases для Off/CanonRmin/FlatLastR/KeepDone,
исходной SearchSynthetic candidate, 2000/20000 Гц, heterogeneous child C при
нулевом parent C, реального отказа attachment и внешнего listener. Сравниваются
весь graph/параметры, links/order и реальные до/после stimulus/soma waveforms.
Часы возвращаются к одинаковой test-only стартовой точке только внутри fixture;
production learner часы не меняет.

A1 normal сборка прошла; все восемь cases были корректно отклонены до
реконструкции: fixture пытался запустить native solo probe при активном PostTune
(`concurrent_native_posttune`). Это ошибка постановки fixture, защита не меняется.
A2 выполняет параллельное предъявление обычным root scheduler без второго
контроллера: spec сохраняется до ticks, raw CSV и complete observation после
полного окна. Independent auditor сверяет semantic graph, heterogeneous C,
свежую пару trial IDs, stimulus timestamps/число импульсов, sampling gaps и
полные до/после waveforms. Native execution и scientific verdict он не подменяет.

A2 normal и ASan: 8/8 native cases прошли, graph/C/Rs/order и waveforms
сохранились, injection rollback и listener guard сработали. Но independent
Python stage отверг все восемь positive subcases по stimulus_count_mismatch:
Dataset по умолчанию повторял пачку, а spec подразумевал одиночное предъявление.
CPP pass не подменяет валидность протокола; A2 сохранён как pipeline failure.

A3 задаёт штатный StateGeneration=2, AdvanceSampleAfterBurst=true,
LoopSamples=false и продолжает окно до declared end после окончания генерации.
Эти значения записываются до ticks. Добавлены N0 controls с тремя фактическими
синапсами при 2000/20000 Гц: прежний rebuild принудительно применял
single-input helper; baseline также выявил несогласованные Rs в N0 bank. Новый clone сохраняет обученное число и граф. Analyze CLI
получает format=posttune-reconstruction, с null scientific verdict.

A3 на обоих workers: 8 pass / 2 fixture failures. Новые N0 cases пытались
изменить Ns до consumed-probe boundary; native guard верно запретил это.
A4 создаёт Ns=3 в исходном ModelSpec штатно, без обхода контроля.

## Подтверждённые A4/A5 и baseline

Native root `e7ee0104f5677e812ffd3b91c45074667ba1ffca`, PulseLib
`d862127d849953b2c7928e87c803a016a0da06d9`: normal Elder-1 и ASan M40,
по 10/10 C++ cases, 7/7 Python tests, 10090 пар / 20180 raw waveform rows.
Граф, параметры, полные окна и реальные времена/число стимулов согласованны.
Native scheduler считает дерево один раз на tick. Модель frozen до/после.

Explicit baseline root `8d23ed533b23f0bf25082545a174b5621292c794` фиксирует
старую PulseLib `593b69cf3754c85013527522757f380c04e2efe5` и тот же fixture.
На каждом worker восемь выбранных mode/physics/N0 cases отказали после старого
rebuild. Потеря heterogeneous physics/identity и несогласованные Rs в N0 bank
подтверждены runtime. Baseline A1 с двумя ошибками N0 setup сохранён отдельно.
Причинной связи с историческими августовскими результатами это не устанавливает.

[Elder artifacts](../../../Reports/StructTrain/TimeLearner/s08-posttune-rebuild-elder1/README.md),
последний report commit `a1c9acba5e8b1b6b72f33ce6c3bee64b929c1bb2`;
[M40 artifacts](../../../Reports/StructTrain/TimeLearner/s08-posttune-rebuild-m40/README.md),
commit `10aae61f14202be06d4571705c4aa0d8aa40af3f`. На каждом по 483 stored /
481 raw hashes проверены локально. Live executable mapping snapshot: 26 файлов
на Elder и 73 на M40; это снимок одного момента, не полная история загрузок.

Python-only A5 `1afdb2669363755e9ffd109b86d118598d00b8b1` проверил те же
immutable A4 данные: по 7/7 tests и все 10 cases / 10090 пар. Generic auditor
не требует fixture-ёмкостей 1.3/1.7/2.3 nF от произвольной модели: эти positive
controls остаются в C++/Python integration tests. Native расчёт не повторялся.
Старые A1/A2/A3 failures не переписаны, не переоценены как passed pipeline.

## Открытый объём

Транзакция пока охватывает только замену фактического physical graph.
EnterPostTunePhase по-прежнему применяет mode adjustments до реконструкции;
полный возврат к исходному Solo/Recognition при отказе последующего кандидата
пока не реализован. Подмена training InputPattern временным stimulus исправлена отдельным проверенным
[подэтапом](PostTuneTransientStimulus.ru.md); произвольный retarget остаётся открыт:
его следует заменить отдельным transient stimulus без retarget captured goal.

Эти cases не заменяют полный поиск SearchSynthetic,
транзакцию выбора/отката всех PostTune candidates, научную оценку, реальную
калибровку порога или независимый Test. Они адресуют конкретную реконструкцию
Branch; legacy математическая цель и правила выбора режимов этим не меняются.
