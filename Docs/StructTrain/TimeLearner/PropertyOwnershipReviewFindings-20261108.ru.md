# Два findings для следующего property/lifecycle реестра

Read-only source review root `9a782e211a7321b2253dacb018d2235a67b8a445`,
PulseLib `fcc3fed0dc63fc0d8ae8dcfdb0f85bd5d004baf8`.
Эти пункты не исправлены calibration/PostTune reconciliation. Новых numerical
tests, запусков компонентов и утверждения о полной поддержке connected commands нет.

## PROPERTY-OWNERSHIP-STEP-001: legacy setter может писать native N0 bank

**Наблюдаемый source факт.** `Core/NNeuronTimeLearner.cpp:3061` и
`Core/NNeuronTimeLearnerBranch.cpp:3811`, SetSynapseResistanceStep: после
проверки N1/пустого bank код перебирает extra contacts k>=2 и записывает
`synapse->Resistance=value` (`:3076` / `:3826`). NativeTrainingOwned,
NativeRecognition и NativeModelDeclaration перед записью не проверяются.
Контакт должен разрешаться как NPulseSynapse; нельзя распространять этот
вывод на все допустимые synapse classes без runtime-проверки.

В отличие от этого, TipSynapseResistance setter при native ownership принимает
только прежний vector (`Core/NNeuronTimeLearner.cpp:3188`, Branch `:3938`).
Native parameter editor входит через явный edit depth:
`Core/TimeLearner/NativeTrainingBindings.h:24`. Модельная revision читается с
реального neuron/source (`:16`), поэтому поздний revision rejection может
обнаружить вмешательство. Нельзя утверждать, что этот setter уже позволил
ложный certificate: такое поведение здесь не воспроизводилось.

**Неопределённость и решение.** Назначение legacyStep после native ownership
может поменять physical bank до typed rejection. Требуется явно определить:
отклонять такую команду атомарно либо разрешать только через согласованный
editor. Общую Rdk семантику SetData/Build менять для этого не следует.

**Необходимые серверные controls.** Classic/Branch, N0 с Ns>=2 и совместимым
synapse class: после construction, во время reference/search, после завершения
и в frozen recognition назначить другой finite/positive legacyStep. При
отклонении сравнить все bank Rs, full model identity, references/certificate
и sampler state до/после; child Calculate не должен скрыть предшествующий edit.
Отдельно positive legacy N0 и no-effect N1 controls, heterogeneous bank и
несовместимый synapse class. Проверка только первого tip Rs недостаточна.

## PROPERTY-CONTROL-RISING-001: external rising-edge restart требует решения

**Наблюдаемый source факт.** После native ownership V2 ordinary setter
IsNeedToTrain делает ResetControl на false→true:
`Core/NNeuronTimeLearner.cpp:2795`, Branch `:3561`.
Автоматический старт общего lifecycle требует уже Idle service:
`Core/TimeLearner/NativeLearnerLifecycle.h:52`. Прямой контроль действующей
службы отдельно читает trainingRequested:
`Core/TimeLearner/NativeTrainingService.cpp:207` и `:278`.

**Что уже покрыто.** Нельзя повторно объявлять connected falling-edge stop
отсутствующим: root `Tests/Integration/Libraries/Test_PulseLib_NativeModelEditor.cpp:4223`
содержит реальные ConnectedStop controls, SetPointer в `:4239`, проверку
Finished/ExternalStop и сохранения параметров в `:4289`. Эти tests включают
ранний/частичный/search/after-sample stop и удержание true.
`NativeTrainingService.ExactAutoCompletionResetWarmRestartAndRetarget` (`:4633`)
использует Reset и явный BeginNativeTraining; он не доказывает connected
false→true restart после Finished.

**Неопределённость и решение.** Для supplier/SetDataDirect false→true callback
ordinary setter не является универсальным наблюдателем команды. По текущему
dispatch Finished сам по себе не превращается в Idle. Это кандидат на пробел
контракта external commands, а не утверждение, что connected restart уже
объявлен поддерживаемым или что все supplier implementations ведут себя одинаково.
Нужно либо объявить и проверить rising-edge semantics в controller, либо
явно отклонять неподдерживаемый способ управления на admission. Не записывать
значение обратно в чужой supplier и не менять общий UProperty протокол.

**Необходимые серверные controls.** Classic/Branch × CalculateMode0/1 ×
ordinary assignment/connected supplier/external data source/SetDataDirect.
Отдельно Finished Exact, ExternalStop и unresolved boundary; затем false→true
без Reset/Build/explicit Begin. Проверять фактические SessionAttempt, Idle/start
transition, сохранение model/references, новое request identity, отсутствие
старого сертификата у новой попытки и неизменность связи supplier. Равный
постоянный supplier и существующие falling-stop случаи — обязательные controls.
До решения этот пункт не должен автоматически стать active scientific factor.
