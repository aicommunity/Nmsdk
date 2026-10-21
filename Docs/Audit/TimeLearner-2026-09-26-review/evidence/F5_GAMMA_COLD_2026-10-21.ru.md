# F5 CorrectAttenuationGammaForTipR — cold W01 (2026-10-21)

Постановка: на HEAD PulseLib `6d746ac` (флаг default off) прогнан cold W01 Classic N1 с `--train-param CorrectAttenuationGammaForTipR=1`, один повтор, host `.11`, Console sha256 `745d6061…`, RUN_ID `F5.gamma-11-20261021T053512Z-6091`.

Итог обучения: `training_convergence=converged_need0` (Need=0), но `failure_class=quality_fail`, fires=`00000000` (silent Test / неразделимость по качеству). Queue: `queue_completed_no_commit`, `quality_failure_cases=1`. Это не infrastructure fail: γ-поправка позволила дойти до Need=0, но порог/разделение на Test не дали целевых fires.

Следующий шаг по F5: разобрать mid/TipR в attempt-bundle и сравнить с baseline S1 без флага на том же case (когда слот Console свободен), не объявляя F5 закрытым как PASS.
