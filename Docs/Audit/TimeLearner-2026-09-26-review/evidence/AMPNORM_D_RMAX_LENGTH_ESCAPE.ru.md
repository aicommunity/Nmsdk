# D — Rmax overshoot: length escape (W3c)

Дата: 2026-10-06.  
Срез до фикса: SoftCold rematrix PARALLEL 13 PASS / 36 FAIL · Console `8589daff…` · PulseLib `b32d715` (W3 hold).

## Физика

`amp_dt = Initial − MaxAmp`. При TipR@ResistanceMax и `amp_dt < 0` (overshoot) R поднять нельзя. Down-step усиливает amp → re-climb → осцилляция `1e11↔0.85·Rmax` (снята W3 hold). Hold без DOF → ceiling freeze / Need=1 (корзина D).

**Рабочая степень свободы:** рост `DendriteLength` (cable attenuation) при hold R@Rmax; после `dt≥0` — штатный W3 undershoot down-step к CanonRmin.

**Отклонено:** latched R-descent (хуже overshoot + конфликт с W1 raise@Rmin).

## Код (W3c)

- `ChangeSynapseResistanceStatus`: overshoot-hold → `DendStatus=1` + cooldown; R не трогать; **сброс `DendStatus=-1`** на hold-тиках (иначе `ChangeDendriteStatus(active)` откатывает L до следующего armed grow).
- `ApplyPendingDendriteLengthChanges`: bypass settle при флаге; forced `delta=1`; **skip** `FeedforwardResistanceOnLengthGrow` + keep TipR@Rmax; **запрет shrink при TipR@Rmax**.
- Twin: base + Branch.

## Selective note (2026-10-06)

Первый selective SHA `4c3da052…`: keep 9/9 rc=0; `pa00` L=`49 41 25` (EstDelay OK) но TipR@`1e11` freeze — +ΔL откатывался Dissync-shrink. Фикс anti-shrink → Console `da3a6424…`; selective перезапущен целиком.

## EstDelay gaps

| case | archive | EstDelay |
|------|---------|----------|
| `phase6_480` | `EXP_480_gen_tiprmin` | 0.01 |
| `tn_classic` | `TimeNeuronTimeLearner` | 0.01 |

## Вне скоупа

LandscapeOk / `br25_on` / `fs50_preinh` / flat A / silent-mid gen (Need→0 + gate).
