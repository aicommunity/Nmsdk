# S3.a result — asym50_preinh after softcold_fix

Run: `_repro/runs/asym50_preinh_20260927T071438Z`  
Console `ec86430e…` · `softcold_fix=2026-09-27_sbm2_strip_tip1`  
Wall ≈3.4 h · polls=401 · `child_rc=-15` (poll-cap terminate)

## Verdict vs plan S3.a

| Критерий | Результат |
|----------|-----------|
| Снятие `timing_softcold_desync` (рост стартует) | **да** |
| Cold PASS / Need=0 | **нет** |
| Gate | FAIL rc=1 |

## Evidence роста (не в final Parameters)

| источник | TipR | L |
|----------|------|---|
| StatisticLog ~sim 62 s (до prune) | `2e7 2e7 2e7 8.6e7` | `27 22 15 1` |
| `posttune_tipr_live.txt` (prune poll#169) | same canon | `29 22 15 1` |
| final Parameters / tipr_final | **flat cold** `86e6×4` | `1 1 1 1` |

Train `config_sha256` before==after — NM **не** Save’нул Train Parameters (`Need` так и 1).  
Harness `failure_class=train_incomplete`, `tipr_class=flat` — по **XML**, не по live (misleading vs pre-fix frozen).

## Отличие от pre-fix

| | pre-fix (P2) | after fix |
|--|---------------|-----------|
| TipR runtime | flat весь budget | →canon за минуты |
| L runtime | stuck `1 1 1 1` | →~`29 22 15 1` |
| EndOfLearning | нет | нет (в 401 poll) |

## Harness note

После `PRUNE StatisticLog` slog остался `0.00G` ~230 polls — возможно, запись трасс сломалась после `rmtree` под живым NM. Не путать с soft-cold desync.

## Классификация

`timing_softcold_desync` → снято. Остаток: **B_partial / train_incomplete** (Need не 0; XML не flush) — кандидат на extended `-t` / разбор EOL, не повтор soft-cold topology fix.
