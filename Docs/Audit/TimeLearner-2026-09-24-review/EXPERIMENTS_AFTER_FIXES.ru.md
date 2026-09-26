# Результаты cold-экспериментов после исправлений измерения и приёмки

Дата сводки: 2026-09-25.  
Сборка Console (SHA-256): `4917a2bcbac318d160ca8b596452d3986ccc9978172d35a1b554d65b5a27c843` (ранее в срезе cold V1–V6 фигурировал `5e7829bf…`).  
PulseLib: `8d429e7`. Bin: `1a664a2`.

Этот документ — **единая человекочитаемая сводка** постановок и фактических результатов после исправления контура измерения/приёмки PostTune. Здесь нет исторических ярлыков вроде «V1…V6» и нет внутренних кодов хвостов аудита как основного языка.

Связанные машинные артефакты: каталог [`evidence/tails/`](evidence/tails/), bundles в `Bin/Configs/SpikeSamples/StructTrain/_repro/runs/`, контракт приёмки [`POST_TRAIN_VERIFY.ru.md`](../../../Bin/Configs/SpikeSamples/StructTrain/POST_TRAIN_VERIFY.ru.md).

**Табличный срез текущего состояния алгоритмов** (ось — алгоритм + параметры; cold/PostTune — протокол того же канона, не отдельная семья): [`EXPERIMENTS.md`](../../../Bin/Configs/SpikeSamples/StructTrain/EXPERIMENTS.md) и [`SUCCESSFUL_EXPERIMENTS.md`](../../../Bin/Configs/SpikeSamples/StructTrain/SUCCESSFUL_EXPERIMENTS.md) (только HEAD PASS). Этот файл — narrative доработок измерения и постановок прогонов.

---

## 1. Как читать результат

Каждый опыт — **холодный** прогон (или явный контроль на gold-весах):

1. Чистый рабочий каталог (не грязный archive EXP).
2. Обучение Train до остановки / флага PostTune (если включён).
3. Калибровка порога и проверка избирательности на Test (матрица из 8 паттернов: 1 цель + 7 фольг).
4. Строгая приёмка: обучение должно завершиться с `IsNeedToTrain=0`; порог mid с источником «из текущего C++ inference»; маска выстрелов должна совпасть с ожиданием; TipR — с ожидаемым классом режима.

**Маска выстрелов** — 8 бит в порядке паттернов матрицы. Пример: `10000000` = цель стрельнула, все семь фольг молчат (идеальная избирательность в этом протоколе).  
**Ложные на фольгах** = число единиц среди битов 2…8.  
**NonSeparable** = PostTune зафиксировал, что целевой пик не отделяется от фольг (`landscape_ok=0`, Result=2); рабочий mid при этом обычно остаётся «тихим» (=1), а не Success-калибровкой.

Пороги `LandscapeOk` **не ослаблялись**.

---

## 2. Что изменилось относительно заявлений «до исправлений»

До повторного аудита и remediation разработчик опирался на сводку вида «2 из 7 cold PASS» (Asym 50 ms и Branch 100 ms Search) и на более раннюю таблицу, где почти все клоны были отмечены PASS. Полных свежих run-bundles с provenance тогда в checkout не было; повторный аудит эти PASS **не принял** как независимую приёмку.

После исправлений измерения (analyzer/PostTune) и harness (чистый workdir, запрет Need≠0, синхронизация TipR из текущего Train-флага, хэш TipR в provenance):

| Было в заявлениях / рисках | Стало в свежих прогонах |
|---|---|
| Можно «получить» mid из старого Test-флага archive | На Asym 50 ms mid Test = `0.0100962`, не archive `0.0116458` |
| Timeout / NaN / старый Success могли дать «хороший» mid | Probes: mid уходит в silent; Result не Success |
| TipR в XML = flat при canon во флаге (гонка Save) | После sync из текущего флага TipR=canon, Need=0; FAIL остаётся из‑за landscape/gate |
| Asym 50 ms и Search — PASS | Оба **не проходят строгую приёмку** (см. ниже) |
| «Почти все клоны PASS» | Холодная матрица 6 клонов: **0 PASS** |

Итог: контур стал **строже и честнее**; число cold PASS **не выросло** — заявленные раньше PASS в строгом протоколе не подтверждаются.

---

## 3. Сводная таблица актуальных прогонов

| Опыт | Ожидание (кратко) | Приёмка | Выстрелы | Ложных на фольгах | Цель попала | Главная причина FAIL / примечание |
|---|---|---|---|---|---|---|
| Branch 25 ms, **готовые gold-веса** (без обучения) | canon TipR, mid≈0.0718, маска `10000000` | **PASS** | `10000000` | 0 | да | Контроль измерительного контура |
| Branch 25 ms, **soft-cold обучение** + Canon TipR | то же после обучения | **FAIL** | нет полного CSV | — | — | NonSeparable: foils ≥ target; mid=1 |
| Branch 25 ms, soft-cold, режим **Keep** TipR | сравнить с Canon | **FAIL** | нет | — | — | Тоже NonSeparable → не «виноват только Canon» |
| Branch 25 ms soft vs **полная очистка** модели | отличить неполный soft-reset | оба FAIL, **без различия** | нет | — | — | Soft и strip дают те же metrics/Result |
| Branch 25 ms AutoScale gap 0 vs 1 | отличить остаточную активность | оба FAIL, **без различия** | нет | — | — | Delay/mid/TipR совпали |
| Branch 25 ms, PostTune **выключен** | legacy TipR-путь, gate | **FAIL** | `10110000` | **2** | да | 2 ложных на фольгах; mid≈0.109 ≠ gold 0.072 |
| AsymRm 25 ms, Flat TipR | flat TipR, избирательность | **FAIL** | нет | — | — | NonSeparable (result=2) |
| AsymRm 50 ms, Canon TipR | Need=0, mid cpp, `10000000` | **FAIL** | `10000000` | 0 | да | Обучение не закрыло Need=1; mid Test свежий |
| Branch 100 ms, **Keep** TipR | сохранить snapshot TipR | **FAIL** | нет | — | — | NonSeparable; tipr≈snapshot но landscape плохой |
| Branch 100 ms, **Search** TipR | поиск / откат к snapshot; `10000000` | **FAIL** | `00000000` | 0 | **нет** | Откат к snapshot сработал; цель молчит |
| Phase6 span 480 ms | harness допускает маску `10000010`; строго — `10000000` | **FAIL** | нет полного CSV | — | — | Need не закрыт; Test mid=1 NonSeparable |

**Счётчик строгой cold-матрицы 6 клонов (без gold-контроля): 0 PASS / 6 FAIL.**  
**Gold-контроль Branch 25 ms: 1 PASS.**

---

## 4. Постановки и результаты по опытам

### 4.1. Branch 25 ms — контроль на уже обученных (gold) весах

**Постановка.** Клон `EXP_br_span25_packA_gen_C1e9_posttune`, веса/порог как у validated gold `EXP_br_span25_packA_gen_C1e9`. Обучение Train **не** запускается; только Test-калибровка и gate на матрице pack A, span 25 ms. Ожидание: TipR вида «канон» (`2e7 2e7 2e7 8.6e7`), mid ≈ `0.0718`, выстрелы `10000000`.

**Результат.** PASS.  
Bundle: `_repro/runs/br25_on_20260924T165949Z`.  
Выстрелы `10000000` (0 ложных), совпадения `11111111`, mid Test `0.0718001`, источник mid = cpp.

**Вывод.** После исправлений измерительный контур на известных хороших весах работает.

---

### 4.2. Branch 25 ms — soft-cold обучение, режим Canon TipR

**Постановка.** Тот же posttune-клон. Перед Train — soft-cold сброс (Need=1, TipR «холодный» flat и т.п.). PostTune включён, режим TipR = CanonRmin. Лимит Train ≈ 320 с модели. Затем Test gate. Ожидание то же, что у gold.

**Результат.** FAIL.  
Bundle: `_repro/runs/br25_on_20260924T170503Z` (и повторные прогоны с sync флага).  
Train-флаг: `result=2` (NonSeparable), `landscape_ok=0`, mid=1,  
metrics (target, 7 foils) ≈  
`0.1025, 0.1033, 0.1033, 0.1034, 0.0787, 0.0791, 0.1016, 0.1035`  
— целевой пик **не выше** фольг (несколько фольг больше target).  
Полного успешного CSV gate в этом прогоне нет (gate rc≠0).

**Ранняя путаница (исправлена отдельным прогоном).** Сразу после обучения XML мог остаться с TipR=flat и Need=1, хотя во флаге уже tipr=canon — гонка Save Console. После синхронизации **текущего** Train-флага в Parameters: TipR=canon, Need=0; FAIL остаётся из‑за NonSeparable/gate, а не из‑за «flat в XML».

**Вывод.** Обучение не строит отделимый landscape на soft-cold длинах L≈`1 1 1 1`.

---

### 4.3. Branch 25 ms — soft-cold, режим Keep TipR (тот же L)

**Постановка.** Как 4.2, но режим TipR = KeepDone (не переписывать в канон). Цель — проверить гипотезу «ломает только Canon».

**Результат.** FAIL, тоже NonSeparable (`result=2`, `landscape_ok=0`).  
Evidence: `evidence/tails/T3_H1_canon_vs_keep.json`.

**Вывод.** Canon не единственная причина.

---

### 4.4. Branch 25 ms — soft-cold против полной очистки структуры модели

**Постановка.** Два независимых workdir с одного archive: (а) soft-cold; (б) strip/full init. Одинаковые PostTune-теги (Canon). Сравнить TipR, L, metrics, Result, выстрелы.

**Результат.** Материальных отличий нет: оба NonSeparable, одинаковые train-metrics и TipR canon после sync.  
Evidence: `evidence/tails/T3_H3_soft_vs_strip.json`.

**Вывод.** Неполный soft-reset **не** объясняет FAIL относительно полной очистки в этом протоколе.

---

### 4.5. Branch 25 ms — AutoScaleIterationGap = 1 против 0

**Постановка.** Soft-cold + Canon; два workdir с разным `AutoScaleIterationGap`. Смотреть Delay, mid, TipR, выстрелы.

**Результат.** Отличий по Delay/mid/TipR/Need/выстрелам нет (оба FAIL gate). XML Delay = `1.5` в обоих.  
Evidence: `evidence/tails/T3_H4_autoscale.json`.

**Вывод.** Гипотеза «остаточная активность из‑за AutoScale gap» здесь не подтвердилась.

---

### 4.6. Branch 25 ms — PostTune выключен

**Постановка.** Клон `…_posttune_off`. Soft-cold, `EnablePostTrainTuning=0`, Train ≈ 320 с, затем gate. Ожидание: «legacy» класс TipR допустим; избирательность как у протокола.

**Результат.** Строгая приёмка FAIL.  
Bundle: `_repro/runs/br25_off_20260924T204259Z`.  
Выстрелы `10110000`: цель да, **2 ложных** на фольгах (паттерны 3 и 4).  
Need Train/Test = 0. mid ≈ `0.108833` (далековато от gold `0.0718`). TipR в XML канонического вида, класс в приёмке — `other`/`legacy`-ожидание.

**Вывод.** Без PostTune обучение завершается, но избирательность хуже эталона (2 FA).

---

### 4.7. AsymRm 25 ms — Flat TipR

**Постановка.** `EXP_span25ms_packA_gen_posttune`, режим FlatLastR, Train ≈ 160 с, gate Asym. Ожидание: TipR все `8.6e7`, избирательность.

**Результат.** FAIL.  
Bundle: `_repro/runs/asym25_20260924T214120Z`.  
Флаг: NonSeparable, mid=1, tipr flat `8.6e7×4`,  
metrics ≈ `0.00793…` с foils того же порядка / выше. CSV gate не получен.

**Вывод.** Landscape не строится; до исправлений этот клон часто числился PASS в старых таблицах — сейчас нет.

---

### 4.8. AsymRm 50 ms — Canon TipR

**Постановка.** `EXP_span50ms_packA_gen_posttune`, Canon, Train лимит увеличен до **640** с модели (при 320 с Finalize часто не успевал: не было Train-флага). Ожидание: Need=0, mid из cpp, выстрелы `10000000`, mid ≠ stale archive `0.0116458`.

**Результат.** FAIL приёмки (Need).  
Bundle: `_repro/runs/asym50_20260924T214908Z`.  
Train: Need=**1**, mid=**1**, TipR уже canon, **Train posttune_complete.flag отсутствует** (Finalize не зафиксирован).  
Test: Need=0, mid=**`0.0100962`** (cpp), TipR canon, выстрелы **`10000000`** (0 ложных), matches `11111111`. Gate сам по себе успешен.

**Вывод.** Избирательность на Test есть и mid свежий (изоляция stale подтверждена), но обучение **не закрыло** Need — строгая приёмка справедливо FAIL. Старый «PASS Asym50» при таком протоколе не воспроизводится.

---

### 4.9. Branch 100 ms — Keep TipR

**Постановка.** `…_posttune_keep`, режим KeepDone, Train ≈ 640 с. Ожидание: TipR совпадает с собственным snapshot, mid cpp, `10000000`.

**Результат.** FAIL.  
Bundle: `_repro/runs/br100_keep_20260924T234016Z`.  
Флаг: NonSeparable, tipr ≈ snapshot (`same` / same_FAIL для приёмки keep), mid=1, landscape_ok=0. CSV нет.

**Вывод.** Keep сохраняет веса, но landscape отрицательный — не Success-калибровка.

---

### 4.10. Branch 100 ms — Search TipR

**Постановка.** `…_posttune_search`, режим SearchSynthetic (полный Train с поиском), Train до ~2400 с. Ожидание: либо улучшение TipR относительно **своего** snapshot (`applied_best`), либо честный откат (`same_reverted`); mid cpp; выстрелы строго `10000000`.

**Результат.** FAIL по выстрелам.  
Bundle: `_repro/runs/br100_search_20260925T015547Z`.  
Статус: `done_search_reverted`, tipr_vs_snapshot=`same_reverted` (откат сработал).  
mid Test ≈ `0.002137` (cpp).  
Выстрелы **`00000000`**: цель **не** стрельнула, фольги тихие (0 FA, но 0 попаданий в цель). matches `01111111`.

**Вывод.** Механика отката поиска жива; качество после отката — молчание цели, не эталонная избирательность. Старый «PASS Search» не подтверждён.

---

### 4.11. Phase6 — span 480 ms

**Постановка.** `Phase6/EXP_480_gen_posttune`, Canon, Train ≈ 900 с. В harness для regression допускается маска `10000010` (одна ложная на фольге); отдельно смотрят строгую `10000000`.

**Результат.** FAIL.  
Bundle: `_repro/runs/phase6_480_20260924T234719Z`.  
Train Need=1, mid=1; TipR экстремальный вид `1e11×3 + 8.6e7`.  
Test flag: NonSeparable, mid=1, metrics с foils, сопоставимыми с target. Полного CSV в малом bundle нет.

**Вывод.** Ни harness-допуск `10000010`, ни строгая маска не оформлены как PASS на этом свежем прогоне.

---

## 5. Сводка «ошибок» в терминах протокола

| Метрика по свежим cold / контролям | Значение |
|---|---|
| Успешных строгих cold-клонов из 6 | **0** |
| Успешный gold-контроль Branch 25 ms | **1** |
| Случаев явной маски с ложными на фольгах | Branch 25 ms off: **2 FA** (`10110000`) |
| Случаев идеальной маски `10000000`, но FAIL по другой причине | Asym 50 ms (Need=1) |
| Случаев полной тишины цели | Search 100 ms (`00000000`) |
| Случаев NonSeparable (result=2) на soft-cold Branch/Asym/Keep/Phase6 | устойчиво воспроизводится |
| Отличие soft vs strip / AutoScale 0 vs 1 | **не найдено** |

---

## 6. Практический вывод

1. **Измерение и приёмка** после исправлений согласованы с аудитом: stale mid не протекают, плохой landscape не маскируется Success mid, Need≠0 не считается PASS.  
2. **Модельные cold-результаты** на семи рабочих posttune-клонах в строгом протоколе **не зелёные**; единственный стабильный PASS в этой серии — контроль на уже известных gold-весах Branch 25 ms.  
3. Локализация soft-cold FAIL Branch 25 ms: отрицательный landscape на L≈1, не Save-lag TipR (после sync), не отличие soft/strip, не AutoScale gap в проверенном диапазоне.  
4. Исторические заявления «почти всё PASS / 2 из 7 PASS» следует читать как **неподтверждённые** этим комплектом свежих bundles.

---

## 7. Указатели на сырые данные

Табличный реестр тех же прогонов **внутри канонических алгоритмов** (не отдельная секция «PostTune»): [`EXPERIMENTS.md`](../../../Bin/Configs/SpikeSamples/StructTrain/EXPERIMENTS.md) §1.1 / §1.3 / §3.1–3.2 / §5.1 · только PASS: [`SUCCESSFUL_EXPERIMENTS.md`](../../../Bin/Configs/SpikeSamples/StructTrain/SUCCESSFUL_EXPERIMENTS.md).

| Опыт | Каталог bundle (малые артефакты) |
|---|---|
| Gold Branch 25 ms | `_repro/runs/br25_on_20260924T165949Z/` |
| Soft-cold Branch 25 ms | `_repro/runs/br25_on_20260924T170503Z/` |
| PostTune off Branch 25 ms | `_repro/runs/br25_off_20260924T204259Z/` |
| AsymRm 25 ms | `_repro/runs/asym25_20260924T214120Z/` |
| AsymRm 50 ms | `_repro/runs/asym50_20260924T214908Z/` |
| Keep 100 ms | `_repro/runs/br100_keep_20260924T234016Z/` |
| Search 100 ms | `_repro/runs/br100_search_20260925T015547Z/` |
| Phase6 480 ms | `_repro/runs/phase6_480_20260924T234719Z/` |
| Soft vs strip / AutoScale | `evidence/tails/T3_H3_soft_vs_strip.json`, `T3_H4_autoscale.json` |
| Машинная матрица 6 клонов | `evidence/tails/D4_matrix_summary.json` |

---

## 8. Retest NOT_RETESTED (2026-09-25/26)

**Console SHA-256:** `4917a2bcbac318d160ca8b596452d3986ccc9978172d35a1b554d65b5a27c843` · PulseLib `8d429e7` · Bin `1a664a2` (accidental rebuild поверх прежнего `5e7829bf…`).

### GoldTest (волна G)

- Инструмент: `scripts/gold_retest_batch.py` (манифест `_repro/NOT_RETESTED_manifest_20260925.txt`, span-aware `-t`, SIGTERM после CSV n≥8).
- Итог: `_repro/GOLD_RETEST_MERGED_20260925.csv` — **101 PASS / 1 FAIL** из 102 прогнанных (OUT×4 не гонялись).
- Единственный GoldTest **FAIL:** `Phase6/EXP_480_ltzcal_twin_gen` (Acc 2/8, fires `11110111`).
- Реестр: [`EXPERIMENTS.md`](../../../Bin/Configs/SpikeSamples/StructTrain/EXPERIMENTS.md) / [`SUCCESSFUL_EXPERIMENTS.md`](../../../Bin/Configs/SpikeSamples/StructTrain/SUCCESSFUL_EXPERIMENTS.md); gate: `AUDIT_GATE_RECOMPUTE.csv`.

### SoftCold (волна C)

- Расширены `CASES` в `posttune_verify.py`; batch: `scripts/softcold_c_batch.sh`; allowlist +`Interface.xml`.
- C1: **14/22** завершены на HEAD — все **FAIL** (`_repro/SOFTCOLD_C_rcs.txt`); batch остановлен 2026-09-26 (Need→stuck / wall-clock). Секция «SoftCold wave C (auto)» в EXPERIMENTS.
- Остаток C1 (Phase6×3, FastSpan×5) + C2 (Ltz/PhaseA/PSI): **DEFER** с таблицей в EXPERIMENTS.
