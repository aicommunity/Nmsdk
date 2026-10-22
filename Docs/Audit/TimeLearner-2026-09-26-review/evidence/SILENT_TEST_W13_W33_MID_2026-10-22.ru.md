# SILENT_TEST — offline candidate_mid на W13 / W33 (2026-10-22)

**Постановка.** После ослабления H4 ([`SILENT_TEST_H4_MARGIN_2026-10-22.ru.md`](SILENT_TEST_H4_MARGIN_2026-10-22.ru.md), `7aaa759f2`) проверить, воспроизводится ли на оставшихся exit-clean волнах **W13** и **W33** тот же паттерн H1-weak / H3, что на Classic×N0 W01 ([`SILENT_TEST_OFFLINE_MID_SWEEP_2026-10-22.ru.md`](SILENT_TEST_OFFLINE_MID_SWEEP_2026-10-22.ru.md)): при finite `candidate_mid` foils дают soma-fire, target_hit=0, а production **thr=1** остаётся silent `00000000`. Полный G1 RERUN и TipR KeepDone cold **не** запускались (H2 reserved после D1). Console D1 W02 занял слоты — основной разбор **flag/CSV** из замороженных G1.S1 bundles; для W13 успел завершиться один лёгкий Test-only gate на копии workdir (тот же рецепт, что W01 mid-sweep).

---

## Trainer×Mode → Span → NeuronModel → Mod

| Trainer×Mode | Span | NeuronModel | Mod | PostTune (волна) | Case | Bundle rep3 |
|--------------|------|-------------|-----|------------------|------|-------------|
| **Classic×N1** | 50 | AsymRm / LTZ HIST | gen | OFF* | `W13_HIST_ltz50_gen` | `G1.S1.W13-11-20261021T073758Z-3533` |
| **Classic×N0** | 50 | AsymRm | gen | **ON** | `W33_CL50_N0_PSIoff_POST` | `G1.S1.W33-11-20261021T120726Z-15166` |

\*Дизайн волны G1 = PostTune OFF; Train помечен `converged_posttune_finalized` и имеет Train `posttune_complete.flag` (HIST LTZ фактически прошёл PostTune phase).

**Train / Test:**

- W13: [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W13/inputs/W13_HIST_ltz50_gen/Train), [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W13/inputs/W13_HIST_ltz50_gen/Test)
- W33: [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W33/inputs/W33_CL50_N0_PSIoff_POST/Train), [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W33/inputs/W33_CL50_N0_PSIoff_POST/Test)

**Workdirs:** `…/ltz50_gen_20261021T073759Z_3421415_c28c3e68_work`, `…/W33_CL50_N0_PSIoff_POST_20261021T120727Z_3720998_d7823c63_work`.

---

## 1. `posttune_complete.flag` (rep3)

### Classic×N1 → 50 → AsymRm → gen (W13)

| Фаза | mid | result | candidate_mid | gap | tipr | tipr_snapshot |
|------|-----|--------|---------------|-----|------|---------------|
| Train | 1 | 2 (NonSeparable) | **0.013252225523523162** | ≈−6.81×10⁻⁵ | **20M×3 + 86M** | **2.88M×3 + 86M** |
| Test (inference) | 1 | 2 | **0.002412666804823535** | ≈−8.36×10⁻⁴ | **20M×3 + 86M** | — |

### Classic×N0 → 50 → AsymRm → gen (W33), PostTune ON

| Фаза | mid | result | candidate_mid | gap | tipr | tipr_snapshot |
|------|-----|--------|---------------|-----|------|---------------|
| Train | 1 | 2 | **0.06701554096608521** | ≈−3.06×10⁻³ | **20M×3 + 86M** | **86M×4** (CanonRmin flat до PostTune tip) |
| Test (inference) | 1 | 2 | **0.0024126668029073456** | ≈−8.36×10⁻⁴ | **20M×3 + 86M** | — |

**H2 TipR-сигнатура:** на **обоих** кейсах финальный TipR = **20 МОм×3 + 86 МОм** (midband+tip1), как в NEXT_STEPS для W13/W33; у W33 `tipr_snapshot` ещё flat Rmin, у W13 snapshot — midband 2.88 М×3+86 М. Это **не** W01-flat 86 М×4, но Test **inference** `candidate_mid` и `gap` численно совпадают с W01 (~0.00241, gap≈−8.36×10⁻⁴).

---

## 2. G1 harness diagnostics (уже в bundle, без нового Console)

Harness `posttune_verify` писал `Test/diagnostics/{train_candidate,cpp_test_threshold}/` с порогом из **Train** `candidate_mid` (не Test inference mid — в отличие от W01 offline sweep).

| Case | Вариант | Порог | fires | Acc | Цель | mode |
|------|---------|-------|-------|-----|------|------|
| W13 | train_candidate (G1) | Train mid **0.01325** | `00000000` | 7/8 | нет | silent |
| W13 | cpp_test_threshold | **1.0** | `00000000` | 7/8 | нет | silent |
| W33 | train_candidate (G1) | Train mid **0.06702** | `00000000` | 7/8 | нет | silent |
| W33 | cpp_test_threshold | **1.0** | `00000000` | 7/8 | нет | silent |

Train mid лежит **выше** кластера Pack A LTZ на Test (W13 production peaks ~0.0117 &lt; 0.01325; W33 peaks ~0.0021…0.0033 ≪ 0.067) → diagnostic на Train mid **не** отличает silent от thr=1. Для параллели с W01 нужен именно **Test** `candidate_mid≈0.00241`.

---

## 3. Test `candidate_mid` — измерение и прогноз

### W13 — измеренный Test-only gate (копия workdir, `--diagnostic-threshold` = Test mid)

Рецепт как W01: `phase9_preinh_bc_gate.py --skip-tipr-mid --diagnostic-threshold <Test candidate_mid> --span-ms 50`. Артефакт: `/tmp/silent_test_W13_testmid/` (успел завершиться до занятости слотов D1).

| Вариант | Порог | fires | Acc | Цель | mode |
|---------|-------|-------|-----|------|------|
| **test_candidate_mid** | **0.002412666804823535** | **`01000101`** | **4/8** | **нет** | miss_target |
| cpp / G1 baseline | 1.0 | `00000000` | 7/8 | нет | silent |

Пики при diagnostic thr сжаты около mid (trial0 `ltz≈0.002418` &lt; thr → target не fire); foils 1/5/7 fire — **байт-в-байт тот же fires-паттерн, что W01** (`01000101`).

Production `Test/results.csv` при thr=1 даёт пики ~0.0117 (все &gt; Test mid) — naive ranking предсказал бы `11111111`; фактический diagnostic run показывает, что при установленном FixedLTZ=candidate_mid динамика/отчёт LTZ **сжимается** к полосе mid (как на W01), и целевой hit **не** появляется. Сильный H1 (target_hit=1) на W13 **не** подтверждён; слабый H1 / H3 — да.

### W33 — flag/CSV only (Console Test-mid не гоняли: D1 busy)

`Test/results.csv` / `cpp_test_threshold/results.csv` (thr=1): target **0.00222977** &lt; Test mid **0.00241267** на ≈1.83×10⁻⁴; foil peaks частично выше mid (тот же кластер, что W01 thr=1 CSV). Naive peak&gt;mid → `01100111`, target_hit=0. С учётом W01/W13 measured (сжатие пиков → `01000101`) ожидаемый phenotyp при Test mid — **foil fires, Цель нет**, не silent `00000000`.

G1 train_candidate на Train mid 0.067 → `00000000` (не информативен для H3-сравнения с W01).

---

## 4. Вердикт по гипотезам

| Гипотеза | W13 | W33 | Итог |
|----------|-----|-----|------|
| **H1-weak** (thr=1 маскирует foil fires, видимые при Test mid) | **Да** — `01000101` vs `00000000` | **Да (по пикам + аналогии W01/W13)**; измеренный gate отложен | Реплицируется на exit-clean тройке |
| **H1-strong** (target_hit / fires[0]=1 при candidate_mid) | **Нет** | **Нет** (target &lt; mid) | Не подтверждена |
| **H3** (finite candidate не применяется на штатном Test → silent) | **Да** | **Да** (cpp thr=1 silent при finite Test mid в flag) | Подтверждена на N1 HIST и N0 POST |
| **H2 TipR 20M×3+86M** | Присутствует | Присутствует (+ snapshot flat→midband) | Сигнатура есть, но **не** снимает silent при thr=1; midband TipR **не** восстанавливает Цель при Test mid (W13 measured) |
| **H4 sole-cause flat Rmin** | Не применимо (не flat) | Не flat на финале | Дополнительно ослабляет H4: silent + H1-weak держатся и при midband TipR |

**Вывод.** Паттерн W01 **реплицируется** на Classic×N1 W13 (измерено) и согласуется с Classic×N0 W33 POST (flag/CSV + идентичный Test mid/gap). Ось закрытия silent/Цели смещается к **H2 KeepDone** (запрет Canon flatten / сохранение midband до Test) и/или иной политике mid/verify — не к повторному G1 RERUN и не к равномерному TipR scale.

---

## 5. Следующий шаг

1. После освобождения Console от D1 — опционально один Test-mid gate на W33 workdir (ожидание `01000101` / Acc 4/8) для симметрии таблицы; **не** блокер вердикта.
2. **H2 TipR KeepDone cold** (одна ось) — как в [`SILENT_TEST_NEXT_STEPS_2026-10-22.ru.md`](SILENT_TEST_NEXT_STEPS_2026-10-22.ru.md) variant B.
3. Не G1 RERUN; H3 flag default-off оставить.

---

*Docs + opportunistic W13 Test-mid; ветка `timelearner_fix2`; D1 Console не трогали.*
