# InhGrid SoftCold — диагностика результатов (2026-10-24)

Постановка: после закрытия cold-очереди Classic 48 + Branch 24 N1 (включая disk_stop re-run) нужно было отделить **сходимость Train** от **качества Test** и понять, есть ли хоть один SoftCold PASS по трём торможениям (PSI/preinh, NextSeg \(d=+1\), SegEI \(d=8,\alpha=1\), SymInh). Источники: Elder-1 `TLAgent-20261020/runs/*/provenance.json` и M40 `10.245.1.17:/home/user/tl-agent/Nmsdk/.../_repro/runs/*/provenance.json` + `inh_grid_logs`. Сырой свод: [`INH_GRID_DIAG_HARVEST_2026-10-24.tsv`](INH_GRID_DIAG_HARVEST_2026-10-24.tsv). План §4: [`CLASSIC_BRANCH_INH_PLAN_2026-10-23.ru.md`](CLASSIC_BRANCH_INH_PLAN_2026-10-23.ru.md).

**Host/SHA (кампания):** Classic Elder-1; Branch+Classic S50 re-run M40. NeuronModel во всех строках: `NSPNeuronGenSymInhC1e9`. PostTune ON.

---

## 1. Вердикт

**SoftCold PASS = 0 / 72.** Ни один кейс не дал `fires=10000000` / Цель=да. Среди 38 `converged_posttune_finalized` почти все имеют `fires=00000000`, метрический `acc=7` (семь foil’ов молчат верно, target не стреляет), `mid_source=cpp_nonseparable`, `detection_quality=target_not_detected`. Остальные 34 — `not_converged_at_stop` (Need=1), Test не оценивался.

Вывод: Done-очередь закрыта инженерно; **научно сетка InhGrid на SymInh не дала селективности** на Span 25/50/100 ни на Classic fan-out, ни на Branch one-dendrite. Повторять pack/cold без новой гипотезы (нейрон / \(d,\alpha\) / TipR-бюджет / landscape) бессмысленно.

---

## 2. Сводка Trainer × Mode → Span → Mod

Группировка каноническая; NeuronModel везде `NSPNeuronGenSymInhC1e9` (не «семья паттерна»). Acc = N/8 из metrics; Цель = target fire.

### 2.1 Classic × N0 / N1

| Span | Conv OK | not_conv | Acc у conv | Цель | Типичный mid |
| --- | ---: | ---: | --- | --- | --- |
| 25 | 16/16 | 0 | 7/8 (или NA на 1) | нет (`00000000`) | `cpp_nonseparable` |
| 50 | 2/16 | 14 | 7/8 на `segei_n0`, `preinh_segei_n0` | нет | то же / missing |
| 100 | 0/16 | 16 | — | — | missing |

На Span 25 **Mod не дифференцирует** качество: `gen`, `preinh`, `nextseg`, `segei` и все комбинации сходятся одинаково в NonSeparable + silent target. На Span 50 единственные converged Classic — **SegEI-содержащие N0** (`segei`, `preinh_segei`); NextSeg-моды и почти весь N1 не финализируют PostTune. На Span 100 ни один Mod не дошёл до terminal Need=0.

Конфиги Train/Test: `Bin/Configs/SpikeSamples/StructTrain/SelectivityInhGrid/EXP_classic_S{25,50,100}_*_InhGrid_N{0,1}/{Train,Test}`.

### 2.2 Branch × N1

| Span | Conv OK | not_conv | Acc у conv | Цель |
| --- | ---: | ---: | --- | --- |
| 25 | 8/8 | 0 | 7/8 | нет |
| 50 | 4/8 | 4 | 7/8 | нет |
| 100 | 8/8 | 0 | 7/8 | нет |

Branch сходится **чаще Classic** на длинных Span (S100: 8/8 vs Classic 0/16), но **качество то же**: NonSeparable + `fires=00000000`. На Branch×S50 not_converged сосредоточены в модах с **NextSeg** (`nextseg`, `preinh_nextseg`, `nextseg_segei`, `all`); `gen` / `preinh` / `segei` / `preinh_segei` финализируют.

Конфиги: `.../SelectivityInhGrid/EXP_branch_S{25,50,100}_*_InhGrid_N1/{Train,Test}`.

---

## 3. Корневая причина `not_converged_at_stop`

Классификатор `posttune_verify.classify_training_convergence`: при `Need=1` и отсутствии terminal PostTune result → `not_converged_at_stop`. Поллинг логов (et≈3.3 ч / 12030 s на Classic S100) даёт три устойчивых режима:

### A. Структурный stall (`L=1 1 1 1`, TipR заморожен `86e6`)

Часто на Classic S50/S100 для `all`, `*segei*`, `nextseg_segei` (и части nextseg): AUTOSAVE не показывает роста длины; TipR не меняется; `tipr_settled=1`, `flag=0`, Need=1 до таймаута. Интерпретация: **структурный поиск не разворачивает дендриты**, PostTune mid не достигается.

### B. Рост L без адаптации TipR (N0) / rmax_stall (N1)

`gen`/`preinh`/`nextseg` N0: L доходит до порядка `52 43 27 1` (S100) или `27 22 15 1` (S50), но TipR остаётся `86e6` (N0 не крутит TipR) и Need не сбрасывается. N1-аналоги чаще заканчивают как **`rmax_stall=1` + `tipr_settled=0`** без финального AUTOSAVE TipR/L в логе — параметрический контур упирается в Rmax-escape/stall, mid не финализируется.

### C. «Verify при Need=1 в последнем poll»

На S25 и части Branch poll-хвост может ещё показывать Need=1, тогда как `provenance.after.IsNeedToTrain=0` и `converged_posttune_finalized`: finalize очищает Need **после** последнего poll. Для диагностики качества опираться на provenance, не на mid-run poll.

**Итог по convergence:** not_converged — не infra disk_stop (хвост закрыт), а **недостижение terminal Train state** за бюджет et; доминируют stall длины (A) и stall TipR/Rmax (B). Mod NextSeg на Branch×S50 коррелирует с B/A сильнее, чем SegEI alone.

---

## 4. Абляция механизмов (качество)

На всех **converged** ячейках абляция preinh / NextSeg / SegEI **не меняет** Test-картину: везде `cpp_nonseparable` и silent target. Следовательно, на текущем SymInh + Classic fan-out / Branch one-dendrite **ни один из трёх механизмов не дал измеримого PASS**; отличие только в том, *доходит ли* Train до PostTune finalize (Branch лучше на S100; Classic S50 — только SegEI∩N0).

Гипотезы следующего шага (не cold-повтор той же сетки):

1. **Landscape / mid:** NonSeparable на всех conv → проверить, не ломает ли SymInh+SegEI \(\alpha=1,d=8\) разделимость уже на linear oracle / Train thr (см. постановку \(m_8<0\)).
2. **TipR/N1 бюджет:** Classic N1 S50/S100 → rmax_stall; возможно ужесточить escape или стартовый TipR/bounds.
3. **Структурный L=1:** кейсы с SegEI/all на Classic длинных Span — wiring/Ensure*Inh vs fan-out (отдельный wiring audit, не полный re-grid).
4. **Контроль без Inh:** короткий SoftCold `gen` на том же SymInh vs HIST AsymRm baseline — отделить «SymInh сам не селективен» от «Inh ломает».

---

## 5. Deliverables / статус Diag

| Артефакт | Статус |
| --- | --- |
| Harvest TSV 72 cases | done — `INH_GRID_DIAG_HARVEST_2026-10-24.tsv` |
| Этот DIAG | done |
| Acc/Need колонки в RESULTS | done (addendum Diag) |
| План §4 + статус | done |
| SoftCold PASS | **0** — реестр SUCCESSFUL не трогаем |

Next action: выбрать одну гипотезу из §4 и оформить узкий cold (не 72), либо wiring-audit L=1; silent full re-run запрещён постановкой Diag.

---

## 6. Follow-up (2026-10-24): wiring-audit L=1 + контроль без Inh

Постановка: гипотезы §4.3–4.4 — проверить, не сломан ли Ensure*Inh/Model у L=1 stall, и отделяет ли `gen` (NS=0,EI=0) на SymInh «Inh ломает» от «SymInh сам не селективен».

### 6.1 Wiring / flags — **не баг разводки**

По `SelectivityInhGrid/EXP_classic_S{25,50,100}_*_InhGrid_N0/Train`:

| Проверка | Результат |
| --- | --- |
| `EnableNextSegmentInhibition` / `EnableSegExcInh` | Совпадают с именем Mod (gen=0/0, nextseg=1/0, segei=0/1, all=1/1, …) на всех Span |
| `SegExcInhDelta` / `Alpha` | везде \(d=8\), \(\alpha=1.0\) |
| Model SHA gen vs segei | **идентичны** (SegEI/NextSeg только Parameters) |
| Model preinh vs gen | отличается `UsePresynapticInhibition=1`, `InhibitionCoeff=2.5` (ожидаемо) |
| Active neuron | `NeuronClassName=NSPNeuronGenSymInhC1e9` (AsymRm в Model — библиотечный хвост, не active) |

**Вывод:** Classic S100 `segei`/`all` с `L=1 1 1 1` — это **динамический stall при включённом SegEI (и комбинациях)**, а не отсутствующие Inh-линки в XML. Починка wiring cold-сетки не требуется. Линейный оракул \(m_8<0\) из постановки согласуется с тем, что SegEI может блокировать полезный рост на длинном Span.

### 6.2 Контроль без Inh (гипотеза §4.4) — **уже в сетке**

`inh_c25_gen_{n0,n1}` и `inh_b25_gen_n1`: NS=0, EI=0, preinh off → это контроль «только SymInh». Результат тот же, что у SegEI/NextSeg/preinh: `converged_posttune_finalized`, fires=`00000000`, Acc=7/8, mid=`cpp_nonseparable`.

HIST SoftCold AsymRm `SelectivityAsymRm/EXP_span25ms_packA_gen_posttune` (`NeuronClassName=NSPNeuronGenAsymRmD001C1e9`) в каноне давал PASS fires=`10000000` (см. `POST_TRAIN_VERIFY.ru.md` V3). Значит доминирующая ось провала InhGrid — **замена нейрона на SymInh**, а не три механизма торможения.

### 6.3 Уточнённый next action

1. **Узкий cold (рекомендуется):** один case Classic S25 `gen` с `NeuronClassName→AsymRmD001C1e9` на том же InhGrid fan-out / PostTune ON — проверить, возвращается ли PASS без Inh. При PASS — SymInh culpable; при FAIL — виноват clone/fan-out InhGrid, не Rm_inh.
2. **Не делать:** re-grid×72, wiring-patch Model, silent pack.
3. Опционально позже: SymInh + SegEI \(\alpha\!\downarrow\) / \(d\!\downarrow\) только после (1).

Статус follow-up: wiring-audit **закрыт**; контроль без Inh **снят с evidence сетки** (gen=FAIL); узкий AsymRm-swap cold — **не запускался** (нужен явный execute).
