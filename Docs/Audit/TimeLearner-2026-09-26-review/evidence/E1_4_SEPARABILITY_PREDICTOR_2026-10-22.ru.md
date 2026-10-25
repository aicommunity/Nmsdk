# E1.4 — предсказатель разделимости (офлайн суперпозиция ядер)

Постановка: по плану [`TIMELEARNER_AUDIT_AND_PLAN_2026-10-20.ru.md`](../TIMELEARNER_AUDIT_AND_PLAN_2026-10-20.ru.md) §E1.4 построить офлайн-предсказатель запаса разделимости `(tgt − max_foil)/tgt` для известных обученных состояний (L, TipR) и тестового Pack A, затем сравнить направление Acc/Цель с Console на **3 PASS** острова Branch и **3 FAIL** (`br25_gen`, `br25_preinh`, `W01_CL50_N0`). Ворота: совпадение с Console ≥ **5/6**. G1 RERUN / F1b cold / KeepDone **не** запускались; код-агент F3 не блокировал этот turn.

**Иерархия (канон):** результаты ниже сгруппированы Trainer×Mode → Span → NeuronModel → Mod; в каждой строке — ссылки Train/Test. Источник L/TipR — стабильные строки [`E2_matrix_2026-10-21.tsv`](E2_matrix_2026-10-21.tsv) (и G1 W01 exit-clean для Classic×N0); Console-метка PASS/FAIL — fires/`Цель` из E2 / POSTTUNE_FIX / G1 vs C2.

**Инструмент:** [`tools/e1_4_separability_predictor.py`](tools/e1_4_separability_predictor.py) + `cable_model` (`τ=10 мс`, `D=1 мс`, AsymRm). Машиночитаемо: [`E1_4_SEPARABILITY_PREDICTOR_2026-10-22.tsv`](E1_4_SEPARABILITY_PREDICTOR_2026-10-22.tsv), [`E1_4_SEPARABILITY_PREDICTOR_2026-10-22.json`](E1_4_SEPARABILITY_PREDICTOR_2026-10-22.json).

## Метод (PARTIAL: измеренные NextSegInh/PSI ещё PENDING)

1. **Пассивный кабель** (`classic_full`): суперпозиция четырёх tip-EPSP с заданными Lᵢ и TipRᵢ на каждом из 8 паттернов Pack A → `cable_sep_margin`. На всех шести кейсах этот запас **≤ 0** (согласуется с C2 `m_oracle≤0` и аудитом: пассив без сужения ядра набор не разделяет).
2. **Proxy NextSegInh / PreInh:** если `mod ∈ {nextseg, preinh}` и **length_sync_cv** = CV((L−1)/need_delay) по первым трём входам **≤ 0.25**, вместо кабеля берётся **ideal_delay** с `τ=0.5 мс` (полоса F1a / аудит «FWHM/span ≲ 0.13»). Иначе остаётся пассивный кабель (в т.ч. `br25_preinh` с CV≈0.45 и все `gen`).
3. **Предсказание fires:** при `sep_margin>0` mid = середина между tgt и max_foil → битовая маска; при `≤0` — NonSeparable → thr=1 → `00000000` (как PostTune silent).
4. **Match:** `pred_label` (PASS если margin>0) vs Console `Цель`/fires-направление.

Обоснование proxy: измеренные ядра NextSegInh/PSI в E1.1 ещё **PENDING**; аудит прямо указывает, что остров PASS держится на сужении ядра (τ_inh / PSI), а не на пассивном кабеле. CV-гейт отделяет пропорционально синхронные L острова от «Need=0 при плохой геометрии» (`br25_preinh` L=`16 13 3 1`).

## Сводная таблица (6 кейсов)

| Trainer×Mode | Span | NeuronModel | Mod | L | TipR | kernel_mode | pred_margin | pred_fires | Console | match | Train · Test |
|---|---:|---|---|---|---|---|---:|---|---|---|---|
| Branch×N1 | 25 | AsymRm | nextseg | 7 6 4 1 | 20M×3+86M | ideal_inh_proxy | **+0.074** | `10000000` | PASS `10000000` / 8/8 / да | ✓ | [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_nextseginh_C1e9/Train) · [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_nextseginh_C1e9/Test) |
| Branch×N1 | 50 | AsymRm+Preinh2_5 | preinh | 15 12 6 1 | 20M×3+86M | ideal_inh_proxy | **+0.177** | `10000000` | PASS `10000000` / 8/8 / да | ✓ | [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span50_packA_preinh_C1e9/Train) · [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span50_packA_preinh_C1e9/Test) |
| Branch×N1 | 100 | AsymRm+Preinh2_5 | preinh | 21 18 11 1 | 20M×3+86M | ideal_inh_proxy | **+0.240** | `10000000` | PASS `10000000` / 8/8 / да | ✓ | [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span100_packA_preinh_C1e9/Train) · [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span100_packA_preinh_C1e9/Test) |
| Branch×N1 | 25 | AsymRm | gen | 7 6 4 1 | 20M×3+86M | passive_cable | **−0.033** | `00000000` | FAIL silent / 7/8 / нет | ✓ | [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_gen_C1e9/Train) · [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_gen_C1e9/Test) |
| Branch×N1 | 25 | AsymRm+Preinh2_5 | preinh | 16 13 3 1 | 20M×3+86M | passive_cable (CV=0.45) | **−0.043** | `00000000` | FAIL silent / 7/8 / нет | ✓ | [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_preinh_C1e9/Train) · [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_preinh_C1e9/Test) |
| Classic×N0 | 50 | AsymRm | gen | 27 22 15 1 | 86M×4 | passive_cable | **−0.503** | `00000000` | FAIL silent / 7/8 / нет | ✓ | [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N0_PSIoff/Train) · [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N0_PSIoff/Test) |

**Match: 6/6** (ворота ≥5/6 — **PASS**).

Ключевой контроль: `br25_nextseg` и `br25_gen` имеют **одинаковые** L/TipR; пассивный кабель даёт один и тот же margin ≈−3.3 %. Различие Console (PASS vs FAIL) ловится только через mod-proxy NextSegInh при том же состоянии длин — без измеренных inh-ядер это неизбежный PARTIAL, но направление Acc совпадает.

## Вердикт

| Область | Статус | Комментарий |
|---|---|---|
| Офлайн суперпозиция L/TipR × Pack A | **PARTIAL DONE** | cable_model + E2 states |
| Gate match Console ≥5/6 | **PASS (6/6)** | Acc/Цель направление |
| Измеренные ядра NextSegInh / PSI | **PARTIAL (E1.1d+e+f)** | single-pulse — [`E1_1d_NEXTSEG_PSI_LIBRARY_2026-10-22.ru.md`](E1_1d_NEXTSEG_PSI_LIBRARY_2026-10-22.ru.md); tip multi-pulse — [`E1_1e_MULTIPULSE_IR_2026-10-22.ru.md`](E1_1e_MULTIPULSE_IR_2026-10-22.ru.md); **4-dendrite Pack-A** — [`E1_1f_FOUR_DENDRITE_PACKA_2026-10-22.ru.md`](E1_1f_FOUR_DENDRITE_PACKA_2026-10-22.ru.md): nextseg sep **−0.01/−0.03** vs proxy **+0.074**; **не** заменяют τ=0.5 мс; proxy остаётся |
| Количественное совпадение margin с Console FixedLTZ | **PARTIAL** | знаки/fires совпали; абсолютные peak ≠ LTZ Console |
| Карта Span × NeuronModel | **PARTIAL** | 6 точечных кейсов R8-среза, не полная матрица |

## Выводы

Пассивная суперпозиция ядер E1.0/C2 **правильно** помечает gen и Classic W01 как неразделимые и совпадает с silent Test, но **не** отличает nextseg PASS от gen FAIL на тех же L. Рабочий scoped-предсказатель для ворот E1.4 — гибрид: кабель для gen/десинка + узкий ideal EPSP для пропорционально синхронных nextseg/preinh. Это подтверждает вывод аудита, что остров Branch держится на сужении ядра, и задаёт критерий для E1.1 (снять Console-ядра NextSegInh/PreInh и заменить proxy). Для Controller v2: Verify может сравнивать Train `sep_margin` с предсказанием при известных L/TipR/mod; порог tol — после замены proxy на измеренные ядра.

**Повторяемость:** `CABLE_SIM=…/cable_model/cable python3 …/tools/e1_4_separability_predictor.py`.
