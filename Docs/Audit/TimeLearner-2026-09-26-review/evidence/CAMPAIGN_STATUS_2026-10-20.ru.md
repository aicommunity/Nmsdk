# Campaign status 2026-10-20 (agent)

Постановка: автокампания AGENT_PLAN; коммиты evidence/tools по ходу (`timelearner_fix2`, local ahead).

## Диск
- .11 ~280+ ГБ free; EventsLog offload на `.17` Data. **Не STOP при <200 ГБ.**

## Закрыто
- A0/R1/A2/B1/E0/E1 flags; D1 STOP; A3 A15_ACTIVE + relink; A1 DEGRADED; C2_MATCH; F1a; Stage0 tools; C1 NSP OK / AsymRm +47% calib.

## D2
- D2.0/D2.2: train `converged_need0`, Test **silent** fires=0
- D2.1 EstDelay=0.01: not_converged (hyp rejected)
- D2.3 W02: not_converged TipR@Rmax
- D2.4/D2.5 + local D2.1: running

## Дальше
- D2.4/5 summarize → R3/F2–F8 → E2/G1 (BASELINE_DEGRADED) → Controller → SYNTHESIS
