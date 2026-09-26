# Повторный аудит TimeLearner и StructTrain Cold

Дата: 2026-09-26. Проверены root-коммит `23e4e8231e2bd1c7201f724fd5510f824c229dad` и состояние на текущем root HEAD `e2c52d0271193dfc853bcab4da07a4cb813362b8`; текущие gitlinks: PulseLib `8d429e7463850b06163f177b42b17977baa38e45`, Bin `a99c7c6af182bafa03119ed4ebcd599e20ec2b94`.

## Вывод

В текущем коде найден конкретный дефект классического `NNeuronTimeLearner`: допуск амплитуды `1e-5` объявлен целым типом и фактически становится нулём. Это может мешать завершению нормализации и удерживать `IsNeedToTrain=1` в Cold AsymRm-прогонах. Дефект уже присутствовал в исходниках на момент аудиторского коммита; он не возник из последних исправлений.

Для `NNeuronTimeLearnerBranch` отдельный нерешённый результат остаётся реальным: завершённый br25 soft-cold получил `NonSeparable`. Проверки исключили несколько простых объяснений, но не установили корень проблемы. По имеющимся данным нельзя заключить, что сломан весь алгоритм роста ветвей.

## Находки

### TL-01 — P1: epsilon классического learner обнуляется при преобразовании в `int`

В `NNeuronTimeLearner.h` задано `static constexpr int kAmpNormEps = 1e-5`. Преобразование константы к `int` даёт `0`. Значение используется как tolerance в `ChangeSynapseResistanceStatus` и `AllSynapsesNormalized`; часть критериев завершения тем самым требует точного равенства амплитуд. MSVC подтверждает проблему предупреждением C4244. Branch-класс объявляет такую же константу как `double`.

Комментарий рядом с константой прямо связывает её с Cold stalls около `6e-6` и незакрытым `IsNeedToTrain`. Это согласуется с незавершёнными AsymRm wave-C случаями (`asym50_preinh`, `asym100_preinh`), но из-за отсутствия run bundles нельзя приписать этому дефекту каждый конкретный отказ.

Ссылки: [классический epsilon](../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearner.h#L451), [проверка завершения нормализации](../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearner.cpp#L3486), [корректный тип в Branch](../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearnerBranch.h#L464), [AsymRm wave C](../../../Bin/Configs/SpikeSamples/StructTrain/SUCCESSFUL_EXPERIMENTS.md#L184).

Происхождение: значение `int` присутствует в PulseLib baseline, привязанном к аудиторскому root-коммиту. Следует заменить тип на `double` и добавить проверку, которая не позволит ненулевому `1e-5` молча превратиться в ноль.

### TL-02 — P2: Cold preflight Branch не отражает фактическое начальное состояние после reset

Python helper проверяет в XML `DendriteLength=1 1 1 1` до запуска. При `ResetToUntrainedState=1` C++ reset Branch устанавливает длину последней опорной ветви в `0`. Это может быть намеренным устройством reference dendrite, но harness не фиксирует runtime-вектор сразу после `AReset`; поэтому указанное в preflight состояние не доказывает фактическое начальное состояние обучения.

Ссылки: [XML preflight](../../../Bin/Configs/SpikeSamples/StructTrain/scripts/repro_cold_lib.py#L215), [Branch reset](../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearnerBranch.cpp#L1846).

### TL-03 — P2: Branch Cold остаётся неуспешным после устранения save/Need рассинхронизации

После синхронизации текущего Train-флага с Parameters результат br25 soft-cold всё ещё `NonSeparable`. Keep TipR также не прошёл; сравнение soft/strip и AutoScale не дало материального изменения. Следовательно, отказ нельзя объяснить только Canon TipR, неиспользуемыми сегментами модели или выбранным inter-iteration gap. Морфогенез Branch и причины отсутствия отделимого landscape остаются открытым вопросом.

Методы `ChangeDendriteStatus` и `FinishTrainingIteration` в PulseLib diff от аудиторского среза до текущего HEAD не менялись; изменения вокруг ученика относятся преимущественно к измерению и PostTune. Результат Branch — подтверждённый cold quality failure, но не доказательство регрессии от этих правок или общей поломки Branch learner.

Ссылки: [результаты soft-cold и H1–H4](../TimeLearner-2026-09-24-review/EXPERIMENTS_AFTER_FIXES.ru.md#L85), [решение по H3/H4 и D4](../TimeLearner-2026-09-24-review/TAILS_EXEC.ru.md#L96), [ChangeDendriteStatus](../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearnerBranch.cpp#L3513), [FinishTrainingIteration](../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearnerBranch.cpp#L5162).

### TL-04 — P2: статусы 14 wave-C случаев смешивают отказы обучения и неполные запуски

14 запущенных C1 случаев помечены `FAIL`, но таблица содержит несколько `train=exited`, в том числе случаи с `gate_rc=0`, где verifier отказал из-за неполного Train. Другие случаи дошли до gate и завершились `gate_rc=1`. Поэтому 14 verifier FAIL нельзя считать 14 независимыми доказательствами дефекта learner. GoldTest/SkipTrainGold запускаются на готовых весах и не являются контролем Cold-обучения. Остаток C1 и C2 отмечены как DEFER.

Ссылки: [таблица результатов](../../../Bin/Configs/SpikeSamples/StructTrain/EXPERIMENTS.md#L238), [подробные причины и DEFER](../../../Bin/Configs/SpikeSamples/StructTrain/SUCCESSFUL_EXPERIMENTS.md#L278).

### TL-05 — P2: недостаточно архивных данных для независимой проверки wave C

В checkout отсутствуют 14 bundle-директорий, на которые ссылаются таблицы wave C; локально доступны только шесть более ранних run bundles. `_repro/SOFTCOLD_C_rcs.txt` содержит имена случаев и `rc`, но не stdout/stderr, параметры после reset и полные артефакты gate. Повторная SSH-проверка `10.245.1.11:22` завершилась таймаутом TCP до аутентификации, поэтому remote `/home/user/Nmsdk/Bin` проверить не удалось.

### TL-06 — P2: несогласованная provenance и текст реестров

Заголовки `EXPERIMENTS.md` и `SUCCESSFUL_EXPERIMENTS.md` указывают один Console SHA и PulseLib, но разные Bin SHA (`1a664a2` и `fbfdcf7`); текущий Bin HEAD — `a99c7c6`. Требуется явно различить commit исходников бинарника и commit редакции документа. Кроме того, вводная `SUCCESSFUL_EXPERIMENTS.md` утверждает, что полные FAIL-строки есть только в `EXPERIMENTS.md`, хотя подробные причины размещены также в `SUCCESSFUL_EXPERIMENTS.md`; wave-C строки в `EXPERIMENTS.md` дают главным образом `rc` и ссылку.

Ссылки: [заголовок EXPERIMENTS](../../../Bin/Configs/SpikeSamples/StructTrain/EXPERIMENTS.md#L3), [заголовок SUCCESSFUL](../../../Bin/Configs/SpikeSamples/StructTrain/SUCCESSFUL_EXPERIMENTS.md#L3), [противоречивая вводная](../../../Bin/Configs/SpikeSamples/StructTrain/SUCCESSFUL_EXPERIMENTS.md#L6).

## Остатки предыдущего аудита

В актуальном статусе R01 reachability в полном scheduler остаётся `not_observed`; для R04 два полных последовательных training cycle подтверждены только probe-уровнем. Эти остатки не доказаны как причина wave-C отказов, но ограничивают полноту аудита жизненного цикла и границ sample.

Ссылка: [status.json: R01/R04](../TimeLearner-2026-09-24-review/status.json#L30).

## Проверки и ограничения

- Существующие Python harness unit tests: 24/24 PASS.
- Windows Release `NeuroModelerConsole` собран и слинкован. На `kAmpNormEps` повторяется предупреждение C4244. Это подтверждает компиляцию Windows-конфигурации, но не заменяет Linux-прогоны.
- Linux wave-C прогоны повторно не выполнены: SSH-порт недоступен из текущего окружения, run bundles отсутствуют локально.
- В рамках аудита код и конфигурации не изменялись.

## Рекомендуемые следующие действия

1. Исправить тип `kAmpNormEps` классического learner на `double` и добавить регрессионную проверку ненулевого epsilon.
2. Повторить минимум затронутые Cold AsymRm cases на чистом workdir с полным provenance и Train output.
3. В harness сохранять runtime state сразу после `ResetToUntrainedState` и согласовать обозначение Branch reference length с ожидаемым `L`.
4. Повторить Branch br25 Cold/контроли на Ubuntu и сохранить полные bundles; до этого не приписывать Branch NonSeparable конкретной причине.
