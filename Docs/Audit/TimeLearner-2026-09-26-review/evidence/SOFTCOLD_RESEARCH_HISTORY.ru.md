# SoftCold — история планов исправления и результатов

Дата сводки: **2026-10-08**.  
Актуальный baseline: SoftCold full49 HEAD **13 PASS / 36 FAIL** · Console `18f0ef414b1f9c06` · PulseLib `dc2866a` · реестр [`EXPERIMENTS.md`](../../../Bin/Configs/SpikeSamples/StructTrain/EXPERIMENTS.md) (§ SoftCold last matrix).

Цель документа — одна хронология: **план → что сделали → что дали эксперименты**. Планы Cursor скопированы в [`plans/`](plans/). Ранние планы аудита лежат рядом в `evidence/` и корне review.

```mermaid
flowchart LR
  P0[Cold audit / SoftCold desync]
  P1[Extended -t / AmpNorm investigate]
  P2[AmpNorm EOL W0-W4]
  P3[Parallel rematrix 13/36]
  P4[D escape W3c-W3e]
  P5[Open Gaps / residual]
  P6[Full49 HEAD 13/36]
  P0 --> P1 --> P2 --> P3 --> P4 --> P5 --> P6
```

---

## Текущий экспериментальный итог (куда пришли)

| Метрика | Значение |
|---------|----------|
| SoftCold case | 49/49 DONE |
| PASS | **13** (список ниже) |
| FAIL | **36** (корзины D≈20 · E≈6 · B≈4 · A≈3 · N=1 · G=2) |
| SNAP | [SOFTCOLD_FULL49_SNAP.md](SOFTCOLD_FULL49_SNAP.md) |
| Аудит | [SOFTCOLD_CONVERGENCE_AUDIT.ru.md](SOFTCOLD_CONVERGENCE_AUDIT.ru.md) |
| STATUS | [STATUS.ru.md](../STATUS.ru.md) |

**PASS full49 HEAD:** `asym50`, `asym50_preinh`, `asym25_preinh`, `asym100_preinh`, `br50_gen`, `br50_preinh`, `br100_preinh`, `br25_nextseg`, `br25_off` (SoftColdOff), `fs25_gen`, `fs25_preinh`, `fs100_preinh`, `ltz50_gen`.

**Главный вывод цепочки:** harness SoftCold desync снят; AmpNorm/EstDelay/Rmax-escape дали **часть** Cold PASS (с 0 → 13), но D-ceiling / E@Rmin / NonSeparable / протокольные gate FAIL остаются — full49 после Open Gaps **не улучшил** PASS-набор rematrix.

---

## Хронология планов → результаты

### 1. Cold audit fixes (2026-09-26…)

| | |
|--|--|
| План | [COLD_AUDIT_FIXES.plan.md](../COLD_AUDIT_FIXES.plan.md) · копия Cursor [`plans/cold_audit_fixes_e6d3a0e9.plan.md`](plans/cold_audit_fixes_e6d3a0e9.plan.md) |
| Цель | Wave-C inventory, `kAmpNormEps`, SoftCold A/B AsymRm, harness provenance, Branch br25, DEFER C1/C2 |
| Эксперименты | P0–P3 evidence: [P0_unpatched_baseline.md](P0_unpatched_baseline.md), [P1_eps_fix.md](P1_eps_fix.md), [P2_asymrm_ab.md](P2_asymrm_ab.md), [P4_br25_B1.md](P4_br25_B1.md) |
| Итог | Eps/harness база; SoftCold Cold PASS **не** получен; DEFER ушёл в отдельную волну |

### 2. SoftCold fix → retest (desync / SBM)

| | |
|--|--|
| План | [SOFTCOLD_FIX_THEN_RETEST.plan.md](SOFTCOLD_FIX_THEN_RETEST.plan.md) |
| Результат-анализ | [SOFTCOLD_PLAN_RESULT.md](SOFTCOLD_PLAN_RESULT.md) |
| Цель | SBM=2 + tip-1 strip; снять `timing_softcold_desync`; retest asym*/fs*/phase6 + DEFER |
| Эксперименты | S2 smoke OK; S3.a desync lifted; S3.c 24/24 `rc=1`; **0 SoftCold PASS** из целевых 9 |
| Итог | **Успех desync**; Cold PASS / NonSeparable / phase6 EstDelay — **вне** этого фикса |

### 3. Extended `-t` + таксономия FAIL

| | |
|--|--|
| План | [RETEST_EXTENDED_TIME.plan.md](RETEST_EXTENDED_TIME.plan.md) |
| Цель | Не жечь wall-clock на A/desync; P0 extended для `B_partial_growth_need1` |
| Эксперименты | 4/4 extended `rc=1`; TipR растёт, **Need=1** остаётся → AmpNorm/EOL |
| Итог | Больший `-t` **не** закрывает EOL; дальше AmpNorm investigate |

### 4. AmpNorm EOL investigate

| | |
|--|--|
| План | [AMPNORM_EOL_INVESTIGATE.plan.md](AMPNORM_EOL_INVESTIGATE.plan.md) |
| Диагноз | [AMPNORM_EOL_STUCK.ru.md](AMPNORM_EOL_STUCK.ru.md), keep-slog [AMPNORM_fs25_KEEPSLOG.ru.md](AMPNORM_fs25_KEEPSLOG.ru.md) / [AMPNORM_asym50_KEEPSLOG.ru.md](AMPNORM_asym50_KEEPSLOG.ru.md) |
| Цель | Почему нет EndOfLearning: (a) mid-band TipR, (b) @Rmin Need=1 |
| Эксперименты | Классификация (a)/(b); code-map `AllSynapsesNormalized`; `--keep-slog` |
| Итог | Расследование **done**; C++ fix — следующий план |

### 5. Follow-up remediations W0–W6 (после desync)

| | |
|--|--|
| План | [`plans/cold_follow-up_remediations_efe00c4b.plan.md`](plans/cold_follow-up_remediations_efe00c4b.plan.md) |
| STATUS | [STATUS.ru.md](../STATUS.ru.md) § W0–W6 |
| Эксперименты | W1 mid→Rmin; W2 length tol; W3 EstDelay Phase6 L≈gold; W4 NonSeparable (не трогали LandscapeOk); W6 matrix **37 RC → 0 PASS** |
| Итог | Точечные симптомы сняты; **Cold SoftCold PASS = 0** на той кампании ([SOFTCOLD_FINAL_MATRIX.ru.md](SOFTCOLD_FINAL_MATRIX.ru.md)) |

### 6. Registry: Working ≠ SoftCold

| | |
|--|--|
| План | [`plans/registry_protocol_clarity_541cfa97.plan.md`](plans/registry_protocol_clarity_541cfa97.plan.md) |
| Контракт | [PROTOCOL_WORKING_VS_LASTCHECK.ru.md](PROTOCOL_WORKING_VS_LASTCHECK.ru.md) |
| Эксперименты | Не прогон; схема колонок (позже SoftCold/SoftColdDetail) |
| Итог | GoldTest PASS больше не маскирует SoftCold FAIL |

### 7. AmpNorm EOL fix (W0–W4 code waves)

| | |
|--|--|
| План | [AMPNORM_EOL_FIX.plan.md](AMPNORM_EOL_FIX.plan.md) · Cursor [`plans/ampnorm_eol_fixes_3c7a888d.plan.md`](plans/ampnorm_eol_fixes_3c7a888d.plan.md) |
| Результат | [AMPNORM_EOL_RETEST_RESULT.md](AMPNORM_EOL_RETEST_RESULT.md), W0 [AMPNORM_EOL_W0_SNAP.md](AMPNORM_EOL_W0_SNAP.md) |
| Цель | E/B Done@Rmin/midband; D Rmax-escape; затем full SoftCold 49 |
| Эксперименты (selective) | Keep PASS: asym50/ltz50/br50; W1: **asym100_preinh PASS**; W2: **fs25_gen/preinh PASS**; D smoke всё ещё FAIL; W4 full matrix **aborted 22/49** (5 PASS / 17 FAIL) |
| Итог | Первые Cold PASS на AmpNorm-якорях; полный 49 на том бинаре не довели |

### 8. Parallel rematrix SoftCold 49×6

| | |
|--|--|
| План | [`plans/softcold_parallel_rematrix_eb3445a3.plan.md`](plans/softcold_parallel_rematrix_eb3445a3.plan.md) |
| Цель | СТОП W4 → EstDelay PhaseA/PSI → W3 dt≥0 → SoftColdOff fires → parallel orchestrator → полный 49 |
| Эксперименты | Console `8589daff…` / PulseLib `b32d715` → **13 PASS / 36 FAIL** (тот же PASS-набор, что позже HEAD) |
| Итог | **Первый устойчивый SoftCold baseline 13/36**; EstDelay L≠97 на pa00 |

### 9. D Rmax length-escape (W3c…)

| | |
|--|--|
| План | [`plans/d_rmax_length_escape_1d50f760.plan.md`](plans/d_rmax_length_escape_1d50f760.plan.md) |
| Док | [AMPNORM_D_RMAX_LENGTH_ESCAPE.ru.md](AMPNORM_D_RMAX_LENGTH_ESCAPE.ru.md) |
| Цель | При hold@Rmax растить L (attenuation), не осциллировать TipR |
| Эксперименты | Selective D-core; full49 **отложен** до зелёного selective |
| Итог | Волны W3c→W3e ниже |

### 10. W3c apply + stall abort → W3d multi-dend → W3e undershoot

| План | Фокус | Эксперименты / итог |
|------|--------|---------------------|
| [`plans/w3c_apply___stall_abort_01bf86de.plan.md`](plans/w3c_apply___stall_abort_01bf86de.plan.md) | ApplyPending / stall abort | Partial SoftCold; registry skip |
| [`plans/w3d_multi-dend_escape_5e464db7.plan.md`](plans/w3d_multi-dend_escape_5e464db7.plan.md) | Multi-dend length escape | L растёт на D-якорях |
| [`plans/w3e_rmax_undershoot_1f9923bc.plan.md`](plans/w3e_rmax_undershoot_1f9923bc.plan.md) | TipR down-step после length; MaxL overshoot | Partial PARALLEL D-core; **full49 отложен** (P1+P2 не зелёные) |
| [`plans/пороги_осцилляция_need_52604238.plan.md`](plans/пороги_осцилляция_need_52604238.plan.md) | Пороги / осцилляция Need | Диагностика anti-bounce |

**Свод по D-волне:** length-escape и undershoot улучшили динамику, но **не** дали 4/5 D-core PASS → политика «full49 закрыт» до Open Gaps override.

### 11. Open Gaps + D residual (перед full49 HEAD)

| | |
|--|--|
| Планы | [`plans/open_gaps_research_c6687d74.plan.md`](plans/open_gaps_research_c6687d74.plan.md), [`plans/d_residual_investigate_b4fa4944.plan.md`](plans/d_residual_investigate_b4fa4944.plan.md) |
| Docs | [OPEN_GAPS_E_B.ru.md](OPEN_GAPS_E_B.ru.md), [OPEN_GAPS_D_CLASSIFY.ru.md](OPEN_GAPS_D_CLASSIFY.ru.md), [SOFTCOLD_PROTOCOL_FAILS.ru.md](SOFTCOLD_PROTOCOL_FAILS.ru.md) |
| Цель | D_algo_open DEFER; закрыть W0 traces; E/B/protocol без ослабления gate; residual anti-bounce |
| Эксперименты | Diagnostic SoftCold E/B/keep; residual 1–3 → условный фикс; **full49/registry закрыты** до явного override |
| Итог | Пробелы классификации закрыты; AmpNorm algo-fix **не** открывали |

### 12. SoftCold Full 49 HEAD (override)

| | |
|--|--|
| План | [`plans/softcold_full_49_d40e240c.plan.md`](plans/softcold_full_49_d40e240c.plan.md) |
| Результат | [SOFTCOLD_FULL49_SNAP.md](SOFTCOLD_FULL49_SNAP.md), RCS `_repro/SOFTCOLD_HEAD_rcs.txt` |
| Цель | PARALLEL matrix на anti-bounce + EolGateAudit; SNAP; apply реестра; автокоммит |
| Эксперименты | **49/49 · 13 PASS / 36 FAIL** — PASS-набор = rematrix; AmpNorm DEFERRED не снимался |
| Итог | Новый HEAD baseline зафиксирован; **нет** прироста PASS vs rematrix |

### 13. Rs/Rm-предел и выборочная D-перепроверка на текущем C++-срезе

| | |
|--|--|
| Отчёт | [`RSRM_D_RETEST_2026-10-08.ru.md`](RSRM_D_RETEST_2026-10-08.ru.md) |
| База | root `0246f1f`, Bin `f04faa3`, PulseLib `d1344cb`; Linux Console SHA записан в отчёте и evidence bundle |
| Выборка | 9 SoftCold cases + диагностические па00-варианты; отдельный gate-only повтор pa00 с правильным `span_ms=480` |
| Train | Основные `D_algo_open` cases `pa00`, `phase6_480`, `phase6_thr_only`, `tn_classic` финализировались с `Need=0`; gate-исходы оценены отдельно |
| Ограничение | Низкий Rs/Rm cap и ослабление `ResistanceMin` приводят к ожидаемому C++-отказу на Rmax; это не доказательство невозможности решения |
| Структурный режим | Rs/Rm cold init, вычисленный cap и W3 изолированы; Classic/Branch проверки прошли тела тестов |

---

## Сводка «планка → Cold PASS»

| Этап | SoftCold Cold PASS (характерно) |
|------|----------------------------------|
| До SoftCold harness fix | 0 (часто desync / frozen TipR) |
| После SoftCold fix + extended `-t` | 0 |
| После W0–W6 follow-up | 0 (37 RC) |
| После AmpNorm EOL selective | первые PASS (asym100_preinh, fs25_*) |
| После parallel rematrix / full49 HEAD | **13 / 49** (стабильный набор) |

---

## Где смотреть реестр экспериментов

| Вопрос | Куда |
|--------|------|
| Успешный протокол (Gold / SoftCold / …) | колонка **Working** + **Acc** в EXPERIMENTS / SUCCESSFUL |
| Последняя cold-попытка | **SoftCold** + **SoftColdDetail** (одинаковы на всех строках Имени) |
| Все 49 case одной таблицей | EXPERIMENTS § SoftCold last matrix |
| Почему Working ≠ SoftCold | [PROTOCOL_WORKING_VS_LASTCHECK.ru.md](PROTOCOL_WORKING_VS_LASTCHECK.ru.md) |

---

## Индекс файлов планов

### В `evidence/` (канон review)

- [SOFTCOLD_FIX_THEN_RETEST.plan.md](SOFTCOLD_FIX_THEN_RETEST.plan.md)
- [RETEST_EXTENDED_TIME.plan.md](RETEST_EXTENDED_TIME.plan.md)
- [AMPNORM_EOL_INVESTIGATE.plan.md](AMPNORM_EOL_INVESTIGATE.plan.md)
- [AMPNORM_EOL_FIX.plan.md](AMPNORM_EOL_FIX.plan.md)
- [P4_br25_plan.md](P4_br25_plan.md)

### В корне review

- [COLD_AUDIT_FIXES.plan.md](../COLD_AUDIT_FIXES.plan.md)
- [PLAN.ru.md](../PLAN.ru.md)

### Копии Cursor → `evidence/plans/`

| Файл | Тема |
|------|------|
| [softcold_full_49_…](plans/softcold_full_49_d40e240c.plan.md) | Full49 HEAD |
| [softcold_parallel_rematrix_…](plans/softcold_parallel_rematrix_eb3445a3.plan.md) | Rematrix 49×6 |
| [ampnorm_eol_fixes_…](plans/ampnorm_eol_fixes_3c7a888d.plan.md) | AmpNorm W0–W4 |
| [d_rmax_length_escape_…](plans/d_rmax_length_escape_1d50f760.plan.md) | D length escape |
| [w3c_…](plans/w3c_apply___stall_abort_01bf86de.plan.md) / [w3d_…](plans/w3d_multi-dend_escape_5e464db7.plan.md) / [w3e_…](plans/w3e_rmax_undershoot_1f9923bc.plan.md) | D волны |
| [open_gaps_…](plans/open_gaps_research_c6687d74.plan.md) / [d_residual_…](plans/d_residual_investigate_b4fa4944.plan.md) | Gaps / residual |
| [пороги_осцилляция_…](plans/пороги_осцилляция_need_52604238.plan.md) | Anti-bounce пороги |
| [cold_follow-up_…](plans/cold_follow-up_remediations_efe00c4b.plan.md) | W0–W6 |
| [registry_protocol_…](plans/registry_protocol_clarity_541cfa97.plan.md) | Working vs SoftCold |
| [cold_audit_fixes_…](plans/cold_audit_fixes_e6d3a0e9.plan.md) | Исходный cold audit |

### Уточнение после выборочной проверки Rs/Rm (2026-10-08)

`ResistanceMin` переведён из абсолютного параметра в вычисляемое состояние по нижнему отношению `Rs/Rm`. Обоснование по эффективному диапазону рисунка 2 статьи Бахшиева и Романова, формулы для общей пары границ и влияние на старые XML: [RSRM_MIN_RATIO_FOLLOWUP_2026-10-08.ru.md](RSRM_MIN_RATIO_FOLLOWUP_2026-10-08.ru.md). Исторические результаты выше относятся к прежнему абсолютному нижнему пределу и не являются повторной проверкой новой политики.
