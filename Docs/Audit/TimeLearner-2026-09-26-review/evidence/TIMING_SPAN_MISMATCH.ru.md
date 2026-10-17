# SoftCold FAIL: несоответствие span ↔ задержка сегментов / soft-cold топология

Дата: 2026-09-27. Console `ec86430e…`.  
Связано: [FAIL_ROOTCAUSE.ru.md](FAIL_ROOTCAUSE.ru.md), [RETEST_EXTENDED_TIME.plan.md](RETEST_EXTENDED_TIME.plan.md), [FAIL_TAXONOMY.json](FAIL_TAXONOMY.json).

## Гипотеза (подтверждена артефактами + кодом)

Провалы **asym50/100** (рост не стартовал) и **phase6_*** (рост не останавливается) — разные проявления одной оси:

> временны́е параметры кабеля / оценка `EstDelayPerSeg` и режим soft-cold **не согласованы** с длительностью паттерна (`span`) и с тем, что learner считает `DelayLenOf`.

Это **не** баг eps (`kAmpNormEps`) и **не** NonSeparable mid (корзина A).

---

## Код: как считается задержка

```970:975:Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearner.cpp
double NNeuronTimeLearner::DelayLenOf(int num) const
{
 if(num < 0 || num >= int(DendriteLength.size()) || DendriteLength[num] <= 1)
  return 0.0;
 return (DendriteLength[num] - 1) * EstDelayPerSeg;
}
```

При `DendriteLength[i] <= 1` модельная задержка **всегда 0**, независимо от фактического числа сегментов в Model.

`EstDelayPerSeg`: в AsymRm XML часто `0.002` с; default в коде `kDelayPerSegDefault = 0.005` с (Phase6 без тега → 5 мс/сег).

Soft-cold (`repro_cold_lib.soft_cold_reset_train`) **до фикса 2026-09-27**:

```
"""Historical soft-cold: param L/TipR + links→tip-1; keep fat Model cable."""
```

То есть в Parameters/Model **теги** L → `1 1 1 1`, TipR → flat, но **жирный кабель сегментов в Model сохранялся**.

**После фикса** (`softcold_fix=2026-09-27_sbm2_strip_tip1`): все `StructureBuildMode` → `2`, Model strip до tip-1, scalar `NumDendriteMembraneParts=1` — см. [SOFTCOLD_FIX_THEN_RETEST.plan.md](SOFTCOLD_FIX_THEN_RETEST.plan.md).

---

## Таблица наблюдений (патченные SoftCold)

| case | span | SBM (последний тег) | EstDelayPerSeg | gold L[0] | SoftCold конец L | TipR конец | Вердикт |
|------|------|---------------------|----------------|-----------|------------------|------------|---------|
| asym25_preinh | 25 ms | **2** | 0.002 | 15 | `1 1 1 1` | near Rmin/canon | TipR-only Done → затем **A** NonSeparable mid |
| asym50_preinh | 50 ms | **0** | 0.002 | 25 | `1 1 1 1` | **flat cold** | **B_frozen** — рост не стартовал |
| asym100_preinh | 100 ms | **0** | 0.002 | 52 | `1 1 1 1` | **flat cold** | **B_frozen** |
| asym100_gen | 100 ms | **0** | 0.002 | 52 | `1 1 1 1` | **flat cold** | **B_frozen** |
| fs25_gen | 25 ms | **2** | 0.005 | 6 | `6 5 4 1` (=gold) | near Rmin | **B_partial** — почти Done, мало `-t` |
| phase6_thr_only | 480 ms | **2** | **default 0.005** | 49 | **`97 81 49 1`** | **ceiling 1e11** | **B_runaway** — рост ушёл за gold |
| phase6_preinh250 | 480 ms | **2** | 0.005* | 51 | `100 81 53 1` | mix Rmin/ceiling | **B_runaway** |
| phase6_ltzcal_twin | 480 ms | **2** | 0.005* | 49 | `97 81 49 1` | ceiling 1e11 | **B_runaway** |

\* Phase6 archive без `EstDelayPerSeg` → runtime default 5 мс/сег.

Число сегментов в Model после soft-cold (уникальные `Dendrite*_N`): asym25 max_seg=**15** (fat), asym50 max_seg=**25** (fat), phase6 end max_seg=**97** (вырос).

---

## 1) asym50/100 — почему рост «не стартовал»

### Факты

- После soft-cold: `DendriteLength=1 1 1 1` ⇒ `DelayLenOf≡0`.
- Model всё ещё **fat** (asym50: сегменты до 25) — физическая задержка кабеля **не нулевая**.
- Archive packA span50/100: **`StructureBuildMode=0`** (no rebuild). Soft-cold делает `set_tag(..., "1")`, но в XML **несколько** тегов SBM; **последний остаётся 0** → эффективный режим без пересборки (`ABuild` вызывает `BuildStructure` только при SBM==1).
- TipR так и `86e6×4`, Need=1 весь poll budget.

### Механизм (рабочая модель)

Learner считает `delay_len=0` и пытается синхронизировать ISI span50/100 (нужны десятки мс задержки), при этом:

1. топология Model не согласована с `DendriteLength` (fat cable + L-тег=1);
2. SBM=0 мешает штатной пересборке после soft-cold;
3. amp-norm TipR не сдвигается с cold flat (нет `length_settled` / нет валидного пути роста).

Оценка «какой L нужен» при `EstDelayPerSeg=0.002`:  
`L ≈ 1 + span_ms/2` → span50≈26 (≈gold 25), span100≈51 (≈gold 52).  
То есть **целевой L согласован с span**, но SoftCold **не смог начать** движение к нему.

**Класс в taxonomy:** `B_tipr_frozen_cold` + метка `timing_softcold_desync` (SBM=0 / fat+L=1).

**Не лечится** слепым ×4 `-t`, пока не форсировать SBM=2 на **всех** тегах и/или strip-cold / BuildStructure после soft-cold.

---

## 2) phase6_* — почему рост «не останавливался»

### Факты

- SBM=**2** — рост **идёт**.
- `EstDelayPerSeg` default **5 мс/сег**.
- SoftCold с L=1; к концу L[0]≈**97** при MaxDendriteLength=100.
- Расчёт: `1 + 480ms/5ms ≈ 97` — совпадает с финальным L.
- Gold в archive: L≈**49** ⇒ модельная задержка ≈240 мс (половина span) — gold **не** соответствует «наивному» `span/EstDelayPerSeg`.
- TipR упирается в **1e11**; Need=1; mid silent.

### Механизм

При SoftCold learner гонит длину по `needed ≈ f(pattern, peaks)` и кабельной оценке `(L-1)*EstDelayPerSeg`.  
С default 5 мс и span 480 мс равновесие упирается в **L~97**, не в gold 49. Amp-norm на такой длине не сходится (TipR→ceiling) → `EndOfLearning` не наступает.

**Класс:** `B_runaway_length` / бывший `B_partial_growth_need1` с уточнением `timing_est_delay_vs_span`.

**Больший `-t`:** может добить до MaxDendriteLength=100 и всё ещё Need=1 — **низкий приоритет** без правки EstDelayPerSeg / soft-cold контракта. Имеет смысл один probe ×2, затем stop.

---

## 3) Почему asym25 / fs25 выглядят «нормально» на той же оси

| | asym25 | fs25 |
|--|--------|------|
| SBM | 2 | 2 |
| SoftCold | TipR→canon при L-теге `1 1 1 1` | L дошёл до gold `6 5 4 1` |
| span | 25 ms короткий | 25 ms + EstDelay=5 мс → L≈6 (=gold) |
| Итог Train | Need=0 | Need=1 (мало `-t`, почти Done) |

Короткий span + SBM=2 согласованы с EstDelayPerSeg; fat-cable soft-cold меньше ломает путь.

---

## 4) Метки для всех таких провалов

| Метка | Критерий | Кейсы сейчас |
|-------|----------|--------------|
| `timing_softcold_desync` | SoftCold: L-тег≤1, Model fat, TipR flat, Need=1, часто SBM last=0 | asym50_preinh, asym100_preinh, asym100_gen |
| `timing_est_delay_vs_span` | SoftCold: L уходит ≫ gold ≈ `1+span/EstDelayPerSeg`, TipR ceiling, Need=1 | phase6_thr_only, phase6_preinh250, phase6_ltzcal_twin |
| `timing_ok_budget` | Рост к gold, Need=1 только из‑за `-t`/polls | fs25_gen (+ ожидать fs* с тем же паттерном) |
| `timing_n/a_quality` | Need=0 TipR canon, FAIL = NonSeparable mid | asym25_preinh, br25_on |

После Phase 5: каждый новый FAIL классифицировать в `FAIL_TAXONOMY.json` одной из меток выше.

---

## 5) Что делать позже (не в этом прогоне)

1. **Harness soft-cold:** форсировать `StructureBuildMode=2` на **всех** вхождениях тега; после soft-cold — `BuildStructure` или strip-cold для packA SBM=0.  
2. **Не** ставить asym50/100 в extended-time queue, пока не снят `timing_softcold_desync`.  
3. **Phase6:** либо задать `EstDelayPerSeg` согласованный с gold (`≈ span_eff/(L_gold-1)`), либо soft-cold не с L=1 при default 5 мс; extended-time — только probe.  
4. **fs25 / B_partial с L→gold:** оставить в [EXTENDED_TIME_MANIFEST](../../../Bin/Configs/SpikeSamples/StructTrain/_repro/EXTENDED_TIME_MANIFEST.txt).  
5. Документировать в EXPERIMENTS примечание: `fail_tag=timing_*` для SoftCold строк.

---

## 6) Краткий вывод

Гипотеза пользователя верна как рамка:

- **asym50/100:** span требует ненулевую кабельную задержку, а SoftCold даёт `DelayLenOf=0` + fat Model + SBM=0 → обучение **не стартует**.  
- **phase6:** span 480 мс при `EstDelayPerSeg=5 мс` толкает L→~97 (не gold 49) → рост **не останавливается**, TipR в потолок.  
- Это ожидаемый класс FAIL при SoftCold, а не «просто мало времени» (кроме fs25-подобных).
