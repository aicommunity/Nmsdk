# F5 CorrectAttenuationGammaForTipR — cold W01 (2026-10-21)

Постановка: на HEAD PulseLib `6d746ac` (флаг default off) прогнан cold W01 Classic N1 с `--train-param CorrectAttenuationGammaForTipR=1`, один повтор, host `.11`, Console sha256 `745d6061…`, RUN_ID `F5.gamma-11-20261021T053512Z-6091`.

Итог обучения: `training_convergence=converged_need0` (Need=0), но `failure_class=quality_fail`, fires=`00000000` (silent Test / неразделимость по качеству). Queue: `queue_completed_no_commit`, `quality_failure_cases=1`. Это не infrastructure fail: γ-поправка позволила дойти до Need=0, но порог/разделение на Test не дали целевых fires.

Следующий шаг по F5: разобрать mid/TipR в attempt-bundle и сравнить с baseline S1 без флага на том же case (когда слот Console свободен), не объявляя F5 закрытым как PASS.

**Mid/TipR (read-only, tick 131):** cold F5 — Need=0 при `quality_fail`/silent Test; для **S1 baseline** того же семейства Classic50 см. pilot extract: `W01_CL50_N0_PSIoff` rep3 `launch.exit=0`, `TipSynapseResistance=86000000×4`, `DendriteLength=27 22 15 1`, POST TipR **20M×3** на W33 (POST tune). Прямое N0 vs N1+γ сравнение TipR/mid по attempt-bundle **ещё не** снято — F5 run `F5.gamma-…6091` vs `G1.S1.W01-…15892` разные norm/case; финальное сравнение только после extract attempt JSON или paired rerun.
