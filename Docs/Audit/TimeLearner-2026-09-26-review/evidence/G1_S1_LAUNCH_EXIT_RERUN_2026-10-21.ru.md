# G1 S1 — RERUN после exit-audit (launch_exit_nonzero_rerun)

> Исторический документ: указанные ниже shell-команды относятся к аудиту октября2026. Исполняемые файлы удалены из текущего дерева; источники доступны только по зафиксированным Git-ссылкам. Это не инструкция запуска текущего pipeline и не разрешение возобновить серию D.
> Источники: [refresh_waves.sh](https://github.com/aicommunity/Nmsdk/blob/fa53680d62ce9dedbee464fc55418dd3f76a0ca6/Docs/Audit/TimeLearner-2026-09-26-review/plans/AGENT_PLAN_2026-10-20/tools/refresh_waves.sh).


**UTC:** 2026-10-21T16:39Z. **Причина:** rep3 [`launch.exit` ≠ 0](G1_S1_LAUNCH_EXIT_AUDIT_2026-10-21.ru.md) на 9/12 волн; **не** трогаем W01/W13/W33 (exit=0).

**ASSIGNMENTS:** строки `G1_S1_RERUN` с `reason=launch_exit_nonzero_rerun` на `.host11` и `.host17`.

| Host | Волны rerun | Launcher tmux | Sel TSV |
|------|-------------|---------------|---------|
| `.11` | W02, W31, W37 | `drv-G1_S1_launcher11` | `G1_selected_rerun_launch_exit.tsv` |
| `.17` | W04, W08, W09, W10, W11, W12, W48 | `drv-G1_S1_launcher17` | то же (фильтр по `host`) |

**Подготовка:** lanes restore из `TLAgent-offload/lanes/g1-s1-w*-done-*` (W37 на `.11` — `make_lane`, offload не было). `refresh_waves.sh` — **WARN** (detached HEAD в lane Bin, без agent branch); queue стартует с существующими manifests.

**Скрипты:** `$REPORTS/G1/launch_g1_rerun_launch_exit.sh` → `launch_g1_host.sh`, `HOST_LIMIT` 8 / 12, 3 rep.

**Не rerun:** W01, W13, W33.

---
Зеркало: `/home/user/TLAgent-20261020/agent-reports/G1/G1_S1_LAUNCH_EXIT_RERUN_2026-10-21.ru.md`.
