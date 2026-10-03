# SoftCold full matrix — аудит сходимости обучения

**Срез:** 2026-10-03T10:35+03 · матрица **не завершена** (46/49 закрыто).  
**RC:** [`SOFTCOLD_HEAD_rcs.txt`](../../../Bin/Configs/SpikeSamples/StructTrain/_repro/SOFTCOLD_HEAD_rcs.txt) · лог [`metrics/SOFTCOLD_full_matrix.log`](metrics/SOFTCOLD_full_matrix.log) · live [`metrics/softcold_last_sample.json`](metrics/softcold_last_sample.json).  
**Console/PulseLib HEAD матрицы:** AmpNorm a/b + midband→Rmin escape · harness `--autosave-model-s 10`.

**Назначение:** систематизировать закрытые SoftCold FAIL с фокусом на **сходимость Train** (Need / TipR / EOL), разделить **C++ алгоритм**, **harness/скрипты** и **объективные** пределы. После 49/49 — обновить §1, §4, §8.

Связанные разборы: [AMPNORM_EOL_STUCK.ru.md](AMPNORM_EOL_STUCK.ru.md) · [SOFTCOLD_FAIL_BOUNDS.ru.md](SOFTCOLD_FAIL_BOUNDS.ru.md) · [FAIL_ROOTCAUSE.ru.md](FAIL_ROOTCAUSE.ru.md) (старый eps-fixed срез) · [A_NONSEPARABLE_MID.ru.md](A_NONSEPARABLE_MID.ru.md) · [PHASE6_ESTDELAY_FIX.ru.md](PHASE6_ESTDELAY_FIX.ru.md).

---

## 1. Сводка матрицы (живой счётчик)

| | |
|--|--|
| Закрыто | **46 / 49** |
| PASS / FAIL | **8 / 38** |
| Сейчас | `phase6_preinh250` (47/49) · TipR `1e11×3 / 8.6e7` · Need=1 · L=`53 45 28 1` · `-t 900` |
| Хвост очереди | `tn_classic`, `phase6_480` |

**PASS (cold Train сошёлся + gate):**  
`asym50_preinh`, `asym25_preinh`, `asym50`, `br50_gen`, `br100_preinh`, `br25_nextseg`, `br50_preinh`, `ltz50_gen`.

**Интерпретация:** soft-cold desync (TipR flat + L=`1 1 1 1` на всём budget) на HEAD **снят** для большинства канонов. Доминируют уже **реальные** провалы AmpNorm/TipR/EOL и селективности.

---

## 2. Таксономия FAIL (сходимость)

Класс по **последнему осмысленному autosave/SNAP перед GATE**: Need, форма TipR (dend0..2), `gate rc`.  
(В логе TipR иногда с запятой как десятичный разделитель — парсер должен нормализовать.)

| ID | Корзина | Критерий | # | Слой |
|----|---------|----------|---|------|
| **D** | TipR runaway / ceiling | ≥1 dend → `≥1e9` или `1e11`; Need=1 | **~20** | **C++** R-control |
| **E** | TipR@Rmin, Need=1 | dend TipR≈`2e7` (или близко), EOL не закрывает Need | **~9** | **C++** AmpNorm(b)/EOL |
| **B** | mid-band TipR, Need=1 | dend2 (часто) ~2.5e7…7e7; gate иногда 0 | **~6** | **C++** AmpNorm(a) |
| **A** | TipR flat LastR | `8.6e7×4`, R-tune не стартовал | **3** | смесь протокол / cold path |
| **C** | Need=0, metrics/fires | Train «закрыт», Acc/fires плохие | **1+** | часто **объективно** / протокол |
| **N** | NonSeparable mid | LandscapeOk=0 при TipR@Rmin | **1** (`br25_on`) | **объективно** (+E) |

### 2.1 По семействам

| Семейство | Паттерн | Заметка |
|-----------|---------|---------|
| PhaseA / PSI | **D** ceiling `1e11`, L часто `97 81 49` | EstDelay/length + R упирается в Rmax |
| Phase6 | **D** частичный ceiling (dend0/1=`1e11`, dend2 mid) | L≈gold (`49 41 25`); thr_only / ltzcal_twin / preinh250 |
| FastSpan | **B** mid dend2 (fs25*) + **E** @Rmin (fs50/100) | классика AmpNorm (a)/(b) |
| AsymRm / LtzCal gen | **E** @Rmin Need=1 на 100/25; **PASS** на 50 | тот же EOL-stuck при канон TipR |
| LtzCal / Asym *preinh* | **D** runaway (ltz25/50/100_preinh) | preinh хуже удерживает TipR |
| Branch | смесь A/B/C/D/E/N | keep/search/nextseg/off — не чистый AmpNorm |

---

## 3. Первопричины по слоям

### 3.1 C++ алгоритм (`NNeuronTimeLearner.cpp`) — главный слой

EOL: `EndOfLearning` ⇔ `AllDendritesSynced() && AllSynapsesNormalized()`  
(см. ~3671–3679). SoftCold PASS требует Need→0; иначе `posttune_verify` → `train_incomplete`.

#### (a) Mid-band TipR / skip `|dt|>5` — корзина **B**

Код: `ChangeSynapseResistanceStatus`, ветка `fabs(dt) > 5.0` (~778–810) + midband→Rmin (~824–841, ~891–908).

| Что делает код | Симптом матрицы |
|----------------|-----------------|
| При \|ampDt\|>5 **не** обновляет TipR несколько хитов; escape к Rmin после `kNoImproveResistanceLimit` | fs25_gen/preinh: dend2 осциллирует ~2.6–4.1e7, Need=1, **gate rc=0** |
| midband_walk / NoImprove→Rmin | не всегда успевает за `-t`; br25_preinh dend2 **замёрз** на `6.76e7` |
| ResistanceStatus=0 без Done | mid freeze при Status=0 |

**Вердикт:** несовершенство **реализации R-control / AmpNorm(a)**. Harness честно режет по Need. Якорь диагностики: [AMPNORM_EOL_STUCK.ru.md](AMPNORM_EOL_STUCK.ru.md) (fs25 keep-slog).

#### (b) TipR@Rmin, но Need=1 — корзина **E**

Код: `AllSynapsesNormalized` parametric (~3567–3640): Done при  
`amp_ok` **или** `at_r_min && dt_positive && length_ok` **или** dead_tip / oscillation / no_improve_done.  
AmpNorm(b): slack `tol * kRminLengthTolFactor` для length при Rmin (~3586–3589).

| Симптом | Кейсы |
|---------|-------|
| TipR=`2e7×3 / 8.6e7`, L растёт, Need=1 до конца `-t` | asym100_*, ltz100_gen, ltz25_gen, fs50_preinh, fs100_*, br25_on |

**Вердикт:** дефект/дыра **EOL-гейтов** (length_ok / dt_positive / ResistanceStatus / PeakSeen). W2 AmpNorm(b) **не** дал Cold PASS на этих якорях. Контраст: asym50 / ltz50_gen — **PASS** при том же каноне TipR.

#### (c) TipR → ceiling / runaway — корзина **D**

damped-P + clamp к ResistanceMax (`1e11`) при патологическом ampDt / нестабильном L.

| Симптом | Кейсы |
|---------|-------|
| `1e11×3` | почти все pa*/psi* |
| `1e11×2` + dend2 mid ~2.2–2.5e7 | phase6_thr_only, phase6_ltzcal_twin, **phase6_preinh250 (live)** |
| runaway ≥1e9…2e10 без единого ceiling | ltz100_preinh, ltz50_preinh, ltz25_preinh, br480_preinh, часть psi |

**Вердикт:** **реализация R-control** не удерживает бассейн притяжения; на PhaseA дополнительно L=`97…` (EstDelay/length трек, см. Phase6 fix — на PSI/PhaseA ещё проявляется). Часть preinh-конфигов может быть **вне рабочего бассейна** (объективный предел конфига), но механизм ухода — кодовый.

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

---

## 4. Карта кейсов (закрытые FAIL, срез 46)

### 4.1 D — runaway / ceiling (~20)

`pa00_baseline`, `pa01_ltz_sweep`, `pa02_ltzone_avg`, `pa06_ltzone_int`,  
`psi01_050`, `psi14_260`, `psi15_270`, `psi21_100`, `psi31_200`, `psi32_300`, `psi33_300`, `psi34_400`, `psi35_400`,  
`phase6_thr_only`, `phase6_ltzcal_twin`,  
`br480_preinh`,  
`ltz100_preinh`, `ltz50_preinh`, `ltz25_preinh`.

Live → ожидаемо в D: `phase6_preinh250`.

### 4.2 E — TipR@Rmin Need=1 (~9)

`br25_on` (+ **N** NonSeparable), `fs50_preinh`, `fs100_gen`, `fs100_preinh`,  
`asym100_gen`, `asym100_preinh`, `ltz100_gen`, `ltz25_gen`,  
`br100_search` (TipR≈`4e7`, не канон Rmin, но «села» полоса без EOL).

### 4.3 B — mid-band Need=1 (~6)

| case | TipR (конец) | gate | Комментарий |
|------|--------------|------|-------------|
| `fs25_gen` | `2e7 2e7 ~2.6e7` | 0 | AmpNorm(a); Acc OK |
| `fs25_preinh` | `2e7 2e7 ~4.0e7` | 0 | то же |
| `br25_preinh` | `2e7 2e7 **6.76e7** freeze** | 0 | mid freeze |
| `br480_nextseg` | `8.6e7 2e7 2e7` | 1 | частичный mid |
| `br480_tiprmin` | `8.6e7 2e7 2e7` | 1 | частичный mid |
| `br100_keep` | `2e7 2e7 ~3.5e7`, **Need→0** | 1 | EOL «закрылся» без canon TipR |

### 4.4 A — flat LastR (3)

`asym25`, `br50_nextseg`, `br100_nextseg`.

### 4.5 C — metrics после Need=0 (1+)

`br25_off` — SoftColdOff, Need=0, gate=0, verify rc=1 (fires/Acc).

---

## 5. Разделение «чинить / не чинить»

| Приоритет | Что | Где | Зачем |
|-----------|-----|-----|-------|
| P0 | AmpNorm(b): TipR@Rmin → EOL | C++ `AllSynapsesNormalized` / sync length | разблокирует E (asym100, ltz*, fs50/100) |
| P0 | AmpNorm(a): mid-band → Rmin за бюджет | C++ ветка `|dt|>5` / escape | разблокирует B (fs25*, br25_preinh) |
| P1 | TipR ceiling/runaway на PhaseA/PSI/Phase6 | C++ R-update + EstDelay/L | корзина D |
| P2 | Диагностика: `--keep-slog`, нормализация TipR в логе | harness | не меняет rc, ускоряет разбор |
| — | LandscapeOk / Acc / fires пороги | gate scripts | **не ослаблять** ради зелёного SoftCold |
| — | Matcher реестра | `apply_softcold_rcs_*` | только LastCheck; уже чинится отдельно |

---

## 6. Что уже *не* является первопричиной на этом HEAD

1. Soft-cold tip-1 desync (исторический `B_tipr_frozen_cold` в FAIL_TAXONOMY) — для PASS-кейсов и большинства FAIL TipR/L **двигаются**.  
2. Ложный FAIL из‑за «gate убил Acc при живом Train» на B-кейсах: gate часто **зелёный**, режет именно Need/tipr_class.  
3. Отсутствие autosave: mtime TipR/Need обновляются (`softcold_last_sample.json`).

---

## 7. Однострочный вердикт

> Из 38 FAIL на срезе 46/49 большинство — **несходимость AmpNorm/TipR/EOL в PulseLib** (D/E/B). Скрипты анализа **честно** фиксируют Need≠0 / tipr≠canon. Меньшинство — **объективная** неразделимость (`br25_on`), Off/Keep/Search/nextseg протоколы.

---

## 8. Чеклист обновления после 49/49

- [ ] Пересчитать §1 из финального `SOFTCOLD_HEAD_rcs.txt`
- [ ] Добавить `phase6_preinh250`, `tn_classic`, `phase6_480` в §4
- [ ] Если новые PASS — вынести общий паттерн (TipR@Rmin + Need=0 + gate) в §2
- [ ] Перегнать классификатор по логу (нормализация `,`→`.` в TipR)
- [ ] Синхронизировать краткий вердикт в [SOFTCOLD_FAIL_BOUNDS.ru.md](SOFTCOLD_FAIL_BOUNDS.ru.md) / STATUS
- [ ] При P0-фиксе — отдельный retest-якорь: `fs25_gen`, `asym100_gen`, `ltz50_gen` (keep PASS)
