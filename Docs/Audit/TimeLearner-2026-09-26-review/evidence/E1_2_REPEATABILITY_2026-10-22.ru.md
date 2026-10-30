# E1.2 — повторяемость измерения (Reset vs без Reset)

Постановка: для одной фиксированной структуры измерить разброс **амплитуды пика** и **латентности t_peak** по **20 пачкам с Reset** и **20 без**, и предложить допуски F4 не уже **3σ** (план [`TIMELEARNER_AUDIT_AND_PLAN_2026-10-20.ru.md`](../TIMELEARNER_AUDIT_AND_PLAN_2026-10-20.ru.md) §E1.2 / F4). Trainer×Mode для probe-физики **N/A**; конфиги Train/Test — probe-only (`IsNeedToTrain=0`), шаблон Test [`TimeLearnerMatrix/W01/inputs/W01_CL50_N0_PSIoff/Test`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N0_PSIoff/Test). G1 RERUN / F1b cold / KeepDone W33 **не** запускались.

**Модель:** `NSPNeuronGenAsymRmD001C1e9`, **L = 10** (все 4 дендрита), **TipR = 8.6×10⁷**, N = 1, ISI = 2.0 с, f = 20 кГц. Выбор L=10 опирается на E1.0 PARTIAL (timing OK, amp cal известна; Gen L=50 / DEBT-C1 silent избегаем).

| Arm | Хост | Протокол | n |
|-----|------|----------|--:|
| **reset** | Elder-1 (`.11`) | 20 независимых cold-start Console на одном single-pulse probe | **20/20** rc=0 |
| **noreset** | M40 (`.17`) | один multi-pulse прогон (20 onset в InputPattern) | см. PARTIAL ниже |

**Console sha256 (оба хоста):** `4a0658f34736bf0575f051d6ee790e9342f5df8ebf904956640fbeaaa7fdc5d7`.  
**Артефакты рантайма:** `$HOME/TLAgent-20261020/agent-reports/E1_2_20261022/` (reset traces + logs); noreset trace на `.17`: `$DATA/scratch/E1_2/noreset/SelectivityLog/test_trace.csv`.  
**Машиночитаемо:** [`E1_2_REPEATABILITY_2026-10-22.tsv`](E1_2_REPEATABILITY_2026-10-22.tsv), [`E1_2_REPEATABILITY_2026-10-22.json`](E1_2_REPEATABILITY_2026-10-22.json). Скрипт: [`tools/e1_2_repeatability.py`](tools/e1_2_repeatability.py).

## Результаты

### Reset (n = 20) — DONE

Все 20 cold-start пачек **битово совпали** по пику и латентности (стимул-относительная метрика):

| Метрика | mean | sample σ | min = max |
|---------|-----:|--------:|-----------|
| peak | **0.0022115747388351537** | **0** | да |
| t_peak | **0.0992 с** (99.2 мс) | **0** | да |

Совпадает с якорем E1.0 AsymRm L=10 (peak ≈ 0.002212, t_peak ≈ 99.65 мс) в пределах шага дискретизации. Вывод: после полного Reset измерение на этой структуре **детерминировано** в пределах float/шага сетки; случайный шум Console **не** задаёт масштаб для `kAmpNormEps`.

### No-Reset — PARTIAL

Запрошено 20 пачек в одном прогоне; фактически:

1. В шаблоне W01 остался **`MaxSpikesPerFeature = 4`**, поэтому multi-pulse InputPattern (20 onset) **не** отрабатывает как 20 независимых EPSP (исправление внесено в `e1_2_repeatability.py` для будущих прогонов; **повтор Console в этом turn не делался**).
2. Trace PatternResponseAnalyzer оборвался на **t_end ≈ 13.50 с** при Console `-t 42` — окна пачек 7…19 пусты.
3. В доступных окнах 0…6 валидный EPSP (peak > 1e−6) только на пачках **0, 1, 3, 6**; пачки 2, 4, 5 — численно плоские (пропуск стимула), не «шум амплитуды».

| Подмножество | n | mean peak | σ_amp | mean t_peak | σ_lat |
|--------------|--:|----------:|------:|------------:|------:|
| valid EPSP (0,1,3,6) | 4 | 0.001752 | 3.06×10⁻⁴ | 0.1002 с | 7.7×10⁻⁴ с |
| settled (pack > 0) | 3 | **0.001599** | **6.7×10⁻⁷** | 0.1005 с | **5.0×10⁻⁴ с** |

Пачка 0 noreset совпадает с reset (cold start процесса). Settled-пачки стабильно ниже на **≈ −27.7 %** относительно reset mean — тот же класс нестационарности, что A5 (0.01507 vs 0.01349 на W01 train), здесь на probe-only AsymRm L=10 / TipR=8.6e7 / ISI=2 с. **Эту систематику нельзя «закрыть» расширением eps_amp:** она требует F3 (`ResetNeuronBeforeTrainBurst`) / E1.3, а не ослабления F4.

## Предложенные допуски F4

База — **reset σ** (контракт «измерение после Reset»), пол `max(3σ, 1%·\|mean\|)` для amp и `max(3σ, 1/f)` для latency:

| Параметр | Значение | Комментарий |
|----------|----------|-------------|
| σ_amp (reset) | **0** | n=20 bit-identical |
| σ_lat (reset) | **0** | n=20 bit-identical |
| **eps_amp** (abs) | **2.212×10⁻⁵** | = 1% · 0.00221157 |
| **eps_amp** (rel) | **0.01** (1%) | для F4 `max(3σ, 1%·target)` |
| **latency_tol** | **5×10⁻⁵ с** (1 sample @ 20 кГц) | пол по сетке |

Вторично (не для расширения F4): σ_amp settled noreset ≈ 6.7×10⁻⁷ ≪ 1%; σ_lat settled ≈ 0.5 мс → 3σ ≈ 1.5 мс — полезно как оценка джиттера без Reset, но **bias −28%** доминирует.

Текущий `kAmpNormEps = 1e−5` **уже порядка** предложенного 1%-пола на этой амплитуде (≈2.2e−5); на более крупных пиках (Gen L=1 ≈ 0.015) 1% даёт ~1.5e−4 ≫ 1e−5 — F4 должен быть **относительным**.

## Вердикт

| Критерий §E1.2 | Статус |
|----------------|--------|
| 20 пачек с Reset, σ_amp / σ_lat | **DONE** (σ = 0) |
| 20 пачек без Reset | **PARTIAL** (4 valid EPSP; MaxSpikesPerFeature + короткий trace) |
| Допуски ≥ 3σ для F4 | **DONE** (пол 1% / 1 sample от reset) |
| **Итог E1.2** | **PARTIAL** |

**DEBT-C1-silent-soma** на этом прогоне **не** мешал (L=10). Для полного noreset×20: поднять `MaxSpikesPerFeature`, проверить длину trace, при необходимости повторить только noreset-arm — без G1 RERUN.

**Следующий логичный шаг:** F4 relative eps в коде (после senior), либо E1.3 / F3 A/B на cold; не раздувать eps под noreset bias.
