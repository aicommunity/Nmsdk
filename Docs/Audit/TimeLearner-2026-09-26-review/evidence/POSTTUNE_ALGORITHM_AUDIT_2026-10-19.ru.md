# Аудит PostTune: NonSeparable → silent threshold ≈ 1.0

Дата: 2026-10-19.  
Trainer×Mode контекст дефекта N+1: **Branch · N1 · baseline · gen/preinh @25**.  
Код: `Libraries/Nmsdk-PulseLib/Core/` — Classic `NNeuronTimeLearner`, Branch `NNeuronTimeLearnerBranch`, shared `NNeuronPostTrainTune`.

## Постановка

После Need=0 при `EnablePostTrainTuning=1` (дефолт CanonRmin) Test часто уходит в silence с `cpp_test_threshold.threshold=1` / `PostTuneResult=NonSeparable`. A2.1 (PostTune OFF) у `br25_gen` дал fires=`10110000` detected на midband TipR. Ниже зафиксирована call chain и пропуск KeepDone для Canon.

## Call chain после EOL

`AllDendritesSynced && AllSynapsesNormalized` → `EndOfLearning` → `EnterPostTunePhase` (snapshot TipR, recognition probes, `ApplyPostTrainTipMode`, silent LTZ=1.0, free-run) → `FinalizePostTuneMid` → FixedLTZ=mid, Need=false. Затем Test / `MaybeStartInferenceMidProbes` (только если FixedLTZ≥0.9).

## Дефектный путь

`LandscapeOk` требует все foils строго ниже target. `ComputeMidThreshold` считает `candidate_mid`, но при `!landscape_ok` или `gap<1e-4` **оба** Finalize (Classic ~L5212, Branch ~L6391) делают `mid = PostTrainSilentThreshold` (дефолт **1.0**) и Result=`NonSeparable`. Это реальный FixedLTZ, не баг репортёра.

## KeepDone сегодня

Snapshot TipR при входе есть. Mode KeepDone и Search-revert на snapshot есть. **Canon/Flat при провале mid TipR не откатывают**; `candidate_mid` только в flag. Branch Search на Train намеренно оставляет silent mid для Test inference.

## Честность mid

Train PostTune probes = `BuildRecognitionProbePatterns` (не полный Test Matrix). Inference mid предпочтительно на MatrixData. Train landscape ≠ Test; silent на Train probes не доказывает Test NonSeparable при KeepDone TipR.

## Политика фикса (A→B→C)

1. **Ideal** — LandscapeOk + gap≥1e-4 → ComputeMidThreshold.  
2. **Best-effort** — при конечных metrics применить `candidate_mid` / mid с реакцией на target (не silent 1.0), Result=`best_effort`.  
3. **KeepDone** — откат TipR на `PostTuneTipSnapshot`, опционально re-probe; иначе честный NonSeparable без маскировки thr=1 как «калибровки».

Не ослаблять `LandscapeOk`. Точки патча: `FinalizePostTuneMid` Classic+Branch.

## Связь с A2

| Эксперимент | Вывод |
|---|---|
| A2.1 OFF | gen: midband TipR + частичный detected — Canon flatten был фактором silence |
| A2.3 TipR×0.75 | gen all-fire; preinh silence — не замена политике mid |
| A2.4 thr=1 | = silent FixedLTZ path выше |
