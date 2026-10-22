# F3 (A5): `ResetNeuronBeforeTrainBurst` на `timelearner_fix2`

Постановка: после E1.3 ([`E1_3_RELAXATION_2026-10-22.ru.md`](E1_3_RELAXATION_2026-10-22.ru.md), root `fbd9b0490`) пауза ≤5 с **не** снимает AsymRm bias ≈−28 % относительно reset-пачек, поэтому вариант «пауза вместо Reset» для A5 несостоятелен. Нужен детерминированный `Neuron->Reset()` перед каждой обучающей пачкой за флагом с default **off** (правило кампании: один алго-фикс = флаг + R8 позже).

## Флаг

| Свойство | Тренеры | Default | Эффект |
|---|---|---|---|
| `ResetNeuronBeforeTrainBurst` | Classic + Branch | `false` | При `true`: в `BeginTrainingIteration` вызывается `Neuron->Reset()` до обнуления peak-буферов / audit burst-start |

Audit: в iteration-строке печатается `;reset_before_train_burst=0|1`.

Матричные defaults / `matrix.json` **не** менялись — флаг включается только через Train overlay (`--train-param` / E0), когда понадобится R8 A/B.

## Call sites

| Место | Поведение |
|---|---|
| `NNeuronTimeLearner::BeginTrainingIteration` | при флаге — `Neuron->Reset()` в начале пачки |
| `NNeuronTimeLearnerBranch::BeginTrainingIteration` | то же; audit `AuditBurstStart*Potential` после Reset отражает post-Reset IC |
| Существующие `Neuron->Reset()` после смены L / N / TipR | без изменений (структурный/Rs путь) |

**Не** вызывается из Test inference и PostTune free-run: они не входят в `BeginTrainingIteration` (`Training()` early-return при `kPhasePostTune && PostTuneFreeRunActive`). Tip-search PostTune, если ещё идёт через train-burst цикл, получит Reset только при явном flag=1 — для F3 A5 это не цель этого коммита.

## Сборка (этот turn)

| Артефакт | Значение |
|---|---|
| PulseLib branch | `timelearner_fix2` (parent `4e3714a` Stage0 amp_be) |
| PulseLib commit (после F3) | `4b85c916ffd68560aaa8becc60ceb7ed05717232` (`4b85c91`) |
| Console sha256 | `9540e64b7813ee2e735d0f570486d7fdd7de3747d7f12c7bb1665a38b3f8e45f` |
| Preset | `linux-gcc-debug-local` → `Nmsdk-PulseLib.core` + `NeuroModelerConsole` |

Предыстория: тот же флаг уже жил на отдельной ветке `agent/tl-audit-f2-f3`@`0ad009a` вместе с F2/F7 ([`F2_F3_PATCH_2026-10-20.ru.md`](F2_F3_PATCH_2026-10-20.ru.md)); cold W01 Need=0 при flag=1 — [`F2_F3_COLD_2026-10-20.ru.md`](F2_F3_COLD_2026-10-20.ru.md). На HEAD `timelearner_fix2` флага не было (база `d52dc1c`+Stage0); этот коммит **портирует только F3**, без PreferMeasuredDelay / MarkRminLengthTolAsBestEffort.

## R8 A/B

**Отложено** (не этот turn): cold A/B flag=0 vs flag=1 на W01 Classic×N1 и R8 после успешного merge. Default off → поведение матрицы без overlay бит-в-бит как до патча.

## Вывод

Код F3 на `timelearner_fix2` готов: opt-in Reset-before-pack закрывает дыру A5/E1.3 на уровне IC; включение в матрицу — отдельный R8 arm.
