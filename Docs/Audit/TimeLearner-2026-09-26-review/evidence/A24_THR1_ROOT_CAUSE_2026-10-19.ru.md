# A2.4: cpp thr=1 — корневая причина и фикс

Дата: 2026-10-19.  
Trainer=Branch · Mode=N1 · NeuronModel=baseline · Mod=gen/preinh @25.

## Вердикт

`cpp_test_threshold.threshold=1` при PostTune ON — **реальный FixedLTZ**, не баг репортёра. В `FinalizePostTuneMid` при `!LandscapeOk` (или gap&lt;1e‑4) mid принудительно ставился в `PostTrainSilentThreshold` (дефолт 1.0), Result=`NonSeparable`, при этом TipR оставался CanonRmin-flattened. Подробности: [POSTTUNE_ALGORITHM_AUDIT…](POSTTUNE_ALGORITHM_AUDIT_2026-10-19.ru.md).

## Фикс (PulseLib `8575df3`)

Политика A→B→C в Classic и Branch `FinalizePostTuneMid`:

1. Ideal LandscapeOk → mid из `ComputeMidThreshold`.
2. Best-effort: частичная разделимость → `candidate_mid` (Result=`BestEffort`=6).
3. KeepDone: откат TipR на `PostTuneTipSnapshot`, silent mid для Test inference mid (Result=`RevertedKeepDone`=7).

SearchSynthetic на Train по-прежнему оставляет silent mid для пересчёта на Test.

## Проверка

Cold dual-host волна1 на SHA фикса (`DUALHOST_ASSIGNMENT…`): сравнить gen ON vs OFF; ON не должен маскировать калибровку необъяснённой thr=1 без KeepDone/best-effort в `posttune_result`.
