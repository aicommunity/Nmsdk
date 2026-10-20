# C1 set1 — NSPNeuronGen L=51,43,25,1

Постановка: сравнить одиночный EPSP на соме Console с офлайн-моделью кабеля (`tools/cable_model`) на шаблоне W02_CL480_N1_PSIoff/Test при TipR=8.6e7, ISI=2 с, f=2000 Гц.

| Trainer×Mode | Span | NeuronModel | L | peak err | t_peak err | FWHM err | ok | Train | Test |
|---|---|---|---|---|---|---|---|---|---|
| probe (IsNeedToTrain=0) | 480 tpl | NSPNeuronGen | 51 | −100% (meas=0) | — | — | no | scratch/C1/p1 | =probe |
| | | | 43 | −6.3% | 0% | 0% | yes | | |
| | | | 25 | −100% (meas=0) | — | — | no | | |
| | | | 1 | −6.5% | +3.4% | 0% | yes | | |

Вердикт set1: `MODEL_MISMATCH_OR_INVALID` — `soma_0` и `soma_2` во всём `test_trace.csv` тождественно 0 при `wiring_after.ok=true` и taps 51/43/25/1. Дендриты L=43 и L=1 совпадают с моделью в допусках 10/5/10%. Сохранить как DEBT-C1-silent-soma; продолжить наборы 2–7 с пометкой, наборы с silent-каналами не валидируют модель целиком.

## C1 set2 — L=30,20,10,1

| L | ok | peak rel_err | t_peak | FWHM |
|---|---|---|---|---|
| 30 | yes | −6.3% | 0 | 0 |
| 20 | no | silent | — | — |
| 10 | yes | −6.3% | 0 | −0.7% |
| 1 | yes | −6.5% | +3.4% | 0 |

Вердикт set2: снова `MODEL_MISMATCH_OR_INVALID` из‑за одного silent-канала; три длины в допусках. Модель кабеля для NSPNeuronGen на живых каналах **валидна** (±7% peak, t/FWHM почти идеал).

## C1 set4 AsymRm L=25,10,4,1

```
MODEL_MISMATCH_OR_INVALID 0.01 0.001
25 False 0.46898663163566673 -0.0051968818708773455
10 False 0.4693072316885552 -0.012884043607532166
4 False 0.4699704289018981 -0.03155339805825249
1 False 0.38069723371324043 -0.12663755458515283
```
