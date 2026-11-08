# Declared-window composite Train: live core и отдельный gate

Pulse feature commit: `269164d2a2339908a8667e859a04a8e81da50c3c`.

2026-11-08. Подготовлен первый исполнимый блок нового Train-пути; адресный M40 ASan143 build/runtime gate принят; service/export/CLI остаются отдельными этапами. Это не acceptance исходной научной серии и не объявление исправленным всего controller pipeline. Production contract находится в PulseLib `Docs/TimeLearner/TypedCompositeTrainingCore.ru.md`.

Основание: Pulse `c3ac0aad30ccc4b9894e0d4dccb3386d688d504f`, Root reader `1de038cc72e6cb6217233d938939385b9f464945`. Перед feature отдельно зафиксировано механическое выделение scalar acceptance: Pulse `474df05b714415057bbcb4692ce224621ae55ac0` / Root `b1457e7e0ae7a63c6aba7599b4189e9465a32e77`. Исправление ошибочной fixture-гипотезы о неизбежном изменении Branch revision — отдельный Root `51566b251a087589411d0a6bbb848de7d0273b6e`, merged в эту root-ветку через `6c41f2f42280cef3e56bc5ef097aecd2acebd99e`. Отрицательный SDK140 A1 runtime остаётся самостоятельным историческим свидетельством; этот patch не исправлял production context ради зелёного теста.

## Что реализовано

- Отдельный `VerificationProtocol=4` с явным методом `declared-window-basin-necessity-v1`, actual context/geometry policies и per-input declared windows.
- Закрытые prepared/validated composite типы. Они создаются только реальным native owner authority, а не public validity boolean или произвольными doubles/JSON.
- `NativeCompositeTrainingAttempt` с actual Classic/Branch owner, его existing native executor и N+2 группой. Один logical Arm на fullBefore; omit/fullAfter не подаются в search как самостоятельные measurements. Все компоненты рассчитывает исходный Rdk scheduler.
- Immutable actual initial source/model/storage/optional-C0 binding отдельно от current candidate witness. Off не требует наличия C0 или поддержки C-trim. Источник C0 не recapture-ится и не заменяется фиктивным unit-state.
- Typed capture/search/final admission с общим прежним scalar residual/rank/tolerance path. CapturedPerInput сохраняет actual fullBefore raw selected peak; reference остаётся N−1. Финальная стадия собирает свежие N Final groups; Reference/Search и replay не дают Final proof.
- Arrival/plateauEnd относительны actual `originStimulusId` конкретного fullBefore. Старт очередной группы в другом абсолютном времени не является sync error.
- Независимые logical-group/native-probe/sample/model-time/wall-time limits; partial frames тоже учитываются. Private live guard перечитывает реальную модель/C0/storage и не доверяет cached revision аргументу.
- Внутренний certificate2 содержит новый protocol и reference/final semantic proof IDs. Recognition не наследует Exact автоматически. Existing diagnostic bridge по-прежнему certfalse, old v1 assignment не становится Train-критерием.

Semantic proof identity не зависит от относительного имени primary CSV: в нём actual native packets, canonical CSV hashes, declared method/policy/window, source/current witness, logical/attempt/group/purpose bindings. Process-local attempt binding не выдаётся за portable физический identity.

## Gate inventory

Новый файл `Tests/Integration/Libraries/Test_PulseLib_CompositeTraining.cpp` подключён к `Test_PulseLib_StorageComponents`. Фильтр: `NativeCompositeTraining.*`; **46 literal test cases**:

| Scope | Cases |
|---|---:|
| Actual capture → bounded search → fresh all-N final, Classic/Branch × 2000/20000 Hz | 4 |
| Reference purpose cannot certify final | 2 |
| Stop during partial N+2 group | 2 |
| Physical Rs edit invalidates final, actual revision supplied | 2 |
| Expired live attempt rejects previously closed proof | 2 |
| Merged vertex remains rejected | 2 |
| Raw probe/reference/old codec cannot enter protocol4 | 2 |
| Closed group cannot serve next final input | 2 |
| Changed declared window cannot relabel captured observations | 2 |
| Existing actual bound C0, capture/search/final, Classic/Branch 2000 Hz | 2 |
| Group budget rejects before next native queue | 2 |
| Cached revision cannot hide actual physical Rs edit | 2 |
| Default sync .02 remains OutsideTolerance | 2 |
| Owner Reset expires proof despite unchanged physical revision | 2 |
| Owner Default + same native reconstruction expires identical proof | 2 |
| Pool Return/Take + same instance reconstruction expires identical proof | 2 |
| Prepared declaration expires after owner Reset during group | 2 |
| N0 capture/search/final with two fresh anchor/input repeats, Classic/Branch 2000 Hz | 2 |
| Setter/direct-data/connected false between final close and consume | 6 |
| Direct-data false during native group | 2 |

Четыре first plumbing positives, два existing-C0 positives и два N0 repeat positives **явно** задают sync=.2 и фиксируют L/Ns/Rs; это инженерная проверка typed admission/scalar processing, а не научная сходимость исходной задачи. Их группы имеют actual begin offsets, отличающиеся более чем на .2s. Tests сравнивают target raw с actual fullBefore sample и residuals с arrival относительно фактического origin события, а не с абсолютным временем или delay predictor. Два отдельных default-sync теста требуют OutsideTolerance/!Exact при .02 и неизменённом amplitudeAbs=1e−5; автоматическое расширение tolerance запрещено.

Native fixtures используют реальный environment/storage/model/scheduler, actual source waveform и actual steady clock. Group/attempt wall limits явно 300/1800s при 2000 Hz и 1200/7200s при 20000 Hz. Model budget 2s на группу и 120s на попытку; sample/native/group budgets заданы отдельно. Положительный default timing outcome не обещан: физически несинхронный unchanged graph должен честно дать OutsideTolerance.

Также обязательна регрессия прежних 74 BoundedTraining +23 FinalVerification cases. Pure `Test_PulseLib_VerificationAlgorithms` и `Test_PulseLib_StimulusSubset` теперь связывают новый production `CompositeTrainingMeasurement.cpp`, поскольку общий FinalVerification содержит typed admission. Это не copied-body harness. Механический pin нужно проверять отдельно от feature pin. Normal и ASan результаты, exact loaded sources, JUnit completeness и фактический execution inventory должны публиковаться серверным worker через Git; локальных numerical tests/builds не было.

## Что остаётся следующим исполняемым этапом

1. Service composition: existing `NativeTrainingService` должен владеть новым authority, соединить before/after hooks с existing shared executor, собирать каждую complete/partial группу и все primary packets до следующего Start, без raw-trial Arm/Consume.
2. Cold protocol4/config6 и learned/stopped package5/certificate2: canonical self-contained primary closure или явный bounded resolver; fresh recomputation на replay; semantic proof IDs отдельно от artifact-document paths. Старый protocol decoder нельзя использовать через characterization ProbeSpec4.
3. Native lifecycle/warm restart/retarget: отмена группы до Reset/Default/Build/retarget, восстановление presentation, сохранение partial evidence и immutable target family, новый live attempt generation. Между новыми owner generations retained target ещё не переносится; это промежуточный scope, а не окончательное ограничение продукта. Legacy warm-start режимы не менялись.
4. Runner CLI и independent reader/replay нового Train envelope, затем server-native positive/negative gates, только после этого ограниченные A/B experiments и отдельное научное решение о методе.

На текущем блоке новые protocol/certificate codecs, service/config/package/CLI и AdvanceUnassignedBurst recovery **явно fail closed**, а не подменяются legacy schema3/старым package1–4. Новый режим не включён в defaults/common experiments. Старые ProbeRecorder schemas1–6, diagnostic portable codec1 и v1 метод сохраняют прежний смысл.


Для первой серверной сборки269/27ba обнаружен отсутствующий полный тип нейрона; отдельная правка и условия повторной проверки — [CompileFix](TypedCompositeTrainingCompileFix.ru.md). Исходный feature pin не объявляется runtime-принятым.


## Адресная приёмка M40

Исправленный Rootd920/Pulsee183 прошёл143/143:97 прежних scalar и46 actual
native core cases. [Независимая проверка](TypedCompositeCoreM40A2Verification.json)
подтвердила1683 архивных members,3056 source/resource files по Git,75 loaded
files и56 kernel closures; lease released. Original compile failure иошибочная
mechanical inventory попытка сохранены отдельно. Это реальные storage/scheduler
assertions и внутренняя typed certificate plumbing; numerical primary exports
в этом frozen fixture не сохранялись, independent raw replay не принят.
Service/cold6/package5/Console и научная классификация этим gate не доказаны.
Окна кандидатов пока фиксированы на попытку; открытый [review](CandidateWindowScopeReview-20261108.ru.md)
остаётся обязательным перед полной приёмкой этапа7.
