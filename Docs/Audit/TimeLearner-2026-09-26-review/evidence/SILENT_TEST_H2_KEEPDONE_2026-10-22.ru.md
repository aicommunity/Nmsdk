# SILENT_TEST H2 — KeepDone cold W33 (2026-10-22)

**Постановка.** Гипотеза **H2** утверждает, что default PostTune **CanonRmin** (`PostTrainTipResistanceMode=1`) уничтожает midband TipR Done-снимка и тем самым толкает landscape probes в NonSeparable → silent `FixedLTZ=1` на Test; явный **KeepDone** (`mode=3`) или PostTune OFF с midband TipR должны дать `fires≠00000000` на Classic silent-оси ([`SILENT_TEST_NEXT_STEPS_2026-10-22.ru.md`](SILENT_TEST_NEXT_STEPS_2026-10-22.ru.md) §H2). После H3 (flag+cold PASS) и ослабления H4 / репликации H1-weak на W13/W33 следующий cold — **одна ось KeepDone** на Classic×N0. Выбран якорь **W33** (PostTune ON в дизайне волны, TipR baseline G1 = 20 М×3+86 М при `tipr_snapshot` flat 86 М×4), Host **`.17`**, без G1 RERUN.

**Иерархия:** Trainer×Mode **Classic×N0** → Span **50** → NeuronModel **AsymRm / TimeLearner Classic** → Mod **gen**; PostTune **ON** + **`PostTrainTipResistanceMode=KeepDone (3)`**.

**Конфиги Train / Test (канон matrix):** [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W33/inputs/W33_CL50_N0_PSIoff_POST/Train), [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W33/inputs/W33_CL50_N0_PSIoff_POST/Test).

---

## Прогон 1 (pre-pin, inconclusive / infra)

| Поле | Значение |
|------|----------|
| RUN_ID | `H2.KeepDone-17-20261022T081725Z-74503` |
| Host | `.17` (`M40`) |
| Work | `/media/user/Data/TLAgent-20261020/runs/h2_keepdone_w33_20261022T081725Z_2074503_ac96b785_work` |
| Launch | `…/runs/H2.KeepDone.launch.log` / `.exit` (**rc=0** harness; Train incomplete) |
| Wall | ~30 с (`08:17:25Z` → `08:17:55Z`) |
| Console SHA-256 prefix | **`4a0658f3…`** |
| Soft-cold tags | `EnablePostTrainTuning=1`, **`PostTrainTipResistanceMode=3`**, `auto_gap=1` |
| `train_t` | 640 с (лимит); Train оборван сразу |

| Метрика | Silent baseline G1 W33 | **H2 KeepDone cold (progon 1)** |
|---------|------------------------|--------------------------------|
| Train convergence | `converged_posttune_finalized` | **`not_converged_at_stop`** |
| L | `27 22 15 1` | **`1 1 1 1`** |
| TipR | `20M×3 + 86M` | **`86M×4` flat** (cold; PostTune не достигнут) |
| Gate | silent `fires=00000000`, Acc 7/8 | **SKIP_GATE** — `fires=` пусто |
| `child_rc` | 0 / −15 | **−6** |
| `failure_class` | quality silent | **`train_incomplete`** |

**Причина.** Сразу после старта Console: `*** stack smashing detected ***` → `SIGABRT` в `EmitToGlog()` (`child_rc=-6`). Инфраструктурный abort (glog ABI), не вердикт KeepDone→landscape. Закрыт pin’ом glog 0.4 — [`DEBT_17_GLOG_ABI_FIX_2026-10-22.ru.md`](DEBT_17_GLOG_ABI_FIX_2026-10-22.ru.md).

---

## Прогон 2 (после DEBT-17 glog 0.4 pin) — interrupt course-correct

| Поле | Значение |
|------|----------|
| RUN_ID | `H2.KeepDone-17-20261022T104632Z-66270` |
| Host | `.17` (`M40`), `source ~/tl-agent/env.sh` → `LD_LIBRARY_PATH=~/tl-agent/lib` |
| Work | `/media/user/Data/TLAgent-20261020/runs/h2_keepdone_w33_20261022T104632Z_2166270_e5272435_work` |
| Launch | `…/runs/H2.KeepDone.retry.launch.log` / `.exit` (**0** harness после SIGTERM) |
| Wall | ~31–32 мин (`10:46:32Z` → interrupt `11:18:26Z`); poll ~63/401, et~1890 с |
| Console | `~/tl-agent/Nmsdk/Bin/Platform/Linux/NeuroModelerConsole` prefix **`4a0658f3…`**; `ldd` → `tl-agent/lib/libglog.so.0` (**0.4.0**) |
| Soft-cold tags | `EnablePostTrainTuning=1`, **`PostTrainTipResistanceMode=3`**, `auto_gap=1` — ось KeepDone **применена** |
| Stop | SIGTERM Console pid 2166275; harness дописал `h2_result.json` и `SKIP_GATE` |

Harness: тот же `posttune_verify.run_case` / `h2_keepdone_launch.py` с attempt-local копией W33 и `posttrain_tip_resistance_mode="3"` (не патч `matrix.json`).

| Метрика | Silent baseline G1 W33 | **H2 KeepDone retry (progon 2)** |
|---------|------------------------|----------------------------------|
| Train convergence | `converged_posttune_finalized` | **`not_converged_at_stop`** (Need=1 plateau) |
| L (после Train) | `27 22 15 1` | **`27 22 15 1`** (плато; осцилляция 27↔29) |
| TipR | `20M×3 + 86M` midband | **`86M×4` flat** весь прогон (`tipr_class=flat`) |
| PostTune | finalized | **`PostTrainTuneComplete` пуст**; mode=3 в XML, но midband **не** появился |
| Gate | silent `00000000`, Acc 7/8 | **SKIP_GATE** — `fires=` **пусто** (train incomplete) |
| Acc / Цель | 7/8 / нет | **не оценены** |
| `child_rc` | 0 | **−15** (SIGTERM course-correct; **не** smash −6) |
| `failure_class` | quality silent | **`train_incomplete`** |
| Smash / EmitToGlog | — | **нет** (`NO_SMASH` в train log) |

`h2_result.json`: `IsNeedToTrain=1`, `PostTrainTipResistanceMode=3`, `EnablePostTrainTuning=1`, `PostTrainTuneComplete=""`, `detection_quality=not_evaluated_training_incomplete`, `fail_notes=["train_incomplete:exited","Need=1"]`, `gate_evaluated=false`.

**Почему interrupt.** После ~31 мин wall Train оставался на Need=1 с L в шаре G1 и TipR **CanonRmin-flat** `86M×4`; max_polls=401 (~ещё ~3 ч) не обещал PostTune-complete / midband KeepDone snapshot. Дальнейшее ожидание не меняло бы измерение «mode=3 сохраняет midband → fires≠0». Gate на incomplete Train **не** запускался (harness `SKIP_GATE`); отдельный Test-only на Need=1 не дал бы валидного KeepDone PostTune→Test пути.

**Infra.** Pin glog 0.4 **подтверждён**: полный soft-cold Train жил десятки минут без `EmitToGlog` smash (в отличие от progon 1).

---

## Вердикт H2

**Ослаблена** на оси TipR-mode KeepDone(3) cold W33 (в связке с уже ослабленным TipR overlay).

1. **Progон 2** выставил KeepDone mode=3 и довёл структурный L до G1-шара, но TipR **остался flat `86M×4`**, Need=1, PostTune **не** завершён — KeepDone **не** продемонстрировал сохранение midband Done-снимка на train path до Test.
2. Gate **SKIP** (`fires` пусто) ≠ silent `00000000` и **не** подтверждает «KeepDone → fires≠0».
3. Frozen TipR overlay на G1 W01 (`H2.TipROverlay-17-20261022T125500Z`) уже показал: midband / keep_snap при thr=1 всё равно `fires=00000000` — [`SILENT_TEST_H2_TIPR_OVERLAY_2026-10-22.ru.md`](SILENT_TEST_H2_TIPR_OVERLAY_2026-10-22.ru.md).
4. Progон 1 остаётся **infra-inconclusive** (smash); после pin физика TipR-mode path измерена и **не** поддерживает H2 как sole-fix silent thr=1.

**Не подтверждено:** causal «Canon flatten → silent; KeepDone → fires≠0» на полном Done→PostTune→Test.

---

## Deferred / next

1. Не ждать max_polls на том же Need=1 plateau; новый KeepDone cold только с явной гипотезой (иной case / PostTune OFF + midband seed / иной train_t), не повтор W33 mode=3 soft-cold без изменения постановки.
2. SPEC/Controller: не фиксировать KeepDone(3) как default, чинящий silent thr=1 — см. [`CONTROLLER_V2_DRAFT_INPUTS_2026-10-22.ru.md`](CONTROLLER_V2_DRAFT_INPUTS_2026-10-22.ru.md).
3. **DEBT-D2-silent-test** остаётся **partial** (silent thr=1 + H3 mid-policy); **DEBT-17** остаётся **done** (pin confirmed cold).

---

*Артефакты: progon1 `…/H2.KeepDone-17-20261022T081725Z-74503/`; progon2 `…/H2.KeepDone-17-20261022T104632Z-66270/` (`h2_meta.json`, `h2_result.json`, `interrupt_snapshot_*.json`, `provenance.json`).*
