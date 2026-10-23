# CL-N1 — следующая гипотеза (post-H1 Span100, 2026-10-22)

Постановка: после HEAD ablations a–e (**6/6** stall на Span **480**), Arm A W3on (MaxL `L=100 58 1 1`, Need=1) и **H1 baseline cold** на Span **100** (`converged_need0`) долг **`DEBT-CL-N1` / `DEBT-D2b5-W02` остаётся open на оси 480**. H1 показал, что TipR@Rmax / `not_converged_at_stop` **не** универсален для Classic×N1: на коротком Span Train уже сходится, а `quality_fail` уходит в silent-Test (`DEBT-D2`). Этот документ фиксирует статус H1 и оставшийся фокус **H2 acceptance / Span480** — **без** нового Console cold.

Trainer×Mode якоря: **Classic×N1**. Span480: AsymRm → PSIoff → PostTune OFF — Train/Test [`W02_CL480_N1_PSIoff/{Train,Test}`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W02/inputs/W02_CL480_N1_PSIoff/Train). Span100 (H1): [`W02_CL100_N1_PSIoff/{Train,Test}`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W02/inputs/W02_CL100_N1_PSIoff/Train). Evidence: W3on [`CL_N1_NEXT_ARM_3CEFD64_2026-10-22.ru.md`](CL_N1_NEXT_ARM_3CEFD64_2026-10-22.ru.md); H1 [`CL_N1_H1_SPAN100_2026-10-22.ru.md`](CL_N1_H1_SPAN100_2026-10-22.ru.md). Controller: DRAFT inputs [`CONTROLLER_V2_DRAFT_INPUTS_2026-10-22.ru.md`](CONTROLLER_V2_DRAFT_INPUTS_2026-10-22.ru.md) §3–§4.5a; SPEC DRAFT (H2 normative) [`CONTROLLER_V2_SPEC_DRAFT_2026-10-23.ru.md`](CONTROLLER_V2_SPEC_DRAFT_2026-10-23.ru.md) §4. Root SHA факта H1: **`596762c6a`**.

**Запрет этого note:** не стартовать cold / G1 RERUN / KeepDone / F1b; не включать W3 в matrix SoftCold defaults; **не** multifactor a–c на Span100 ради train stall.

Инфра: Bin tip **`e49a52bf`** (W02 manifest refresh + E0 `--train-param` whitelist) на `timelearner_fix2` — overlays attempt-local без патча `matrix.json`.

---

## H1 — baseline Span ≠ 480, W3=off — **EXECUTED**

| Поле | Значение |
|------|----------|
| Вопрос | Сохраняется ли Classic×N1 `not_converged_at_stop` / TipR@Rmax при W3=off на **короче** Span, или stall специфичен для 480? |
| Case | `W02_CL100_N1_PSIoff` (Span **100**), **не** повтор W02 480 |
| Overlay | W3 **off**; multifactor a–c **не** запускали |
| PostTune | OFF (`--force-posttrain-tuning 0`) |
| RUN | `CLN1.H1.S100-11-20261022T181822Z-23399` |
| Результат Train | **`converged_need0`**, Need=**0**, L=`54 48 30 1`, TipR `~2.88M×3+86M` (не TipR@`1e10`) |
| Результат Test | `quality_fail` / silent (`test_mid_nonseparable`) — **`DEBT-D2`**, не train-stall |
| Vs Span480 | HEAD base Need=1, L=`54 44 1 1`, TipR@`1e10` — stall **480-specific** |
| Статус | **executed** (baseline DONE); критерий Span-specificity **выполнен** |

Иерархия строки: Classic×N1 → Span **100** → AsymRm → PSIoff → PostTune OFF — Train/Test выше. **Multifactor на Span100 не нужен** для объяснения train stall: Train уже сходится; дальше не «чинить» 100 multifactor’ом.

---

## Кандидат H2 — docs-ready acceptance: `LEN_SEARCH` / `infeasible_len` (без cold) — **оставшийся фокус**

| Поле | Значение |
|------|----------|
| Вопрос | Как Controller v2 должен принимать MaxL-escape и stall@Rmax на **длинном** Span, не путая их с shorter-span Need=0 + silent-Test? |
| Артефакт | критерии входа в SPEC / DRAFT §`LEN_SEARCH`, **не** новый Console RUN |
| Предлагаемые acceptance (черновик, post-H1) | (1) если L₀ достигло MaxL **и** Need≠0 → класс **`infeasible_len` / MaxL-hold**, не `quality_fail` SoftCold; (2) W3=1 — **opt-in diagnostic**, не SoftCold default; (3) stall TipR@Rmax / Need=1 при W3=off на Span **480** — отдельный класс **bounded stall@Rmax** (H1 доказал: на 100 этого класса нет); (4) shorter-span Need=0 + silent-Test → **`quality_fail` / `DEBT-D2`**, **не** тот же `infeasible_len` |
| Ссылки | скелет [`CONTROLLER_V2_SKELETON_2026-10-21.ru.md`](CONTROLLER_V2_SKELETON_2026-10-21.ru.md); DRAFT §4.5a; SPEC DRAFT §4 [`CONTROLLER_V2_SPEC_DRAFT_2026-10-23.ru.md`](CONTROLLER_V2_SPEC_DRAFT_2026-10-23.ru.md); AMPNORM W3 [`AMPNORM_D_RMAX_LENGTH_ESCAPE.ru.md`](AMPNORM_D_RMAX_LENGTH_ESCAPE.ru.md); H1 evidence |
| Статус | **нормативен в SPEC DRAFT** §4; FINAL SPEC **blocked** (`DEBT-CTRL-V2-DRAFT` open) |

---

## Приоритет и что не делать

1. **H2 wording** — **нормативен** в [`CONTROLLER_V2_SPEC_DRAFT_2026-10-23.ru.md`](CONTROLLER_V2_SPEC_DRAFT_2026-10-23.ru.md) §4; дальше — FINAL SPEC / senior close (FINAL ещё blocked).  
2. **Span480 / SoftCold policy** — `DEBT-CL-N1` open; не считать H1/SPEC DRAFT закрытием долга на 480 без FINAL/senior.  
3. **Не** multifactor a–c на Span100; **не** повторять a–e на W02 480 без новой гипотезы; **не** «чинить» SoftCold включением W3; **не** G1 RERUN / F1b / KeepDone из этого note.

`DEBT-CL-N1` остаётся **open** до policy-close через FINAL SPEC `infeasible_len` (H2) на оси **480** и/или явного senior close; H1 **не** закрывает долг, но сужает scope: train-stall TipR@Rmax = 480-specific.
