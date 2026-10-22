# E1.1 — библиотека задержки и FWHM (scoped follow-up после E1.0 PARTIAL)

Постановка: после этапа **E1.0** ([`E1_0_CABLE_VS_CONSOLE_2026-10-22.ru.md`](E1_0_CABLE_VS_CONSOLE_2026-10-22.ru.md), commit **`642cabb5b`**, вердикт **PARTIAL**) собрать **первичную timing-библиотеку** для контроллера и F1 (поиск L\* по задержке): для **NSPNeuronGen** и **NSPNeuronGenAsymRmD001C1e9** на **TipR = 8.6e7**, одиночный EPSP, **L = 1…100**. Колонки: **t_peak**, **FWHM**, **peak** (Console где есть, иначе модель), provenance **RUN/json**. Полная сетка E1.1 по плану ([`TIMELEARNER_AUDIT_AND_PLAN_2026-10-20.ru.md`](../TIMELEARNER_AUDIT_AND_PLAN_2026-10-20.ru.md) §E1.1: Rs×8, N∈{1,2,4…128}, NextSegInh, PSI, FastSpan, AsymRm A/B/C) **не** запускалась в этом проходе.

**Политика источников (этот turn):** строки **t_peak / FWHM** для L без живого Console — **офлайн `cable_model`** с параметрами прогона (Gen: τ=10 мс, D=5 мс, f=2000 Гц; AsymRm: τ=10 мс, D=1 мс, f=20 kГц). Обоснование замены сетки — E1.0: на якорях **L ∈ {1, 4, 10, 25}** (Gen) и **L ≥ 4** (AsymRm) относительная ошибка **t_peak и FWHM ≤ 5%**; для Gen **L = 50** Console **silent**, timing берётся только из модели с пометкой **DEBT-C1-silent-soma**.

**Машиночитаемый срез:** [`E1_1_TIMING_LIBRARY_2026-10-22.tsv`](E1_1_TIMING_LIBRARY_2026-10-22.tsv) (200 строк = 2×100 L). Повторяемость: [`tools/e1_1_timing_library.py`](tools/e1_1_timing_library.py), `--reports ~/TLAgent-20261020/agent-reports`.

**Git (docs):** ветка `timelearner_fix2`, база E1.0 **`642cabb5b`**. Kernel JSON read-only: `$HOME/TLAgent-20261020/agent-reports/{C1_20261020_11,E1_0_20261022}/`.

## Сводка δ(L) (модель + якоря Console)

Линейная оценка **δ ≈ (t_peak(L) − t_peak(1)) / (L − 1)** по таблице TSV (модель на всём диапазоне; якоря совпадают с моделью на проверенных L):

| NeuronModel | δ (мс/сегмент) | t_peak(1) мс | t_peak(100) мс | FWHM(1) мс | FWHM(50) мс |
|---|---:|---:|---:|---:|---:|
| NSPNeuronGen | **9.48** | 15.0 (Console) | 954.0 (model) | 26.5 | 162.0 |
| NSPNeuronGenAsymRmD001C1e9 | **9.96** | 10.05 (Console) | 996.4 (model) | 23.0 | 166.2 |

## Якоря Console (kernel JSON)

Probe-only, `IsNeedToTrain=0`. Trainer×Mode не применим.

### NSPNeuronGen (f = 2000 Гц)

| L | t_peak_ms | FWHM_ms | peak Console | peak model (json) | source json | примечание |
|---:|---:|---:|---:|---:|---|---|
| 1 | 15.0 | 26.5 | 0.014605 | 0.015628 | `E1_0_20261022/kernel_gen_grid.json` | C1 p2 дублирует L=1 |
| 4 | 42.5 | 47.0 | 0.008592 | 0.009176 | `E1_0_20261022/kernel_gen_grid.json` | E1.0 якорь |
| 10 | 99.5 | 73.0 | 0.005608 | 0.005985 | `C1_20261020_11/kernel_2.json` | |
| 25 | 242.0 | 115.0 | 0.003591 | 0.003832 | `E1_0_20261022/kernel_gen_grid.json` | C1 p1 L=25 silent — заменён E1_0 |
| 30 | 289.5 | 126.0 | 0.003283 | 0.003503 | `C1_20261020_11/kernel_2.json` | |
| 43 | 413.0 | 150.5 | 0.002747 | 0.002932 | `C1_20261020_11/kernel_1.json` | |
| 50 | 479.0 | 162.0 | — | 0.002720 | `E1_0_20261022/kernel_gen_grid.json` | **silent soma**; timing = model |
| 51 | — | — | 0 (silent) | 0.002694 | `C1_20261020_11/kernel_1.json` | DEBT |
| 20 | — | — | 0 (silent) | 0.004275 | `C1_20261020_11/kernel_2.json` | DEBT |

### NSPNeuronGenAsymRmD001C1e9 (f = 20 kГц)

| L | t_peak_ms | FWHM_ms | peak Console | peak model (json) | source json | примечание |
|---:|---:|---:|---:|---:|---|---|
| 1 | 10.05 | 23.0 | 0.006110 | 0.004403 | `E1_0_20261022/kernel_asym_L50_w11.json` | L=1: t_peak −12.7% vs model (E1.0) |
| 4 | 39.9 | 47.35 | 0.003452 | 0.002349 | `C1_20261020_11/kernel_4.json` | |
| 10 | 99.65 | 74.5 | 0.002212 | 0.001505 | `E1_0_20261022/kernel_asym_L50_w11.json` | |
| 25 | 248.9 | 117.6 | 0.001406 | 0.000957 | `E1_0_20261022/kernel_asym_L50_w11.json` | |
| 50 | 497.65 | 166.2 | 0.000996 | 0.000678 | `E1_0_20261022/kernel_asym_L50_w11.json` | Gen L=50 silent; AsymRm L=50 **OK** |

**Peak (амplitude):** для Gen систематический bias **≈ −6.5%** Console vs passive cable → для контроллера умножать model peak на **≈ 0.935** или делить измерение на **≈ 1.067** ([`E1_0_CABLE_VS_CONSOLE_2026-10-22.ru.md`](E1_0_CABLE_VS_CONSOLE_2026-10-22.ru.md)). Для AsymRm peak **+39…+47%** vs model — **не** включать в timing-библиотеку без oracle Rm=1e8; в TSV колонка `peak_model` — passive cable, `peak_console` — только якоря.

## Выборочные строки L = 1, 4, 10, 25, 50, 100 (из TSV)

| NeuronModel | L | t_peak_ms | FWHM_ms | peak Console | peak model |
|---|---:|---:|---:|---:|---:|
| NSPNeuronGen | 1 | 15.0 | 26.5 | 0.014605 | 0.015777 |
| NSPNeuronGen | 4 | 42.5 | 47.0 | 0.008592 | 0.009174 |
| NSPNeuronGen | 10 | 99.5 | 73.0 | 0.005608 | 0.005985 |
| NSPNeuronGen | 25 | 242.0 | 115.0 | 0.003591 | 0.003832 |
| NSPNeuronGen | 50 | 479.0 | 162.0 | — | 0.002720 |
| NSPNeuronGen | 100 | 954.0 | 229.0 | — | 0.001932 |
| NSPNeuronGenAsymRmD001C1e9 | 1 | 10.05 | 23.0 | 0.006110 | 0.004403 |
| NSPNeuronGenAsymRmD001C1e9 | 4 | 39.9 | 47.35 | 0.003452 | 0.002349 |
| NSPNeuronGenAsymRmD001C1e9 | 10 | 99.65 | 74.5 | 0.002212 | 0.001505 |
| NSPNeuronGenAsymRmD001C1e9 | 25 | 248.9 | 117.6 | 0.001406 | 0.000957 |
| NSPNeuronGenAsymRmD001C1e9 | 50 | 497.65 | 166.2 | 0.000996 | 0.000678 |
| NSPNeuronGenAsymRmD001C1e9 | 100 | 996.4 | 234.9 | — | 0.000481 |

## Вердикт E1.1 (этот scoped pass)

| Область | Статус | Комментарий |
|---|---|---|
| **t_peak(L), FWHM(L), L=1…100** | **PARTIAL DONE** | Gen + AsymRm W01-class; модель + якоря C1/E1_0 |
| **δ(L), τ(L) таблицы** | **PARTIAL** | δ линейно из t_peak; τ(L) не выделена отдельно |
| **γ, Rs-сетка** | **PENDING** | 8 точек log Rs, TipR≠8.6e7 |
| **N-train (1,2,4…128)** | **PENDING** | с Reset; влияние на soma kernel |
| **NextSegInh, PSI** | **PENDING** | отдельные прогоны |
| **NeuronModel sweep** | **PENDING** | W01, W10, FastSpan, AsymRm A/B/C |
| **Amp library** | **PENDING** | Gen bias 1.067; AsymRm oracle; silent L50 Gen |

## Что E1.1 ещё требует (amp / Rs / N)

1. **Amplitude:** Console-сетка или калиброванная модель — Gen (**×1.067** к model peak), AsymRm (**oracle** тормозной Rm=1e8, ≈×1.45–1.47), разбор **silent soma** Gen на L≈50–51 и sporadic L=20,25 (C1 p1/p2).
2. **Rs (8 log-точек):** для каждой NeuronModel и опорного L — γ(Rs), сдвиг t_peak/FWHM/peak; база F5 paired TipR частично см. [`F5_GAMMA_PAIRED_2026-10-22.ru.md`](F5_GAMMA_PAIRED_2026-10-22.ru.md), но не заменяет E1.1 kernel grid.
3. **N ∈ {1,2,4,…,128}:** train-length sweep с Reset перед импульсом — амплитуда и форма на соме vs одиночный EPSP; нужно для F1/F5 и margin H1/H4.
4. **Расширение моделей:** тот же каркас L×Rs×N для **FastSpan**, **AsymRm A/B/C**, шаблонов W01/W10 — не покрыто текущим TSV.
5. **Одиночный missing-L cold Console** (опционально): только если понадобится снять silent **Gen L=50** — не блокирует timing L≤25 и модель L=50.

**Следующий логичный шаг:** E1.1b — Rs×N на фиксированных L={1,10,25,50} для Gen (Console amp) + AsymRm после oracle; либо CL-N1 bisect по плану синтеза.
