# SoftCold full matrix — аудит сходимости обучения

**Срез (актуальный):** SoftCold rematrix PARALLEL **49×6** · **DONE** 2026-10-05T09:17Z→2026-10-05T22:12Z (apply 2026-10-06T05:15Z).  
**RC:** [`SOFTCOLD_HEAD_rcs.txt`](../../../Bin/Configs/SpikeSamples/StructTrain/_repro/SOFTCOLD_HEAD_rcs.txt) · log `metrics/SOFTCOLD_full_matrix_parallel.log`.  
**Console SHA16:** `8589daff6d131c9b` · **PulseLib:** `b32d715` (RmaxDwell escape только при dt≥0) · harness `--autosave-model-s 10` · `PARALLEL=6`.

Предыдущий срез 2026-10-03 (8/41) и partial W4 — архив; PASS W4 **не** входят в финал.

**Назначение:** систематизировать SoftCold FAIL с фокусом на **сходимость Train** (Need / TipR / EOL).

Связанные разборы: [AMPNORM_EOL_RETEST_RESULT.md](AMPNORM_EOL_RETEST_RESULT.md) · [PHASEA_PSI_ESTDELAY_FIX.ru.md](PHASEA_PSI_ESTDELAY_FIX.ru.md) · [AMPNORM_FLAT_TIPR_ASYM25.ru.md](AMPNORM_FLAT_TIPR_ASYM25.ru.md) · [AMPNORM_EOL_FIX.plan.md](AMPNORM_EOL_FIX.plan.md) · [PHASE6_ESTDELAY_FIX.ru.md](PHASE6_ESTDELAY_FIX.ru.md).

---

## 1. Сводка матрицы (rematrix PARALLEL, финал)

| | |
|--|--|
| Закрыто | **49 / 49** |
| PASS / FAIL | **13 / 36** |
| Статус очереди | **DONE** (`phase6_480` последний Train; RCS merge + registry apply) |
| Оркестратор | `scripts/softcold_full_matrix_parallel.sh` (rcs.d shards → merge → apply) |

**PASS (cold Train сошёлся + gate):**  
`asym50_preinh`, `asym25_preinh`, `asym50`, `br25_off`, `fs25_gen`, `br50_gen`, `br100_preinh`, `br25_nextseg`, `br50_preinh`, `fs100_preinh`, `fs25_preinh`, `asym100_preinh`, `ltz50_gen`.

**Дельта vs 2026-10-03 (8 PASS):** +`br25_off` (expect_fires SoftColdOff), +`fs25_gen`/`fs25_preinh`/`fs100_preinh`, +`asym100_preinh`. Keep-якоря (`asym50`, `ltz50_gen`, `br50_gen`, `fs25_gen`) зелёные. EstDelay PhaseA: live L=`49 41 25` на `pa*` (≠`97 81 49`); TipR всё ещё ceiling → корзина **D**.

---

## 2. Таксономия FAIL (сходимость, срез rematrix)

Класс по `tipr_final` / provenance `tipr_class` + `failure_class` последнего run на SHA `8589daff…`.

| ID | Корзина | Критерий | # | Слой |
|----|---------|----------|---|------|
| **D** | TipR ceiling freeze @Rmax | ≥1 dend → `1e11`; Need=1; `amp_dt&lt;0` hold | **20** | **C++** W3c: length-grow DOF ([AMPNORM_D_RMAX_LENGTH_ESCAPE.ru.md](AMPNORM_D_RMAX_LENGTH_ESCAPE.ru.md)) |
| **E_algo** | TipR partial Rmin, **Need=1** | Branch partial (`br480_nextseg`/`tiprmin`) | **2** | Branch EOL (отложено) |
| **E_gate** | TipR@Rmin canon, Train done, gate/Landscape | Need→0; LandscapeOk=0 / silent mid | **6** | **объективно** (`asym100_gen`, `ltz100_gen`, `ltz25_gen`, `fs100_gen`, `br25_preinh`, + overlap C) — **не** AmpNorm EOL |
| **B** | mid-band TipR, Need=1 | mid вне Rmin/Rmax | **1** (`ltz25_preinh`) | R-control / budget |
| **A** | TipR flat LastR | `8.6e7×4` | **3** | протокол (`asym25`, nextseg) |
| **C** | TipR canon + gate_fail | metrics/Landscape | **1** (`fs50_preinh`) | §4 не ослаблять |
| **N** | NonSeparable mid | LandscapeOk=0 @Rmin | **1** (`br25_on`) | объективно |
| **G** | Keep/Search TipRMode | не CanonRmin | **2** | режим/протокол |

**Подсчёт FAIL:** D=20 + E_algo=2 + E_gate≈5–6 + B=1 + A=3 + C=1 + N=1 + G=2 ≈ **36** (+13 PASS). Старая «E=8» смешивала gate/Landscape с Need=1 — для волны D чинить только D (+ EstDelay gaps); E_gate/N/C/A/G вне скоупа.

### 2.1 По семействам (rematrix)

| Семейство | Паттерн | Заметка |
|-----------|---------|---------|
| PhaseA / PSI | **D** ceiling; L≈gold | EstDelay OK; нужны L-grow @Rmax overshoot |
| Phase6 / TimeNeuron | **D** ceiling; `phase6_480`/`tn_classic` ещё L=`97…` | EstDelay gap в `EXP_480_gen_tiprmin` / TimeNeuron |
| FastSpan / AsymRm gen | **E_gate** @Rmin+Landscape (`asym100_gen`, `fs100_gen`, …); `fs50_preinh` **C** | не ослаблять LandscapeOk |
| LtzCal preinh | **D** ceiling/runaway | W3c |
| Branch | A/G/N + E_algo `br480_*` Need=1 | keep/search/nextseg отдельно |

---

## 3. Гипотезы по слоям (не все причины подтверждены)

### 3.1 C++ алгоритм (`NNeuronTimeLearner.cpp`) — главный кандидат

EOL: `EndOfLearning` ⇔ `AllDendritesSynced() && AllSynapsesNormalized()`  
(см. ~3671–3679). SoftCold PASS требует Need→0; иначе `posttune_verify` → `train_incomplete`.

**Ограничение причинного вывода:** `Need=1` и конечные TipR/L не показывают, какой именно гейт удержал EOL. Нужно сохранить оба результата (`AllDendritesSynced`, `AllSynapsesNormalized`), `DendLastAbsDt`, best-effort/length status, amp `dt`, `ResistanceStatus`, NoImprove и фазу PostTune на последнем SNAP. В Branch нормализация идёт в обратном порядке и `AllSynapsesNormalized` рассматривает только `ActivePulseIndex`; базовый разбор нельзя механически переносить на Branch.

#### (a) Mid-band TipR / skip `|dt|>5` — корзина **B**

Код: `ChangeSynapseResistanceStatus`, ветка `fabs(dt) > 5.0` (~778–810) + midband→Rmin (~824–841, ~891–908).

| Что делает код | Симптом матрицы |
|----------------|-----------------|
| Base path при \|ampDt\|>5 пропускает несколько TipR-обновлений, затем делает ограниченный шаг по знаку dt | механизм есть в коде, но `fs25` keep-slog измерил **0** таких hits; это не объясняет fs25 freeze |
| NoImprove сбрасывает ResistanceStatus; midband walk требует \|dt\|≤0.005 | старый fs25 keep-slog наблюдал NoImprove=21, Status=0 и узкий R-oscillation; это объясняет тот срез, но не доказывает точную причину после поздней midband правки |
| Branch не имеет `|dt|>5` skip/midband walk | применимо к Branch B-кейсам, но точный gate/controller state финальных запусков не приложен |

**Вердикт:** fs25 keep-slog подтверждает stall старого среза на счётчике NoImprove/ResistanceStatus, а не на `|dt|>5`. Более поздний HEAD добавил midband walk, но matrix fs25 всё ещё не дошёл до Rmin за бюджет; без текущего полного лога нельзя решить, это остаточный stall, слишком медленный сход за `-t` или другой путь. Не приписывать все B-кейсы одной ветке кода. Harness корректно сохраняет Need≠0. Якорь: [AMPNORM_EOL_STUCK.ru.md](AMPNORM_EOL_STUCK.ru.md) и [AMPNORM_fs25_KEEPSLOG.ru.md](AMPNORM_fs25_KEEPSLOG.ru.md).

#### (b) TipR@Rmin, но Need=1 — корзина **E**

Код: `AllSynapsesNormalized` parametric (~3567–3640): Done при  
`amp_ok` **или** `at_r_min && dt_positive && length_ok` **или** dead_tip / oscillation / no_improve_done.  
AmpNorm(b): slack `tol * kRminLengthTolFactor` для length при Rmin (~3586–3589).

| Симптом | Кейсы |
|---------|-------|
| TipR=`2e7×3 / 8.6e7`, L растёт, Need=1 до конца `-t` | asym100_*, ltz100_gen, ltz25_gen, fs50_preinh, br25_on |

**Вердикт:** кандидат — EOL/sync гейты (length_ok / dt_positive / ResistanceStatus / PeakSeen), но сама комбинация `TipR@Rmin + Need=1` не устанавливает, какой гейт ложен. W2 AmpNorm(b) **не** дал Cold PASS на этих якорях. Контраст: asym50 / ltz50_gen — **PASS** при том же каноне TipR.

#### (c) TipR → ceiling / runaway — корзина **D**

damped-P + clamp к ResistanceMax (`1e11`) при патологическом ampDt / нестабильном L.

| Симптом | Кейсы |
|---------|-------|
| `1e11×3` | почти все pa*/psi* |
| `1e11×2` + dend2 mid ~2.2–2.5e7 | phase6_thr_only, phase6_ltzcal_twin, **phase6_preinh250 (live)** |
| runaway ≥1e9…2e10 без единого ceiling | ltz100_preinh, ltz50_preinh, ltz25_preinh, br480_preinh, часть psi |

**Вердикт:** R-control — основной кодовый кандидат, но конечный высокий TipR не доказывает, что причина только в регуляторе. На PhaseA дополнительно L=`97…` (EstDelay/length трек, см. Phase6 fix — на PSI/PhaseA ещё проявляется). Часть preinh-конфигов может быть **вне рабочего бассейна**; для отделения этого от дефекта регулятора нужны временные ряды amp/dt/TipR/length на том же бинарном срезе.

### 3.2 Harness / скрипты — вторичный слой

| Артефакт | Влияние | Вердикт |
|----------|---------|---------|
| `posttune_verify`: `train_incomplete` / Need=1 | rc=1 | **Корректная фиксация**; не первопричина |
| `tipr_class≠canon` при gate Acc OK | fs25_*, br25_preinh | **Строгий контракт** SoftCold (TipR должен быть канон) |
| `fires_missing` при gate_rc=1 | обнуление fires в `run_gate` | **Вторичный** артефакт анализа (см. FAIL_ROOTCAUSE) |
| early-stop + post-flag grace | режет Train после Need=0 | по дизайну; при Need=1 не маскирует |
| `apply_softcold_rcs_to_registry` WARN name | реестр | **баг маппинга** (Phase6/LtzCal/FastSpan matchers чинились); **не** меняет train rc |
| PRUNE StatisticLog | потеря AmpDt traces | **диагностический** пробел (`--keep-slog`) |

### 3.3 Объективные / протокольные

| Класс | Пример | Почему не «просто баг» |
|-------|--------|------------------------|
| NonSeparable mid | `br25_on` (TipR@Rmin + LandscapeOk=0) | физика ландшафта; **не** ослаблять LandscapeOk |
| SoftColdOff | `br25_off` Need=0, gate=0, verify fires/Acc | протокол без PostTune |
| TipRMode Keep/Search | `br100_keep` (Need→0 при mid TipR), `br100_search` | не CanonRmin cold path |
| nextseg flat | `br50/100_nextseg` L=`1 1 1 1` | протокол сегментации; R-tune не стартует |
| Gold PASS ≠ SoftCold | почти все SUCCESSFUL | Working=GoldTest ≠ cold Train — ожидаемо |
| Длинный span / preinh runaway | ltz*_preinh, psi* | конфиг может быть вне бассейна TipR |

Эти строки показывают возможные объяснения, а не доказанную объективную границу конфигурации; для такого вывода нужны повторяемость/сравнение с управляемым изменением параметров.

---

## 4. Карта кейсов (закрытые FAIL, финал 49)

### 4.1 D — runaway / ceiling (22)

`pa00_baseline`, `pa01_ltz_sweep`, `pa02_ltzone_avg`, `pa06_ltzone_int`,  
`psi01_050`, `psi14_260`, `psi15_270`, `psi21_100`, `psi31_200`, `psi32_300`, `psi33_300`, `psi34_400`, `psi35_400`,  
`phase6_thr_only`, `phase6_ltzcal_twin`, `phase6_preinh250`, `phase6_480`,  
`br480_preinh`,  
`ltz100_preinh`, `ltz50_preinh`, `ltz25_preinh`,
`tn_classic`.

### 4.2 E — TipR@Rmin Need=1 (6)

`br25_on` (+ **N** NonSeparable), `fs50_preinh`,  
`asym100_gen`, `asym100_preinh`, `ltz100_gen`, `ltz25_gen`.

### 4.3 B — mid-band Need=1 (7)

| case | TipR (конец) | gate | Комментарий |
|------|--------------|------|-------------|
| `fs25_gen` | `2e7 2e7 ~2.6e7` | 0 | AmpNorm(a); Acc OK |
| `fs25_preinh` | `2e7 2e7 ~4.0e7` | 0 | то же |
| `br25_preinh` | `2e7 2e7 ~6.76e7` | 0 | mid freeze |
| `fs100_gen` / `fs100_preinh` | mid/нестабильный dend | 1 | рядом с E; TipR не удержал канон |
| `br480_nextseg` | `8.6e7 2e7 2e7` | 1 | частичный mid |
| `br480_tiprmin` | `8.6e7 2e7 2e7` | 1 | частичный mid |

`ltz25_preinh` включён в D по симптому runaway из §2.1; в checkout нет первичного лога, чтобы независимо перепроверить его последний SNAP. `br100_keep` / `br100_search` относятся к отдельной корзине G: это Keep/Search, а не CanonRmin.

### 4.4 G — другой TipR-режим / протокол (2)

`br100_keep`, `br100_search` — KeepDone/SearchSynthetic; не считать эти результаты свидетельством дефекта CanonRmin-маршрута. Для Search отдельно сохранять признак search-revert и результат gate.

### 4.5 A — flat LastR (3)

`asym25`, `br50_nextseg`, `br100_nextseg`.

### 4.6 C — metrics после Need=0 (1)

`br25_off` — SoftColdOff, Need=0, gate=0, verify rc=1 (fires/Acc).

---

## 5. Разделение «чинить / не чинить»

| Приоритет | Что | Где | Зачем |
|-----------|-----|-----|-------|
| P0 | Установить блокирующий EOL-гейт для E/B и точный branch/dendrite state | `AllDendritesSynced`, `AllSynapsesNormalized`, SNAP/StatisticLog | отделить причину от корреляции |
| P1 | Исправлять подтверждённый AmpNorm/R-control stall | base + Branch отдельно | E/B, с сохранением знака dt и проверок Done |
| P1 | Проверить причины TipR ceiling/runaway на PhaseA/PSI/Phase6 | C++ R-update; EstDelay/L отдельно | D; не вводить Rmax escape без dwell evidence |
| P2 | Упаковать `--keep-slog`, autosave и нормализацию TipR в воспроизводимый артефакт | harness/evidence | не меняет rc, позволяет перепроверить классификацию |
| — | LandscapeOk / Acc / fires пороги | gate scripts | **не ослаблять** ради зелёного SoftCold |
| — | Matcher реестра | `apply_softcold_rcs_*` | только LastCheck; уже чинится отдельно |

---

## 6. Что не объясняет FAIL по доступным записям

1. Исторический soft-cold tip-1 desync не объясняет PASS-кейсы и те FAIL, где в записях матрицы есть движение TipR/L. Полного лога, чтобы проверить это утверждение для всех 49 кейсов, в checkout нет.
2. Ложный FAIL из‑за «gate убил Acc при живом Train» не объясняет B-кейсы с `gate_rc=0` в зафиксированных SNAP-заметках: там rc=1 возникает от Need/tipr_class. Без полного лога это нельзя обобщить на все B-кейсы.
3. Отсутствие autosave не подтверждено: записи указывают на autosave, но упомянутый aggregate `softcold_last_sample.json` не сохранён в checkout, поэтому проверка всех mtime независимо не повторяется.

---

## 7. Однострочный вердикт

> Финал **41 FAIL / 8 PASS** подтверждён RCS. Симптомы D=22, E=6, B=7 (35 кейсов) указывают на приоритет проверки PulseLib R-control/EOL, но без полного SNAP/trace не доказывают для всех этих кейсов единую C++-причину. Остальные корзины: A=3, C=1, G=2; `br25_on` — пересекающийся E+NonSeparable, не отдельный дополнительный кейс.

---

## 8. Чеклист обновления после 49/49

- [x] Пересчитать §1 из финального `SOFTCOLD_HEAD_rcs.txt` → **8/41**
- [x] Добавить `phase6_preinh250`, `tn_classic`, `phase6_480` в §4 (все **D**)
- [x] Новых PASS в хвосте нет — список из 8 канонов стабилен
- [x] Классификатор был прогнан во время матрицы (по отчёту автора); полный исходный лог не приложен и независимо не воспроизводится из текущего checkout
- [x] Сверить числа с RCS/manifest: D=22 с `ltz25_preinh`; G=2 (`br100_keep`, `br100_search`); N — overlap
- [ ] Синхронизировать краткий вердикт в [SOFTCOLD_FAIL_BOUNDS.ru.md](SOFTCOLD_FAIL_BOUNDS.ru.md) / STATUS (по желанию)
- [ ] При P0-фиксе — отдельный retest-якорь: `fs25_gen`, `asym100_gen`, `ltz50_gen` (keep PASS)

---

## 9. Независимая проверка аудита (2026-10-03)

### Что подтверждается в текущем checkout

- Корневой HEAD `c0b69ef`; `Bin` HEAD `babdba99`; PulseLib HEAD `b29b595`. Ветка обоих репозиториев — `time_trainer_audit3`. Реестр фиксирует Console SHA-256 `e018c02430d905be`.
- `SOFTCOLD_QUEUE_manifest.txt` и `SOFTCOLD_HEAD_rcs.txt` согласуются по 49 case id; RCS содержит 8 значений `0` и 41 значение `1`.
- PulseLib на этом срезе включает mid-band walk (09d37e2) и Rmin length slack ×2 в base/Branch (bb438c4/b29b595). Матрица проверяла именно этот алгоритм.
- Код `EndOfLearning` требует одновременно синхронизацию длин и нормализацию амплитуд. У base и Branch есть разные детали: в частности, Branch пропускает неактивные импульсы при проверке AmpNorm.

### Что исправлено в классификации

Исходные списки не сходились с 41 FAIL: `ltz25_preinh` назван runaway в семейной таблице и в комментарии к матрице, но отсутствовал в §4.1; корзина G упоминалась, но не была определена и не перечисляла `br100_keep/search`. Для арифметически полной раскладки `ltz25_preinh` отнесён к D, G содержит два неканонических режима, итог D=22 / E=6 / B=7 / A=3 / C=1 / G=2. N по `br25_on` пересекается с E. Классификацию `ltz25_preinh` следует считать предварительной, пока не приложен его первичный SNAP/log.

### Ограничения доказательств и причинности

Файлы `evidence/metrics/SOFTCOLD_full_matrix.log` и `evidence/metrics/softcold_last_sample.json` **не tracked в git** (clone их не получает). На машине прогона они могут оставаться как untracked working-tree артефакты (~0.5 MB log проверен 2026-10-03: `ltz25_preinh` TipR runaway подтверждает отнесение к D). Для причинной атрибуции E/B/D этого журнала недостаточно: в нём нет полей обоих EOL-гейтов / `DendLastAbsDt` / `ResistanceStatus`. Нужен W0 SNAP (см. [AMPNORM_EOL_FIX.plan.md](AMPNORM_EOL_FIX.plan.md)).

Сильные диагностические подтверждения старого среза существуют для `fs25_gen` (keep-slog: NoImprove/ResistanceStatus freeze) и asym* W2 (Rmin, но Need остаётся 1). Они предшествуют финальному matrix HEAD и не заменяют поле-за-полем анализ финального среза. Для причинной атрибуции E/B/D сначала фиксировать оба EOL-гейта и состояние дендритов из списка в §3.1; не выводить одиночный дефект C++ только из конечных TipR, длины и Need.
