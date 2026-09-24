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

## Критерий «remediation закрыт»

T0 + T1 + T2 выполнены и задокументированы. Полный PASS семи cases — отдельно и только со свежими runs.
