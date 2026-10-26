# Этап 6: общий контроллер — работа продолжается

Полный общий контроллер и ControllerVersion=2 ещё не реализованы/не приняты.
Подготовка native A/B controls выявила TL-015 — неинициализированный live Neuron
в Classic. Сначала исправляется этот дефект владельца: LiveRebuildInit.ru.md.
Отдельно выявлен TL-016 — mixed effective rates после создания/growth legacy
элементов. Это ограничивает пригодность baseline для проверки нового контура.

Следующее исправление общего режима Rdk описано в
[FrequencyContract](FrequencyContract.ru.md). Для дальнейшего A/B используются
новые baseline с явным режимом и readback частот после структурных изменений;
старые mixed-rate traces не переименовываются в uniform-rate результаты.

В root добавлен opt-in native compatibility control. Каждый case запускает
отдельный процесс, считает actual stimulus edges и полный hash soma samples,
сохраняет последовательность состояний, параметры и отдельный effective graph.
Трёхсекундный budget не считается завершённым Train или научным PASS. Короткие
обязательные regressions проверяют Init и физический импульсный ответ после
cold Reset, без дополнительных Build/Calculate в проверяющем коде.

## Принятая часть: общие legacy-политики

Механически выделены ChooseDelay, ComputePeakTimes, DetectPulses и демпфированный
R proposal в `Core/TimeLearner/LegacyController.h/.cpp`. Обе топологии вызывают
одну реализацию. Их wrappers сохраняют per-input ClampResistance, модель кабеля,
порядок входов и применение изменений. Аргумент амплитудной ошибки переименован
из `dt` в `amplitude_error`, чтобы не смешивать его с шагом интегрирования.
Константы, математическая цель и вычислительный порядок не меняются.

Baseline root dc0432021067a3076c41751bfb2f40133e8ee443 включает TL-015/016;
проверенный refactor root 8f5481523525515143be9899d1584ef5d673b184 использует
PulseLib 6abc7e9c86e0ec52593b62f8995b1556e748b671. На обоих серверах прошли:

- восемь baseline и восемь строгих A/B controls: Classic/Branch × N0/N1 ×
  global 2000/20000, по три модельных секунды;
- шесть проверок production-функций: модельный fallback, overshoot/undershoot,
  недостаточная амплитуда, границы как ответственность adapter, N>4 и legacy
  counter-reset fallback;
- четыре maintained CTest suites. PulseLib: 163 cases, 154 passed, 9 skipped
  (восемь opt-in long controls выполнены отдельно; archive helper исполняется
  в fresh дочерних процессах по вызову его parent fixtures).

Совпали полные JSON наблюдений/решений, реальные stimulus onset ticks и SHA256
всех binary64 soma samples. Отдельно совпали effective graph: topology/order,
cached pointers по именам, physics, bindings и свойства с `ptParameter` mask.
Из этой metadata-проекции исключены state properties, включая wall-clock
диагностику; она не выдаётся за checkpoint динамики. Во всех восьми final
readbacks частоты соответствуют объявленному общему clock и граф valid.
Новые checks связаны с production-функциями; тестовых копий их тела нет.

Положительный контроль N1 выполняет реальное изменение Rs. Например Classic
2000 завершает bounded window с Rs[0]=60603175.71580935 вместо исходных 86000000;
N0 в этот момент сохраняет Rs[0]=86000000. Совпадение их waveform hashes до
конца этого окна не доказывает эквивалентности алгоритмов. JSON фиксирует
разные конечные Rs; полная настройка и последующий ответ здесь не проверяются.

Все native logs, XML, traces/events, readbacks и pre-test runtime manifests:
`Reports/StructTrain/TimeLearner/s06-shared-elder1` и `s06-shared-m40`.
Это совместимость ограниченного протокола, не завершённый Train, не
исторический replay августа, не 8/8 распознавание и не полная матрица режимов.
ASan для этого механического переноса отдельно не выполнялся.

Fallback от measured delay к model delay остаётся явно Legacy policy, а не
доказательством измеренной синхронности будущего контроллера. Zero placeholders
missing peaks и поведение при уменьшении pulse counter сохранены, чтобы
исправлять их отдельным изменением. Полный контракт общей части:
[PulseLib SharedPolicies](../../../Libraries/Nmsdk-PulseLib/Docs/Analysis/TimeLearnerSharedPolicies.ru.md).

## Оставшаяся работа

Принятая PulseLib develop closure:
0d8253871fd058e314a9c4852ee52f34a065284f, опубликована до корневого merge.
Production Core совпадает с проверенным 6abc7e9c86e0ec52593b62f8995b1556e748b671;
последующий 5e742918 меняет только ссылки компонентов в документации. Rdk и Bin
этим подэтапом не изменены. Все 704 опубликованных artifact hashes и gzip
payloads проверены локально как данные; численные тесты выполнялись на серверах.

Общие ProbeSpec/Observation и bounded recorder реализованы и проверены на
физических soma streams: [ProbeMeasurement](ProbeMeasurement.ru.md). Это API
измерений и native characterization adapter, не готовый controller action loop.
При полном тестировании исправлены TL-017/018 в Rdk storage metadata/identity.

Общий stateful final-verification контур реализован отдельно:
[FinalVerification](FinalVerification.ru.md). Он ещё не заменяет legacy gate.

Остаются production-подключение ProbeRecorder/FinalVerification и revision
producers, полный bounded search и topology adapters с native scheduler.
Различия Classic round-robin и Branch reverse/mute не заменяются общим
single-pulse протоколом. Совместимость старого кода и исправление алгоритмов
должны иметь разные commits и разные критерии проверки.
