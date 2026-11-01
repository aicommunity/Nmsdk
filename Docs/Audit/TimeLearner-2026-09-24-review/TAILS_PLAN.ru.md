# Хвосты после R01–R07 remediation (2026-09-24)

Основание: [PLAN.ru.md](PLAN.ru.md), [README.md](README.md). Код закоммичен; приёмка PLAN закрыта **не полностью**.

## Коммиты

| Репо | SHA | Содержание |
|------|-----|------------|
| PulseLib | `8d429e7` | R01–R05 PostTune/Analyzer |
| Bin | `4521415` | R06 harness, metrics, P1.5/P2 protocols, build_manifest |
| root | `7c0c0d8` | gitlinks + REMEDIATION_NOTES + status |

Verifier unit: **21/21**. Console в manifest собран **до** PulseLib `8d429e7` → нужна повторная пересборка перед control runs.

## Соответствие PLAN / аудиту

| Пункт | Код | Приёмка | Статус |
|---|---|---|---|
| P0.1 R06 clean workdir / accept_run / phase9 | да | unit negatives; нет e2e crash+stale artifacts | частично |
| P0.1 build manifest полный | частично | SHA+gitlinks; нет libs/dirty/post-commit rebuild | хвост |
| P0.2 R03/R04 SampleState + Result reset | да | Branch/posttune probes не перепрогнаны | частично |
| P0.2 weights identity | слабо | clear metrics на fallback; нет TipR hash | хвост |
| P0.3 R01 close-first + censored | да | нет scheduler reachability; нет Dataset→CSV e2e | частично |
| P0.3 R02 delay≥late + pending neu | да | нет advance_window на новом бинарнике | частично |
| P0.3 R07 schema/N=1/CSV v3 | да | нет N=1..8 сквозных; legacy=alias не historical | частично |
| P1.4 R05 collector | да | `branch_ltz_mode` не подтверждён | частично |
| P1.5 4 control runs | протокол | **не запускались** | открыто |
| P2 morphogenesis | протокол | ждёт FAIL после P1.5 | ожидает |
| P3 clone READMEs | 1/7 | только br25_on | хвост |
| P3 Preinh/Delay/CLI | нет | не исполнялись | открыто |

Аудит README: без свежих run-bundles нельзя принимать cold PASS и нельзя локализовать FAIL только в морфогенез — **остаётся в силе**.

## План закрытия хвостов

### T0 — Rebuild + regression floor (блокер)

1. Пересобрать `NeuroModelerConsole` после PulseLib `8d429e7`.
2. Обновить `build_manifest.json` (SHA, gitlinks, dirty=clean, compiler, `ldd`).
3. GUI 13 / CE 9 (без A12) / Branch 8 / verifier 21.
4. `Scripts/audit-probes/review-20260924`: timeout/NaN/stale Success / incomplete_sample / branch_ltz больше не показывают ошибочный mid.

### T1 — Приёмка измерения без cold

- R06: e2e negative (mock crash + stale Asym50 flag/live/CSV) → fail, без переноса weights/mid.
- R03/R04: probes timeout×3 / NaN / double train / fallback; опц. TipR identity hash.
- R01: Dataset+Analyzer reachability → запись в status.json.
- R02/R07: N=1..8 + advance_window + censored → silence не PASS.

### T2 — P1.5 control runs (обязательный evidence)

На clean workdir, одной сборке: Branch25 gold; Branch25 soft_cold; Asym50 stale-flag isolation; Asym50 cold. Полные bundles в `_repro/runs/`. Не ослаблять LandscapeOk.

### T3 — P2 только если T2 FAIL

По `_repro/MORPHOGENESIS_P2.md`: br25_on, один фактор; затем остальные cases; phase6 dual expect.

### T4 — P3 docs / executable

- 6 оставшихся EXP_*/README (clean workdir; current ≠ gold).
- Preinh Storage/XML; NPulseDelay |Delay|<.001; CLI `-S` без `-x`.
- status: `verified` только с путями к probes/bundles.
- RU/EN + local Markdown links.

## Сделано (T0–T2 / H1–H2)

| ID | Статус |
|---|---|
| T0 rebuild + floor | DONE |
| T1 measurement probes | DONE |
| T2 control runs | DONE (gold PASS; soft_cold/asym50 FAIL documented) |
| H1 Canon vs Keep | DONE |
| H2 flag_flush TipR/Need | DONE |

## Осталось (долги D1–D6)

См. план долгов (не PLAN.ru.md): D1 measure / D2 harness / D3 morpho H3–H4 / D4 cold matrix / D5 Preinh·Delay·CLI / D6 docs sync.

| ID | Статус (2026-09-24 вечер) |
|---|---|
| D1 | DONE — `d1_*.json` / R04 txt |
| D2 | DONE — tipr hash + asym50 diag + unit 24 |
| D3 | DONE — H3 no_material_diff; H4 no differs; overlay skipped |
| D4 | DONE — 0/6 PASS; `D4_matrix_summary.json`; no 7/7 claim |
| D5 | DONE — `d5_*` |
| D6 | DONE — status/TAILS/reconcile/POST_TRAIN_VERIFY + EXP README lines |

Verifier unit: **24/24**. Bin gitlink `0600e38` (tipr hash + cold matrix). PulseLib `8d429e7`.

**Сводка экспериментов для чтения:** [EXPERIMENTS_AFTER_FIXES.ru.md](EXPERIMENTS_AFTER_FIXES.ru.md).
