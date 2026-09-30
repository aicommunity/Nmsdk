# Amp-norm / EOL stuck — классификация после S3.c/d

Дата: 2026-09-30 (после checkpoint `c790edb` / Bin `0bb8125`).  
План: [AMPNORM_EOL_INVESTIGATE.plan.md](AMPNORM_EOL_INVESTIGATE.plan.md).  
Diagnostic log: `evidence/metrics/AMPNORM_fs25_noprune.log` · run `fs25_gen_20260930T101032Z`.

## Полнота хвостов (вход)

- `DONE_TAILS` 2026-09-30T10:05:51Z
- 4 extended + 24 C1+C2, `missing_count=0`, все `rc=1`
- SoftCold desync снят ранее; здесь только **Need≠0 / EOL**

## Классификация extended (live TipR)

| case | polls Need=1 | live TipR (SNAP) | L live/params | XML Save | класс |
|------|--------------|------------------|---------------|----------|-------|
| `fs25_gen` `-t 640` | 222/222 | `2e7 2e7 **3.42e7** 8.6e7` | gold `6 5 4 1` (saved) | да (`child_rc=0`) | **(a) TipR not-at-Rmin** (dend2) |
| `asym50_preinh` `-t 1280` | 801/801 | `2e7×3 8.6e7` (=Rmin) | live `29 22 15 1` | нет (SIGTERM, XML flat) | **(b) TipR@Rmin Need=1** |
| `asym100_preinh` `-t 1280` | 801/801 | `2e7×3` | (live growth) | нет | **(b)** |
| `asym100_gen` `-t 1280` | 801/801 | `2e7×3` | (live growth) | нет | **(b)** |

`ResistanceMin=2e7`, `EnableDebug=1` уже в Parameters. После PRUNE slog=`0.00G` до конца — трассы ampDt мертвы (**H4**).

## Diagnostic re-run `fs25_gen --no-prune` (DONE)

| | |
|--|--|
| flags | `--train-t 640 --max-polls 801 --no-prune --snap-every 20 --slog-abort-gib 8` |
| конец | NM **exit 0** по `-t` (~poll **#369**, slog **7.49 G**); abort 8 G **не** сработал |
| Need | **1** все 369 polls |
| gate | `gate_ok=True`, `failure_class=train_incomplete` |
| Save | TipR `2e7 2e7 **3.42e7** 8.6e7`, L=`6 5 4 1` (live late L=`7 5 4 1`) |
| StatisticLog | ~7.5 G, затем **стёрт harness cleanup** — AmpDt/NoImprove traces **не сохранены** |

### SNAP TipR dend2

К poll#20 уже ≈`3.49e7`; дальше полоса **~34.2–35.0 M** без выхода к Rmin `2e7`:

- #20–100 ≈34.9 M → #120–160 ≈34.3 M → #180–320 **freeze** `34977812…` → #340/`#360` микросдвиги 34.2↔35.0 M

**Вывод:** класс **(a) подтверждён** — dend0/1 на Rmin, **dend2 mid-band stuck** весь `-t 640`. Для следующего diagnostic нужен `--keep-slog` / copy before cleanup.

## Гипотезы (кратко)

| H | Статус |
|---|--------|
| H1 mid-band / residual dt | **(a) подтверждён** SNAP; (b) всё ещё кандидат |
| H2 NoImprove | не доказан (traces wiped) |
| H3 length_ok | вероятен для (b); для fs25 L≈gold — слабее |
| H4 harness slog wipe | подтверждён (prune + post-run rmtree) |
| H5 softcold tip-1 | снят |

## Вердикт / next

1. Need=0 на fs25 **не** получен: TipR dend2 не доезжает до Rmin.
2. Next: `--keep-slog`; разбор TipR-update (`dt>5` skip / ready_for_r_tune); отдельно asym50 для (b) — **без** ослабления LandscapeOk.

## Не смешивать

- A_nonseparable, phase6 EstDelay, SoftCold SBM — отдельно / снято.
