# Campaign status 2026-10-20 (agent)

Постановка: автокампания AGENT_PLAN без human-gate (кроме infra); коммиты evidence/tools по ходу.

## Диск
- .11 свободно ~280+ ГБ после оффлоада EventsLog на `.17:/media/user/Data/from-11-offload-20261020/`.
- **Правило:** `<200 ГБ` — не STOP; лишнее уводить на Data-.17.

## Закрыто
- A0, R1, A2/B1/E0/E1 flags, D1 STOP (нет регрессии в окне PulseLib), A3.1 **A15_ACTIVE_AT_RUNTIME**, A3.2 relink≈DendriteLength, A1 BASELINE_DEGRADED, C2_MATCH, F1a MATCH, Stage0 tool-columns.

## В полёте
- D2.0 OK; D2.1 EstDelay отвергнут (1×); D2.2–D2.5 на .17; D2.1 rerun на .11; C1 live-soma OK / AsymRm calib.

## Дальше
- Дожать D2 summarize → R3/F2–F8 → E2/G1 labeled BASELINE_DEGRADED → Controller/Stage6 → SYNTHESIS.
