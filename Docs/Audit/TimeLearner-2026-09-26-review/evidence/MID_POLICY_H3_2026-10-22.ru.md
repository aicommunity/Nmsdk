# MID_POLICY H3 — Test candidate_mid при NonSeparable (2026-10-22)

**Постановка.** Offline mid-sweep на замороженном bundle **`G1.S1.W01-11-20261021T113257Z-15892`** ([`SILENT_TEST_OFFLINE_MID_SWEEP_2026-10-22.ru.md`](SILENT_TEST_OFFLINE_MID_SWEEP_2026-10-22.ru.md)) подтвердил **H3**: штатный C++ Test-path в `FinalizePostTuneMid` при `PostTuneResult=NonSeparable` оставляет **`FixedLTZ=PostTrainSilentThreshold` (1.0)**, хотя в `posttune_complete.flag` уже записан finite **`candidate_mid≈0.00241`**. Diagnostic gate с `--diagnostic-threshold` на том же EXP даёт **`fires=01000101`**, Acc 4/8, Цель нет; production thr=1 — silent **`00000000`**, Acc 7/8. Цель не восстанавливается (peak target &lt; candidate_mid); меняется только честность phenotyp vs «тишина по умолчанию».

**Решение (PulseLib, default-off).** Train-параметр **`UseCandidateMidOnNonSeparableTest`** (default **`0`/`false`**): только на **Test inference** (`inference=1` в `FinalizePostTuneMid`), после обычной ветки A→B→C, если результат **NonSeparable** или выбран **silent mid** ≥ `PostTrainSilentThreshold`, и **`candidate_mid ∈ (0,1)`** — подменить **`mid`/`FixedLTZ`** на `candidate_mid` для классификатора gate. **`PostTuneResult` не меняется** (остаётся `kResultNonSeparable` → gate **quality_fail**, Acc 7/8 не трактуется как selectivity PASS). Train-path и `flag=0` повторяют поведение **d52dc1c / G1 partial**.

**Код.**

| Компонент | Файл | Hook |
|-----------|------|------|
| Политика | [`NNeuronPostTrainTune.h`](../../../../Libraries/Nmsdk-PulseLib/Core/NNeuronPostTrainTune.h) | `PostTrainTune::ApplyCandidateMidOnNonSeparableTest(...)` |
| Параметр | [`NNeuronTimeLearner.h`](../../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearner.h), [`NNeuronTimeLearnerBranch.h`](../../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearnerBranch.h) | `UseCandidateMidOnNonSeparableTest` |
| Classic | [`NNeuronTimeLearner.cpp`](../../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearner.cpp) | `FinalizePostTuneMid` — вызов перед `FixedLTZThreshold.SetDataDirect` |
| Branch | [`NNeuronTimeLearnerBranch.cpp`](../../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearnerBranch.cpp) | то же |
| Flag audit | `posttune_complete.flag` | при применении: `test_mid_policy=candidate` |

**Включение в StructTrain.** В Train XML нейрона (Classic или Branch): `<UseCandidateMidOnNonSeparableTest>1</UseCandidateMidOnNonSeparableTest>`. Test EXP наследует frozen weights; inference mid пересчитывается в отдельном процессе Test с тем же параметром, если он сериализован в модель/конфиг Test.

**Cold (harness, 2026-10-22).** Test-only на frozen W01 rep3 с **`UseCandidateMidOnNonSeparableTest=1`**, Console **`4a0658f3…`**, PulseLib **`5e5a59d`** — **PASS**: [`MID_POLICY_H3_COLD_2026-10-22.ru.md`](MID_POLICY_H3_COLD_2026-10-22.ru.md) (`FixedLTZ≈candidate_mid`, `fires=01000101`, `result=2`, `test_mid_policy=candidate`). При **`flag=0`** регрессия cold **не** требуется (идентично G1 partial / offline `test_cpp_mid`).

**Связанные долги.** [`TECH_DEBT_TIMELEARNER_2026-10-20.ru.md`](TECH_DEBT_TIMELEARNER_2026-10-20.ru.md) **DEBT-D2-silent-test**; оси H1/H2/H4 без изменения.
