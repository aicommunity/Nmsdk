# SILENT_TEST H4 / sep_margin — offline (2026-10-22)

**Постановка.** После E1.1b amp-библиотеки ([`E1_1b_RS_N_AMP_LIBRARY_2026-10-22.ru.md`](E1_1b_RS_N_AMP_LIBRARY_2026-10-22.ru.md), SHA **`2604dc08c`**) и offline mid-sweep ([`SILENT_TEST_OFFLINE_MID_SWEEP_2026-10-22.ru.md`](SILENT_TEST_OFFLINE_MID_SWEEP_2026-10-22.ru.md)) проверить гипотезу **H4** из [`SILENT_TEST_NEXT_STEPS_2026-10-22.ru.md`](SILENT_TEST_NEXT_STEPS_2026-10-22.ru.md): на **Classic×N0 → Span 50 → AsymRm → gen** (`W01_CL50_N0_PSIoff`, PostTune OFF) flat TipR@CanonRmin (**86 МОм×4**) сам по себе объясняет `target_hit=0` при `candidate_mid`. Cold TipR-overlay и G1 RERUN **не** запускались (D1 bisect PulseLib `5308aa5` занял CPU; `.11` недоступен).

**Train / Test:** [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N0_PSIoff/Train), [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N0_PSIoff/Test).

**Bundle:** `G1.S1.W01-11-20261021T113257Z-15892` / work `W01_CL50_N0_PSIoff_20261021T113258Z_3673774_4a914156_work` (rep3). L=`27 22 15 1`, TipR=`86000000×4`.

---

## 1. Пики vs `candidate_mid` (G1 flag + CSV)

| Величина | Значение | Комментарий |
|----------|----------|-------------|
| `candidate_mid` | **0.0024126668029073456** | Test `posttune_complete.flag`, NonSeparable (`result=2`, `landscape_ok=0`) |
| `gap` (flag) | **−8.36×10⁻⁴** | отрицательный → mid не разделяет |
| TipR | **86 МОм × 4** | flat CanonRmin |
| Probe `metrics` (8) | min **0.002102**, max **0.003348** | 6/8 > mid, 2/8 < mid; span_ratio ≈ **1.59** |
| Target trial0 `ltz_potential_max` | **0.00222977** | CSV Test gate; **ниже** `candidate_mid` на **≈1.83×10⁻⁴** (~7.6 %) |
| Max foil (metrics) | **≈0.003348** | выше mid на **≈9.4×10⁻⁴** |

Offline mid-sweep уже показал: при thr=`candidate_mid` fires=`01000101` (foils fire, target нет); при thr=1 — silent `00000000`. Сильный H1 отвергнут; H3 подтверждена ([`MID_POLICY_H3_COLD_2026-10-22.ru.md`](MID_POLICY_H3_COLD_2026-10-22.ru.md)).

**Вывод по ландшафту:** кластер LTZ-пиков Pack A на flat Rmin **не** «абсолютно плоский» (есть foil fires при finite mid), но **сжат** в полосу ~0.0021…0.0033, внутри которой `candidate_mid` режет так, что **цель ниже порога**, а часть foil — выше (инвертированный / неразделимый ranking, `gap<0`).

---

## 2. Ожидаемая amp с E1.1b (AsymRm, N=1, Reset-before-pulse)

Калибровка: `peak_calibrated = peak_model × 1.46` ([`E1_1b_RS_N_AMP_LIBRARY_2026-10-22.tsv`](E1_1b_RS_N_AMP_LIBRARY_2026-10-22.tsv)).

| TipR | L=1 peak_cal | L=10 | L=25 | L=50 | L25/L1 |
|------|--------------|------|------|------|--------|
| **8.6×10⁷** (Rmin) | 0.00643 | 0.00220 | **0.00140** | 0.00099 | **0.217** |
| **1.72×10⁷** (~midband) | 0.0359 | 0.0123 | **0.00780** | 0.00553 | **0.217** |
| **2.0×10⁶** (low) | 0.356 | 0.121 | 0.0772 | 0.0547 | **0.217** |

Относительная аттенюация по L (**γ(L) ≈ const по TipR**, E1.1b) почти не зависит от уровня TipR: перевод всех синапсов с 86 МОм на ~17 МОм даёт **глобальный масштаб ≈5.58×** при том же L25/L1.

Сопоставление с Console Pack A: одиночный дистальный EPSP @Rmin L≈25 даёт ~0.0014; наблюдаемый кластер LTZ ~0.0021…0.0033 согласуется с **частичной суммацией** четырёх входов (L=27/22/15/1), а не с полной некогерентной суммой (~0.01 по грубой оценке). Target **0.00223** лежит **внутри** этого кластера и **ниже** `candidate_mid`.

**Если бы TipR снизили равномерно** (все входы ×5.58): ожидаемый target ≈0.0124, а mid, пересчитанный на том же ranking, ≈0.0135 — **знак gap сохраняется**. Равномерный TipR-сдвиг **не** переворачивает NonSeparable ranking; он только сдвигает абсолютную шкалу.

---

## 3. Вердикт H4

| Формулировка H4 | Вердикт | Обоснование |
|-----------------|---------|-------------|
| **Сильная:** flat TipR@Rmin → soma «слишком flat» для Pack A при **любом** mid &lt; 1 | **Ослаблена / не подтверждена** | При `candidate_mid` уже есть foil fires (`01000101`); ландшафт различим, но **цель ниже mid** |
| **Слабая (sep_margin):** @CanonRmin абсолютная шкала EPSP кладёт Pack A LTZ в полосу ~2–3×10⁻³, где `candidate_mid` оказывается **выше target** при `gap&lt;0` | **Подтверждена количественно** | Δ(target−mid)≈−1.83×10⁻⁴; E1.1b: single L25@Rmin≈0.0014 ≪ midband |
| **Как единственная причина silent / target miss** | **Ослаблена** | γ(L)≈const → равномерный TipR не чинит gap; W33 (TipR 20 М×3+86 М) тоже silent при thr=1 (ось H2/H3, не чистый H4); F4/F6 N1 midband тоже silent |

**Итог:** H4 **ослаблена** как каузальная «единственная ось»; остаётся полезным описанием **численной тесноты** sep_margin на flat Rmin. Закрытие `target_hit` требует либо **дифференциальной** TipR-геометрии / L (H2 KeepDone), либо иной политики mid/verify (H3 уже даёт fires≠0, но не Цель), а не только «поднять все TipR одинаково».

---

## 4. TipR midband overlay cold

**Статус: DEFERRED.**

Причины: (1) D1 bisect активно собирает PulseLib `5308aa5` — не конкурировать полным Console rebuild; (2) E1.1b предсказывает, что **равномерный** midband overlay не перевернёт `gap`; имеет смысл cold только как **H2** (KeepDone / запрет Canon flatten, одна ось), не как проверка сильного H4; (3) G1 RERUN и `.11` запрещены брифом.

Когда D1 освободит CPU: один cold `W01_CL50_N0_PSIoff` с KeepDone **или** explicit midband TipR без PostTune — см. variant B в [`SILENT_TEST_NEXT_STEPS_2026-10-22.ru.md`](SILENT_TEST_NEXT_STEPS_2026-10-22.ru.md).

---

## 5. Следующий шаг (docs/algorithm)

1. Держать H3-флаг default-off; Controller contract — не считать silent thr=1 PASS ([`CONTROLLER_V2_SKELETON_2026-10-21.ru.md`](CONTROLLER_V2_SKELETON_2026-10-21.ru.md) §5 п.7–8).
2. После D1 — точечный H2 TipR cold (не H4-uniform), либо offline W33/W13 candidate_mid sweep (есть midband TipR).
3. Не стартовать G1 RERUN.

---

*Docs-only 2026-10-22, ветка `timelearner_fix2`; база E1.1b `2604dc08c`.*
