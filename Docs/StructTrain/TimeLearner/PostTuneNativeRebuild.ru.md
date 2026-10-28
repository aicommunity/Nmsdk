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
синапсами при 2000/20000 Гц: прежний rebuild принудительно создавал только один
синапс на сегменте. Новый clone сохраняет обученное число и граф. Analyze CLI
получает format=posttune-reconstruction, с null scientific verdict.

Проверка A3 ещё не выполнена. Эти cases не заменяют полный поиск SearchSynthetic,
транзакцию выбора/отката всех PostTune candidates, научную оценку, реальную
калибровку порога или независимый Test. Они адресуют конкретную реконструкцию
Branch; legacy математическая цель и правила выбора режимов этим не меняются.
