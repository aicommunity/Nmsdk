# Preflight фазы D (дендрит / H0) — 2026-10-23

Постановка: перед UploadClass H0 и cold-сеткой зафиксировать tip SHA на обоих хостах, подтвердить A15 на origin и выполнить R8 smoke в пределах лимитов Console (`.11`≤8, `.17`≤12).

## Tips (после sync)

| Компонент | SHA | Примечание |
|-----------|-----|------------|
| root `timelearner_fix2` | `23b6ff7ad` → bump после H0 commits | A15 port + strategy уже на origin |
| Bin | `7292522e` → `ab8c5bae` (SelectivityTauCm) | A15 B1/B2 на tip |
| PulseLib | `9efca9c` → `35cd074` (H0 UploadClass) | legacy classes untouched |
| Console `.11` | `dd4ebd0a…` (rebuild after H0a) | |
| Console `.17` | rebuild after pull `35cd074` | до rebuild: `4a0658f3…` (старше tip) |
| Якорь baseline | `tl-baseline-20261020` | не сбрасывался |

**`.17` sync path:** локальный `origin` URL `/home/user/Nmsdk` на `.17` битый; sync через `git fetch git@github.com:aicommunity/…` в detached tip (root/Bin/PulseLib). Backup untracked AGENT_PLAN: `/media/user/Data/TLAgent-20261020/scratch/pre-sync-backup-20261023T0826Z`.

## A15

FAIL Test 0 на tip Bin закоммичен и запушен (`7292522e` / root `23b6ff7ad`); evidence «до ремонта» не стиралось. См. [`A15_PORT_TO_TIP_2026-10-23.ru.md`](A15_PORT_TO_TIP_2026-10-23.ru.md).

## R8 smoke

Попытка `run_timelearner_matrix_queue --prepare` на `W01_CL50_N0_PSIoff` / `W10_HIST_br25_nextseg` **упала**: `matrix definition differs beyond line endings` (дрейф манифеста после A15 без `--refresh`). Канонические inputs на диске на месте; `--refresh` shared inputs **не** применяли (скилл / план).

**Альтернатива preflight (plan: smoke + sync-check):**

1. Sync-check tip SHA на `.11` и `.17` — **PASS** (одинаковые root/Bin/PulseLib до H0 bump).
2. SoftCold R8-якорь `posttune_verify --case br25_nextseg` на `.11` после rebuild H0 (не меняет legacy UploadClass) — запускается в фоне; ожидаемо PASS-остров Branch.
3. Полный E2 R8 A/B (дни) **не** перезапускался: E2_R8_SYNTHESIS уже EQUIVALENT; F3_R8 закрыт.

## Инструменты

cable_model/C2, E1.4, E0 `--train-param` — доступны. Лимиты cpu_gate: `.11` 8 / `.17` 12.
