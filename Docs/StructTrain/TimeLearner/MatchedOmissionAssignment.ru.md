# Matched omission: первый production алгоритмический блок

Добавлены PulseLib `Core/TimeLearner/MatchedOmissionAssignment.h/.cpp` и
детерминированные C++ cases
`Tests/Integration/Libraries/Test_PulseLib_MatchedOmissionAssignment.cpp`.
Точный контракт находится в PulseLib
`Docs/TimeLearner/MatchedOmissionAssignment.ru.md`.

Чистый selector использует настоящие максимумы полной пачки и bounded
группу `fullBefore → omit-each-original-input → fullAfter`. Измеряемая
величина берётся из full potential; omission differences устанавливают
операционную поддержку, не подменяют потенциал и не раскладывают нелинейную
пачку на линейные слагаемые. Отсутствие response peaks посторонних импульсов
не является причиной отказа. Shared/unknown support возможного высшего
assigned максимума остаётся Ambiguous.

Контекст связывает физические каналы, actual Branch selector, source physics,
исходный target, model/base/effective revisions, epoch, native instance/reset
binding и восстановление полного предъявления. Проверяются actual event
ordinals/frame indices, source waveform, сетка и полное покрытие samples,
baseline, отдельная full repeatability и все burst/sample budgets.
Явный timeComparisonTolerance допускает roundoff абсолютных часов и строго
меньше половины tick; никакой сдвиг на tick или интерполяция не разрешены.
Допуски influence/repeatability не берутся из train amplitude/sync tolerances.

Это новый метод `matched-omission-assigned-maximum-v1`. Он не меняет смысл
ProbeRecorder schemas1–6, не превращает старые window/domain diagnostics в
сертификат и сам не создаёт `TrainingCertificate`. Для N1 возвращается
Unsupported с указанием существующего SingleImpulse пути.

## Проверки и границы этапа

Отдельный target `Test_PulseLib_MatchedOmissionAssignment` компилирует тот же
production selector и `MeasuredResponse.cpp`; его cases также включены в
полный `Test_PulseLib_StorageComponents` target. Покрываются actual full
maximum против global/difference maximum, delayed-prior counterexample,
отсутствующие посторонние отклики, minor extrema, shared/unknown/nonlinear
support, ties/plateau/clipping, retained actual timestamps, источник,
model/reset/baseline changes, nonfinite/gaps/budgets и повторяемость.

Во время реализации локальные сборки и численные тесты не выполнялись.
Проверка diff и статическое чтение не являются C++ PASS. Нужны серверные
normal/ASan unit gates и затем production native composite integration:
bounded N+2 FSM, реальные закрытые packet/trace witnesses, controls restore,
reference/search/final-verification transport и отдельная версионированная
certificate/reader проверка. Научная сходимость или избирательность этим
блоком не заявляется; весь план остаётся открытым.
