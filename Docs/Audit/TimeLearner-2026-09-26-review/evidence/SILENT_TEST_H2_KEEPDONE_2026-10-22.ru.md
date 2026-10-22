# SILENT_TEST H2 — KeepDone cold W33 (2026-10-22)

**Постановка.** Гипотеза **H2** утверждает, что default PostTune **CanonRmin** (`PostTrainTipResistanceMode=1`) уничтожает midband TipR Done-снимка и тем самым толкает landscape probes в NonSeparable → silent `FixedLTZ=1` на Test; явный **KeepDone** (`mode=3`) или PostTune OFF с midband TipR должны дать `fires≠00000000` на Classic silent-оси ([`SILENT_TEST_NEXT_STEPS_2026-10-22.ru.md`](SILENT_TEST_NEXT_STEPS_2026-10-22.ru.md) §H2). После H3 (flag+cold PASS) и ослабления H4 / репликации H1-weak на W13/W33 следующий cold — **одна ось KeepDone** на Classic×N0. Выбран якорь **W33** (PostTune ON в дизайне волны, TipR baseline G1 = 20 М×3+86 М при `tipr_snapshot` flat 86 М×4), Host **`.17`**, без G1 RERUN.

**Иерархия:** Trainer×Mode **Classic×N0** → Span **50** → NeuronModel **AsymRm / TimeLearner Classic** → Mod **gen**; PostTune **ON** + **`PostTrainTipResistanceMode=KeepDone (3)`**.

**Конфиги Train / Test (канон matrix):** [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W33/inputs/W33_CL50_N0_PSIoff_POST/Train), [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W33/inputs/W33_CL50_N0_PSIoff_POST/Test).

---

## Прогон

| Поле | Значение |
|------|----------|
| RUN_ID | `H2.KeepDone-17-20261022T081725Z-74503` |
| Host | `.17` (`M40`) |
| Work | `/media/user/Data/TLAgent-20261020/runs/h2_keepdone_w33_20261022T081725Z_2074503_ac96b785_work` |
| Launch | `…/runs/H2.KeepDone.launch.log` / `.exit` (**rc=0** harness; Train incomplete) |
| Wall | ~30 с (`08:17:25Z` → `08:17:55Z`) |
| Console SHA-256 prefix | **`4a0658f3…`** (rsync с локального H3-matched бинарника) |
| Soft-cold tags | `EnablePostTrainTuning=1`, **`PostTrainTipResistanceMode=3`**, `auto_gap=1` — ось KeepDone **применена** |
| `train_t` | 640 с (лимит); фактически Train оборван до Need=0 |

Harness: `posttune_verify.run_case` с attempt-local копией matrix inputs W33 и `posttrain_tip_resistance_mode="3"` (не патч `matrix.json`).

---

## Результат

| Метрика | Silent baseline G1 W33 | **H2 KeepDone cold** |
|---------|------------------------|----------------------|
| Train convergence | `converged_posttune_finalized` | **`not_converged_at_stop`** |
| L (после Train) | `27 22 15 1` | **`1 1 1 1`** (не вырос) |
| TipR | `20M×3 + 86M` | **`86M×4` flat** (cold start; PostTune не достигнут) |
| Gate | silent `fires=00000000`, Acc 7/8 | **SKIP_GATE** — `fires=` **пусто** |
| Acc / Цель | 7/8 / нет | **не оценены** |
| `child_rc` | 0 (exit-clean) / −15 на части gate | **−6** |
| `failure_class` | quality silent | **`train_incomplete`** |

`h2_result.json`: `IsNeedToTrain=1`, `PostTrainTuneComplete` пуст, `detection_quality=not_evaluated_training_incomplete`, `fail_notes=["child_rc=-6","train_incomplete:exited","Need=1"]`.

**Причина обрыва Train.** В `Train/run_posttune_verify.log` сразу после старта Console: `*** stack smashing detected ***` → `SIGABRT` в `RDK::Logging::detail::EmitToGlog()` / `__stack_chk_fail`. Это **инфраструктурный abort** на `.17` при данном Console+glog, а не вердикт KeepDone→landscape. PostTune phase и Test mid **не** выполнялись.

---

## Вердикт H2

**Inconclusive** по оси «KeepDone cold → fires≠00000000» на Classic×N0 W33: KeepDone-тег выставлен, но Train **не** сошёлся, gate **не** бежал, пустой `fires` ≠ фенотип silent `00000000` и **не** подтверждает и **не** опровергает H2.

Отдельно (уже зафиксировано offline, не этим cold): midband TipR **20 М×3+86 М** на G1 W33/W13 при thr=1 всё равно silent — слабая форма «одна midband-геометрия Canon спасает fires» уже **ослаблена** ([`SILENT_TEST_W13_W33_MID_2026-10-22.ru.md`](SILENT_TEST_W13_W33_MID_2026-10-22.ru.md)); этот прогон к той оси не добавляет Test-метрик.

**Не подтверждено / не ослаблено этим RUN:**因果KeepDone TipR snapshot vs Canon на Done→PostTune→Test.

---

## Deferred / next

1. **W01 KeepDone** (или `EnablePostTrainTuning=0` + midband TipR overlay) — **deferred**: локальный host занят D1 bisect build PulseLib/`2bb72a3` (~Console rebuild); `.11` SSH broken; повторный cold на `.17` — только после стабильного Console (без glog stack-smash) или на host с проверенным LD_LIBRARY_PATH/glog.
2. Повтор H2 KeepDone cold на W33 **не** планировать на том же бинарнике, пока не закрыт abort `EmitToGlog`; альтернатива — frozen TipMode TipR overlay на уже converged G1 bundle (без retrain), если нужна только TipR-геометрия KeepDone snapshot.
3. DEBT-D2-silent-test остаётся **partial**; алгоритм mid (H3) и sep_margin (H4 weakened) без изменения статуса от этого RUN.

---

*Артефакты: `h2_meta.json`, `h2_result.json`, `provenance.json` под `…/runs/H2.KeepDone-17-20261022T081725Z-74503/`.*
