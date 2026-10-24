# Campaign status — latest

**Активный план (приоритет):** [`../plans/PLAN_2026-10-25_dendrite_limits.md`](../plans/PLAN_2026-10-25_dendrite_limits.md)  
**Ветка:** `plan/2026-10-25-dendrite-limits` (от `timelearner_fix3`)  
**Обновлено:** 2026-10-24T18:00Z

Метрика волн: `sep_margin` + обязательная детекция цели; **Done_exact** и **Done_BE** раздельно. Волна без прошедшего контроля W0 не засчитывается. H0_tau_cm_per_span / TauH0 — **сняты с приоритета** (τ масштабируется неверно относительно плана §1).

---

## Очередь

| Блок | Статус | Коммит / note |
| --- | --- | --- |
| §0 F1 InhGrid neuron = AsymRm (не SymInh) | **code done** | `clone_inh_grid.py` → `NEURON_BASE`/`NEURON_PSI`; re-clone EXP перед следующей InhGrid-волной |
| §0 F2 PSI только классом нейрона | **code done** | убран Model `UsePresynaptic` патч |
| §0 F3 Test overlay NumSynapse + Ns==128 = saturated | **code done** | phase8/phase9 overlay; `not_converged_saturated` в `posttune_verify` |
| §0 F4 ложный ERROR Resistance bounds | **code done** | PulseLib Classic+Branch: `target_count==0` → true без ERROR |
| §0 F5 / R0 Train↔Test LTZ ≤5% | **script ready** | прогон после W0 артефактов |
| W0 br25_nextseg ×3 + R0 | **running** | 3× SoftCold `br25_nextseg`; Console `27ea0604ca9af64b`; logs `w0_br25_nextseg_logs/` |
| C1 доза-ответ торможения | **pending** | после W0 PASS детекции |
| W1/W2 sim Span | **pending** | после C1 / контроль в каждой волне |
| genasym SoftCold (`inh_c25_genasym_n0_pton`) | **running** — не стопать | poll ~262+; параллельно W0 |

---

## genasym (не блокер §0)

Параллельный Diag §6.3: InhGrid S25 gen fan-out + `NeuronClassName=AsymRm`. Лог: `evidence/inh_grid_logs/INH.inh_c25_genasym_*`. Не прерывать ради dendrite_limits.

---

## Next

1. Commit+push PulseLib → Bin → root (§0 block).  
2. Rebuild Console (F4).  
3. W0: `br25_nextseg` контроль (явный cold после §0 push).
