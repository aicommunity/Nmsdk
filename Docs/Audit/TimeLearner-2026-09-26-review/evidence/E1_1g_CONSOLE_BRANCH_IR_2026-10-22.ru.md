# E1.1g — Console Branch soma IR (остров nextseg vs gen)

Постановка: офлайн цепочка E1.1d/e/f **не** заменила E1.4 `ideal_inh_proxy` (τ = 0.5 мс, FWHM≈2.1 мс, sep≈+0.074). Этот scoped-проход снимает **Test-only** Console TRACE на Branch×N1 Pack-A при состоянии острова `br25_nextseg` (L = `7 6 4 1`, TipR = `20M×3+86M`) для mods **nextseg** и **gen** (тот же L), с коротким `-t 40` и wall-kill ≤3 мин, чтобы не зависнуть на `posttune_mid_dbg` / TRACE hang (E1.1d / DEBT-A3). G1 RERUN / F1b / KeepDone / PASS×3 **не** запускались.

**Политика источников:** NeuroModelerConsole HEAD `timelearner_fix2`, PulseLib `3a599a7`, PostTune OFF (`EnablePostTrainTuning=0`), `IsNeedToTrain=0`, `StructureBuildMode=1`, TRACE `test_trace.csv` → метрики **soma_sum** peak / t_peak / FWHM. Два плеча: **Acc-arm** FixedLTZ = E1.5 island mid `0.10023…`; **IR-arm** FixedLTZ = `100` (без LTZ-spike collapse на цели). Полный 8/8 CSV на nextseg Acc не обязателен: 8 TRACE-окон + sep_ltz по 7 строкам CSV достаточно для PARTIAL.

**Машиночитаемый срез:** [`E1_1g_CONSOLE_BRANCH_IR_2026-10-22.tsv`](E1_1g_CONSOLE_BRANCH_IR_2026-10-22.tsv) · [`E1_1g_CONSOLE_BRANCH_IR_2026-10-22.json`](E1_1g_CONSOLE_BRANCH_IR_2026-10-22.json). Инструмент: [`tools/e1_1g_console_branch_ir.py`](tools/e1_1g_console_branch_ir.py). База docs: HEAD с E1.1f **`18ddd803a`**.

**Группировка:** Trainer×Mode → Span → NeuronModel → Mod — **Branch×N1** → Span **25 мс Pack-A** → **AsymRm** → Mod ∈ {nextseg, gen} → arm. Конфиги: [Train nextseg](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_nextseginh_C1e9/Train) · [Test nextseg](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_nextseginh_C1e9/Test); [Train gen](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_gen_C1e9/Train) · [Test gen](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_gen_C1e9/Test).

## Сетка

| Ось | Значения |
|---|---|
| Trainer×Mode | Branch×N1 |
| L / TipR | `7 6 4 1` / `2e7 2e7 2e7 8.6e7` |
| Mod | nextseg / gen |
| Arms | Acc (FixedLTZ≈0.10023); IR (FixedLTZ=100) |
| E1.4 gates | tgt FWHM ≤ 3.25 мс; sep ≈ proxy +0.074 |

## Ключевые результаты

| Arm | Mod | tgt_fwhm | foil_fwhm≈ | sep_soma | vs proxy FWHM 2.1 мс | fwhm_gate |
|---|---|---:|---:|---:|---|:---:|
| Acc | **nextseg** | **28.8 мс** | ~66.8 мс | **−0.0157** | ×13.7 | **нет** |
| Acc | **gen** | **22.7 мс** | ~23.4 мс | ≈0 | ×10.8 | **нет** |
| IR ltz100 | **nextseg** | **30.9 мс** | ~66.6 мс | **−0.0142** | ×14.7 | **нет** |
| — | ideal_inh_proxy (E1.1f) | **2.1 мс** | — | **+0.074** | ref | да |

Примечания: Acc-arm nextseg цель fires=1 → часть сужения FWHM до 28.8 мс — коллапс после спайка; IR FixedLTZ=100 убирает спайк, но tgt FWHM остаётся **~31 мс** (foil ~67 мс ≈ offline passive E1.1f). Gen Acc при mid острова стреляет на всех паттернах (fires=`11111111`) — FWHM~23 мс тоже ≫ proxy. `mid_dbg` **не** рос (0 байт); kill по wall/CSV — известный TRACE hang, не posttune hang.

## Вердикт: можно ли снять `ideal_inh_proxy`?

**Нет (retire=NO).** Console Branch soma IR на острове **не** показывает сужение ядра до τ ≈ 0.5 мс: FWHM цели **28–31 мс** (и foil ~66 мс) против proxy **2.1 мс**; `sep_soma` **отрицательный** (~−1.4…−1.6 %) против proxy **+0.074**. Вместе с E1.1d/e/f offline это закрывает дешёвую замену proxy измеренными ядрами.

**SPEC:** `ideal_inh_proxy` τ = 0.5 мс фиксируется как **intentional phenomenological stand-in** для Acc-direction nextseg/preinh (E1.4 gate 6/6); VERIFY-tol **не** должен требовать Console/offline FWHM/sep из E1.1d–g.

## Вердикт E1.1g / DEBT-E1.1f

| Область | Статус | Комментарий |
|---|---|---|
| Console Branch Pack-A TRACE nextseg vs gen @ island | **PARTIAL DONE** | Acc 8/8 TRACE; IR nextseg 5/8 TRACE OK для FWHM |
| Narrowing → proxy FWHM / positive sep | **DONE (negative)** | FWHM ≫ 2.1 мс; sep&lt;0 |
| Retire `ideal_inh_proxy` | **NO** | proxy intentional for SPEC |
| DEBT-E1.1f | **partial / wontfix-offline** | offline+Console IR negative; SPEC proxy intentional |

## Выводы

Console подтверждает офлайн-вердикт: реальная Branch soma-трасса на PASS-острове nextseg **не** является узким coincidence-фильтром уровня E1.4 proxy. Для Controller v2 пункт «замена ideal_inh_proxy» закрывается как **proxy intentional**; дальнейшие wall_timeout TRACE-циклы не нужны для этого долга.

**Повторяемость (без новых cold):** артефакты `$HOME/TLAgent-20261020/scratch/E1_1g_CONSOLE_IR/{nextseg,gen}_acc_ltz0p100` и `…/nextseg` (IR); пересчёт — анализ `test_trace.csv` тем же скриптом / TSV выше.
