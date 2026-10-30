# Карта дендрита (ворота D) — τ(Cm) per Span · 2026-10-23

**Статус ворот D:** карта **зафиксирована** как вход в фазу A. H0a (теория + UStorage + EXP) на origin; H0b cold dual-host **запущен** (ядро Span100 → далее 50/25/200/480); SPEC FINAL дендритного Controller закрыт. Senior: на Span, где MaxL/FWHM/silent/stall не закрываются согласованной τ и mods, нужен **новый носитель задержки** (аксонный тренер), а не ещё одна единая τ.

Группировка: [`RESULT_GROUPING_HIERARCHY.ru.md`](RESULT_GROUPING_HIERARCHY.ru.md). Стратегия: [`STRATEGY_TAU_PER_SPAN_THEN_AXON_2026-10-23.ru.md`](STRATEGY_TAU_PER_SPAN_THEN_AXON_2026-10-23.ru.md).

---

## 1. H0a — Span → τ → Cm → StorageClass

Полная таблица: [`H0A_TAU_CM_TABLE_2026-10-23.ru.md`](H0A_TAU_CM_TABLE_2026-10-23.ru.md) / [`.tsv`](H0A_TAU_CM_TABLE_2026-10-23.tsv).

Кратко: S25 τ=0.5 мс Cm=5e-11; S50 τ=1 мс Cm=1e-10; S100 τ=2.5 мс Cm=2.5e-10; S200 τ=5 мс Cm=5e-10; S480 τ=10 мс Cm=1e-9 — все AsymRm Pack A, **новые** имена `…TauH0_S*`. Ideal margin +7…15%; cable `feasible=true` при MaxL≈100, но `m_oracle≈−0.02…−0.05` (FWHM/span≈0.34) — физический потолок пассивного кабеля.

PulseLib: `35cd074` (`CreateClassSamples`). Legacy `C25e12`/`C25e11`/`C1e9` **не** трогались.

---

## 2. H0b — cold dual-host (волна 1, SERIES_DONE 2026-10-23T12:36Z)

| Хост | Лимит | Полоса (волна 1) | Итог |
|------|-------|-----------------|------|
| `.11` | ≤8 | Classic S50/S100/S200 + R8 smoke | 8/8 DONE |
| `.17` | ≤12 | Branch S25/S50/S100/S480 gen/preinh/nextseg | 12/12 DONE |

**Вердикт волны 1.** На согласованных TauH0-классах **ни одна** новая H0-ячейка не дала SoftCold PASS: 14× `not_converged_at_stop` (Need≠0 до max_polls / stop), 2× Classic×N1 `cpp_training_refusal`, 3× `gate0_exit_nonzero`. Единственный PASS волны — preflight R8 `br25_nextseg` на **legacy** C1e9 Branch (не TauH0). Это усиливает потолок §3: τ(Cm) per Span необходима, но **недостаточна** для cold PASS на дендрите без аксонного носителя / иной топологии.

Журнал: [`H0B_COLD_LAUNCH_2026-10-23.tsv`](H0B_COLD_LAUNCH_2026-10-23.tsv). Монитор 10 мин остановлен после ALL_DONE волны 1.

### Сводка волны 1 (Trainer×Mode → Span → Mod; PostTune ON)

| Trainer×Mode | Span | NeuronModel | Mod | PostTune ON | Host | Train | Test | exit |
|--------------|------|-------------|-----|-------------|------|-------|------|------|
| Classic×N0 | 50 | TauH0_S50 | gen | fail | .11 | `SelectivityTauCm/EXP_classic_S50_gen_TauH0_N0/Train` | `…/Test` | not_converged_at_stop |
| Classic×N1 | 50 | TauH0_S50 | gen | fail | .11 | `…_N1/Train` | `…/Test` | gate0_exit_nonzero |
| Classic×N0 | 100 | TauH0_S100 | gen | fail | .11 | `EXP_classic_S100_gen_TauH0_N0/Train` | `…/Test` | not_converged_at_stop |
| Classic×N1 | 100 | TauH0_S100 | gen | fail | .11 | `…_N1/Train` | `…/Test` | cpp_training_refusal |
| Classic×N0 | 100 | TauH0_S100 | preinh | fail | .11 | `EXP_classic_S100_preinh_TauH0_N0/Train` | `…/Test` | not_converged_at_stop |
| Classic×N1 | 100 | TauH0_S100 | preinh | fail | .11 | `…_N1/Train` | `…/Test` | cpp_training_refusal |
| Classic×N0 | 200 | TauH0_S200 | gen | fail | .11 | `EXP_classic_S200_gen_TauH0_N0/Train` | `…/Test` | not_converged_at_stop |
| Branch×N0/N1 | 25 | TauH0_S25 | nextseg | fail | .17 | `EXP_branch_S25_nextseg_TauH0_N*/Train` | `…/Test` | not_converged_at_stop |
| Branch×N0 | 50 | TauH0_S50 | gen/nextseg | fail | .17 | `EXP_branch_S50_*_TauH0_N0/Train` | `…/Test` | not_converged_at_stop |
| Branch×N0/N1 | 100 | TauH0_S100 | gen/preinh/nextseg | fail | .17 | `EXP_branch_S100_*_TauH0_N*/Train` | `…/Test` | not_converged / gate0 |
| Branch×N0 | 480 | TauH0_S480 | gen/nextseg | fail | .17 | `EXP_branch_S480_*_TauH0_N0/Train` | `…/Test` | not_converged_at_stop |
| Branch (legacy R8) | 25 | C1e9 | nextseg | **PASS** | .11 | `SelectivityBranch/…_nextseginh_C1e9/Train` | `…/Test` | SoftCold ok |

**Хвосты после волны 1:** PostTune OFF / полная сетка 88 / PASS×3 — не стартовать без новой гипотезы (единая τ уже опровергнута; TauH0 cold не PASS). Рекомендация: senior review ворот D → фаза A (F1b), либо узкий diagnostic (EstDelay↔τ, wiring) без полного RERUN.

---

## 3. Потолок дендрита (без смены носителя задержки)

| Симптом | Где проявляется | Интерпретация для ворот D |
|---------|-----------------|---------------------------|
| cable `m_oracle`<0 при FWHM/span≈0.34 | все H0a Span @ MaxL≈100 | Пассивный кабель синхронизирует L, но не даёт идеальный запас |
| `bounded_stall_rmax` | Classic×N1 @480 | FINAL policy; не чинить W3/multifactor |
| `quality_fail` silent Test | Classic Need=0 + thr=1 | DEBT-D2; mid = C+A, не default-on |
| C25e12 на чужом/коротком спане | W13/W37 HIST | Legacy read-only негатив единой быстрой τ |
| F5 γ tip noop | Span100 | A7 midband noop; без нового F5 cold |

**Вывод потолка:** согласованная τ(Cm) — необходимый, но не достаточный шаг; нелинейные mods (nextseg/preinh/PSI) и/или аксонная задержка нужны там, где H0b не даёт SoftCold PASS при MaxL.

---

## 4. Legacy vs H0

| | Legacy (read-only) | H0 (новые имена) |
|--|--------------------|------------------|
| UploadClass | `…C25e12`, `…C25e11`, `…C1e9`, Pack B/C, FastCell | `…TauH0_S25…S480` gen/preinh |
| EXP | HIST / W13 / W37 / SelectivityAsymRm packA C1e9 | `SelectivityTauCm/EXP_*_TauH0_*` |
| Политика | эталоны неудачных подходов | derived from … в `DERIVED_FROM.md` |

---

## 5. R8 / baseline / долги

- Preflight: [`PREFLIGHT_PHASE_D_2026-10-23.ru.md`](PREFLIGHT_PHASE_D_2026-10-23.ru.md).
- E2 R8 EQUIVALENT (ранее); полный RERUN не делался.
- SPEC FINAL: [`CONTROLLER_V2_SPEC_FINAL_2026-10-23.ru.md`](CONTROLLER_V2_SPEC_FINAL_2026-10-23.ru.md).
- `DEBT-H0-tau-cm`: **partial** — H0a done; H0b волна 1 SERIES_DONE (0 SoftCold PASS на TauH0); ворота D подтверждают потолок → фаза A.
- `DEBT-CTRL-V2-DRAFT`: **closed** (FINAL).
- `DEBT-F1b`: **OPEN**, отложен.

---

## 6. Отложенная фаза A (не исполнять до senior / после D)

Связь сохранена; cold F1b **не** стартовать из этой карты:

- [`STRATEGY_TAU_PER_SPAN_THEN_AXON_2026-10-23.ru.md`](STRATEGY_TAU_PER_SPAN_THEN_AXON_2026-10-23.ru.md) §3 — норматив аксонного тренера
- [`../plans/AGENT_PLAN_2026-10-20/cards/F1_fast_epsp_pilot.md`](../plans/AGENT_PLAN_2026-10-20/cards/F1_fast_epsp_pilot.md) — F1b checklist
- [`F1B_EXPLAINER_AND_STATUS_2026-10-23.ru.md`](F1B_EXPLAINER_AND_STATUS_2026-10-23.ru.md) — N0/N1 vs рост аксонов источников
- Аудит E1.6 / этап 6; `DEBT-F1b` OPEN

Будущий шаг: отдельный тренер; рост сегментов аксонов нейронов-источников; пилот verify-first (L=1, быстрый τ, `NAxoneDelay`); не merge в Classic/Branch без fork.
