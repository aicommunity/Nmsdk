# E1.1f — 4-дендритная Pack-A суперпозиция IR (offline)

Постановка: **E1.1e** закрыл tip multi-pulse **отрицательно** (nextseg@L=7 ≈passive, last_fwhm~62–66 мс, gate 0/132) и оставил gap «pattern-level / 4-dendrite Pack-A». Этот scoped-проход проверяет, даёт ли **полная 4-входная** суперпозиция при состоянии острова `br25_nextseg` (L = `7 6 4 1`, TipR = `20M×3+86M`) с mods **passive / nextseg / psi_k2_5** узкое эффективное ядро и **положительный** `sep_margin`, сопоставимый с E1.4 `ideal_inh_proxy` (τ = 0.5 мс, margin ≈ +0.074, FWHM/span ≲ 0.13). Console Branch soma IR, G1 RERUN / F1b / KeepDone **не** запускались.

**Политика источников:** dual-channel Euler как E1.1d/e (`NPulseChannel`/`NPulseSynapse`). Два drive-режима: **`per_input`** (дендрит k получает только спайк в момент паттерна p[k] — семантика TimeLearner) и **`full_train`** (каждый tip получает всю 4-спайковую пачку — семантика `classic_full` / E1.4 cable). Reference-строка `ideal_inh_proxy` — matched-filter τ = 0.5 мс через `cable_model` (тот же код, что E1.4).

**Машиночитаемый срез:** [`E1_1f_FOUR_DENDRITE_PACKA_2026-10-22.tsv`](E1_1f_FOUR_DENDRITE_PACKA_2026-10-22.tsv) (8 строк = 2 drive × {proxy + 3 mod}). Инструмент: [`tools/e1_1f_four_dendrite_packa.py`](tools/e1_1f_four_dendrite_packa.py). База: HEAD с E1.1e **`2adf0cd35`** / E1.4 **`e9a0808c8`**.

**Группировка:** Trainer×Mode → Span → NeuronModel → Mod — offline probe Trainer/PostTune **N/A**; Span **25 мс Pack-A**; **NeuronModel = AsymRm → Mod ∈ {ideal_inh_proxy, passive, psi_k2_5, nextseg} → drive**. Конфиги Train/Test (ориентир острова): [Train nextseg](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_nextseginh_C1e9/Train) · [Test nextseg](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_nextseginh_C1e9/Test); gen-контроль тех же L/TipR: [Train gen](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_gen_C1e9/Train) · [Test gen](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_gen_C1e9/Test).

## Сетка

| Ось | Значения |
|---|---|
| NeuronModel | `NSPNeuronGenAsymRmD001C1e9` |
| L / TipR | `7 6 4 1` / `2e7 2e7 2e7 8.6e7` (`length_sync_cv=0`) |
| Span / pats | 25 мс Pack-A, 8 паттернов |
| Drive | `per_input`, `full_train` |
| Mod | `ideal_inh_proxy` (ref) / `passive` / `psi_k2_5` / `nextseg` |
| E1.4 gates | sep > 0 и ≈proxy (+0.074); tgt_fwhm ≤ 3.25 мс |

## Ключевые результаты

| Drive | Mod | sep_margin | pred_fires | tgt_fwhm | fwhm/span25 | gate FWHM | vs proxy |
|---|---|---:|---|---:|---:|:---:|---|
| per_input | **ideal_inh_proxy** | **+0.0744** | `10000000` | 2.1 мс | 0.084 | **да** | E1.4 ref ✓ |
| per_input | passive | −0.0162 | `00000000` | 60.6 мс | 2.42 | нет | FAIL |
| per_input | psi_k2_5 | −0.0167 | `00000000` | 60.5 мс | 2.42 | нет | amp↑, sep≈pas |
| per_input | **nextseg** | **−0.0101** | `00000000` | 57.8 мс | 2.31 | **нет** | чуть уже pas, **не** +sep |
| full_train | **ideal_inh_proxy** | **+0.0744** | `10000000` | 2.1 мс | 0.084 | **да** | E1.4 ref ✓ |
| full_train | passive | **−0.0329** | `00000000` | 72.2 мс | 2.89 | нет | ≡ E1.4 cable ✓ |
| full_train | psi_k2_5 | −0.0255 | `00000000` | 72.5 мс | 2.90 | нет | amp↑ |
| full_train | **nextseg** | **−0.0299** | `00000000` | 67.7 мс | 2.71 | **нет** | ≈passive cable |

Контроль воспроизводимости: `full_train`+passive даёт `sep_margin=−0.032891` — **бит-в-бит** с E1.4 `cable_sep_margin` для `br25_nextseg`/`br25_gen`; proxy строка даёт `+0.074361` — **бит-в-бит** с E1.4 `pred_sep_margin`.

## Вердикт: можно ли снять `ideal_inh_proxy`?

**Нет.** Четырёхдендритная Pack-A суперпозиция с измеренным NextSegInh dual-Euler **не** воспроизводит ни положительный запас разделимости proxy (+0.074), ни узкое эффективное ядро (FWHM/span ≲ 0.13). NextSeg слегка режет tgt_fwhm относительно passive (−5…−6 % на per_input / full_train), но margin остаётся **отрицательным** (−1.0 % / −3.0 %), fires silent, gate FWHM **0/6** measured-mod строк. PSI масштабирует amp без смены знака sep.

Следовательно, E1.4 `ideal_inh_proxy` остаётся **феноменологическим** стендом Acc-direction (gate 6/6), а не измеренным ядром NextSeg. Дешёвый offline gap E1.1e→E1.1f **закрыт отрицательно**.

Остающийся долг (вне этого PARTIAL): **Console Branch soma-trace** на Train `br25_nextseg` (реальная проводка / SumPotential / LTZ) или явный SPEC «proxy intentional» для VERIFY-tol nextseg/preinh.

## Вердикт E1.1f

| Область | Статус | Комментарий |
|---|---|---|
| Offline 4-dendrite Pack-A AsymRm × island L/TipR | **PARTIAL DONE** | 8 строк; инструмент + TSV |
| NextSeg → positive sep / FWHM gate | **DONE (negative)** | sep&lt;0; FWHM~58–68 мс |
| Cross-check E1.4 cable + proxy | **DONE** | full_train pas −0.0329; proxy +0.0744 |
| Retire `ideal_inh_proxy` | **NO** | proxy остаётся |
| Console Branch soma IR | **PENDING** | вне scope; см. TECH_DEBT |

## Выводы

Офлайн 4-входная суперпозиция Pack-A при острове `br25_nextseg` с NextSegInh **измерена** на dual-Euler и даёт отрицательный ответ на главный вопрос E1.1f: multi-dendrite + NextSeg **не** превращает пассивный кабель в узкий coincidence-фильтр τ ≈ 0.5 мс и **не** даёт положительный `sep_margin` уровня E1.4 proxy. Вместе с E1.1d (single-pulse) и E1.1e (tip multi-pulse) цепочка IR закрывает дешёвые model-only замены proxy. Для Controller v2: VERIFY-tol nextseg/preinh **не** должен опираться на FWHM/sep из E1.1d/e/f; либо SPEC фиксирует proxy как intentional, либо нужен Console Branch IR.

**Повторяемость:** `python3 …/tools/e1_1f_four_dendrite_packa.py --out …/E1_1f_FOUR_DENDRITE_PACKA_2026-10-22.tsv`.
