# Карта дендрита (ворота D) — τ(Cm) per Span · 2026-10-23

**Статус ворот D:** карта **зафиксирована** как вход в фазу A. H0a (теория + UStorage + EXP) на origin; H0b cold dual-host **запущен** (ядро Span100 → далее 50/25/200/480); SPEC FINAL дендритного Controller закрыт. Senior: на Span, где MaxL/FWHM/silent/stall не закрываются согласованной τ и mods, нужен **новый носитель задержки** (аксонный тренер), а не ещё одна единая τ.

Группировка: [`RESULT_GROUPING_HIERARCHY.ru.md`](RESULT_GROUPING_HIERARCHY.ru.md). Стратегия: [`STRATEGY_TAU_PER_SPAN_THEN_AXON_2026-10-23.ru.md`](STRATEGY_TAU_PER_SPAN_THEN_AXON_2026-10-23.ru.md).

---

## 1. H0a — Span → τ → Cm → StorageClass

Полная таблица: [`H0A_TAU_CM_TABLE_2026-10-23.ru.md`](H0A_TAU_CM_TABLE_2026-10-23.ru.md) / [`.tsv`](H0A_TAU_CM_TABLE_2026-10-23.tsv).

Кратко: S25 τ=0.5 мс Cm=5e-11; S50 τ=1 мс Cm=1e-10; S100 τ=2.5 мс Cm=2.5e-10; S200 τ=5 мс Cm=5e-10; S480 τ=10 мс Cm=1e-9 — все AsymRm Pack A, **новые** имена `…TauH0_S*`. Ideal margin +7…15%; cable `feasible=true` при MaxL≈100, но `m_oracle≈−0.02…−0.05` (FWHM/span≈0.34) — физический потолок пассивного кабеля.

PulseLib: `35cd074` (`CreateClassSamples`). Legacy `C25e12`/`C25e11`/`C1e9` **не** трогались.

---

## 2. H0b — cold dual-host (ядро)

| Хост | Лимит | Полоса (первая волна) |
|------|-------|----------------------|
| `.11` (10.245.1.11) | ≤8 | Classic×N0/N1 × S100 × {gen,preinh} × PostTune ON |
| `.17` (10.245.1.17) | ≤12 | Branch×N0/N1 × S100 × {gen,preinh,nextseg} × PostTune ON |

Ключи SoftCold: `h0_c100_*_pton`, `h0_b100_*_pton` (регистрация из `SelectivityTauCm/H0_EXP_MANIFEST.json` в `posttune_verify.py`).  
Train/Test: `Bin/Configs/SpikeSamples/StructTrain/SelectivityTauCm/EXP_*_{N0,N1}/{Train,Test}` — см. манифест и `DERIVED_FROM.md`.

Порядок Span (план): 100–200 → 50 → 25 → 480 (480 преимущественно `.17`). PostTune OFF — attempt-local/`h0_*_ptoff` после ядра ON; PASS-кандидаты — PASS×3 на том же SHA.

Машиночитаемый журнал запусков: [`H0B_COLD_LAUNCH_2026-10-23.tsv`](H0B_COLD_LAUNCH_2026-10-23.tsv) (обновляется по мере SERIES_DONE).

### Сводка по иерархии (заполняется по мере cold)

| Trainer×Mode | Span | NeuronModel | Mod | PostTune ON | PostTune OFF | Host | Train | Test | Need/fires/Acc/Цель | exit |
|--------------|------|-------------|-----|-------------|--------------|------|-------|------|---------------------|------|
| Classic×N0 | 100 | TauH0_S100 | gen | *running* | — | .11 | `SelectivityTauCm/EXP_classic_S100_gen_TauH0_N0/Train` | `…/Test` | TBD | TBD |
| Classic×N1 | 100 | TauH0_S100 | gen | *running* | — | .11 | `…_N1/Train` | `…/Test` | TBD | TBD |
| Branch×N0 | 100 | TauH0_S100 | nextseg | *running* | — | .17 | `EXP_branch_S100_nextseg_TauH0_N0/Train` | `…/Test` | TBD | TBD |
| … | … | … | … | … | … | … | … | … | … | … |

*(Полная сетка 88 ключей `h0_*`; строки добавляются в TSV без overwrite HIST.)*

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
- `DEBT-H0-tau-cm`: **narrowed** — H0a done; H0b in flight; ворота D открыты для фазы A по потолкам выше.
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
