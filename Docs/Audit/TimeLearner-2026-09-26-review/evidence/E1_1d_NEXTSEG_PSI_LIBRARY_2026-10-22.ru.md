# E1.1d — библиотека импульсных откликов NextSegInh / PSI vs passive (scoped)

Постановка: этап **E1.4** явно оставил **PARTIAL**, потому что предсказатель разделимости для `nextseg`/`preinh` опирается на **ideal_inh_proxy** с τ = 0.5 мс при `length_sync_cv≤0.25`, а не на измеренные ядра ([`E1_4_SEPARABILITY_PREDICTOR_2026-10-22.ru.md`](E1_4_SEPARABILITY_PREDICTOR_2026-10-22.ru.md)). Параллельно **E1.5 FRAGILE** показал, что PASS-остров `br25_nextseg` держится на NextSeg. Этот scoped-проход закрывает чекбокс E1.1 «отдельно с NextSegInh и PSI» для **AsymRm** на короткой сетке **L ∈ {1, 4, 7, 10, 25}**, **N = 1**, несколько TipR, с записью **peak / t_peak / FWHM** и относительных δ относительно **passive** baseline. Полный L = 1…100 × Rs × N и NeuronModel A/B/C **не** запускались.

**Политика источников:** офлайн dual-channel Euler, повторяющий `NPulseChannel`/`NPulseSynapse` (тот же каркас, что `cable_model`). Passive-ветка **бит-в-бит** совпадает с бинарём `cable` (rel peak ≲ 10⁻⁹ на L ∈ {1,4,10,25}). PSI: `PresynapticInhibitionConductance` с **k = 2.5** (как W01 `PSI25` / Preinh2_5) и `OutputConstData = 4k/R`. NextSegInh: Exc на tip L, Inh на **L+1** (дистальнее tip), `Rm_inh = 1e8` → τ_inh = 100 мс, `R_inh = SynapseResistanceBase = 8.6e7`; soma amp = `SumPotential` = Vexc+Vinh. **Console:** prepare `tl_probe_kernels` для Classic PSIoff/PSI25 (L = 10,4,1,25) прошёл `wiring_ok`, но живой `-t 8` завис на росте `posttune_mid_dbg.txt` / warning Resistance bounds — **якоря Console в этот turn не сняты** (см. `$REPORTS/E1_1d_20261022/CONSOLE_HANG_NOTE.txt`). Branch NextSegInh probe через `tl_probe_kernels` **не** поддержан (Classic-only). G1 RERUN / F1b cold / KeepDone **не** трогались.

**Машиночитаемый срез:** [`E1_1d_NEXTSEG_PSI_LIBRARY_2026-10-22.tsv`](E1_1d_NEXTSEG_PSI_LIBRARY_2026-10-22.tsv) (45 строк = 5 L × 3 TipR × 3 mod). Инструмент: [`tools/e1_1d_nextseg_psi_library.py`](tools/e1_1d_nextseg_psi_library.py). База docs: HEAD до коммита — E1.5 **`f9e83bf8c`**.

**Группировка:** Trainer×Mode → Span → NeuronModel → Mod — для probe-физики Trainer/Span/PostTune **N/A**; ниже **NeuronModel = AsymRm → Mod ∈ {passive, psi_k2_5, nextseg} → L**. Конфиги Train/Test: **N/A** (offline); для острова Branch ссылки-ориентиры: [Train nextseg](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_nextseginh_C1e9/Train) · [Test nextseg](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_nextseginh_C1e9/Test); Classic PSI шаблон [Train PSI25](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N1_PSI25/Train) · [Test PSI25](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N1_PSI25/Test).

## Сетка

| Ось | Значения |
|---|---|
| NeuronModel | `NSPNeuronGenAsymRmD001C1e9` (τ = 10 мс, D = 1 мс, f = 20 kГц) |
| L | 1, 4, **7** (tip `br25_nextseg` L=`7 6 4 1`), 10, 25 |
| TipR | 2 × 10⁶, 2 × 10⁷, 8.6 × 10⁷ |
| N | 1 (Reset-before-pulse: независимый прогон из покоя) |
| Mod | `passive` / `psi_k2_5` / `nextseg` |

## Ключевые δ @ TipR = 8.6e7 (vs passive)

| L | Mod | peak | FWHM мс | Δpeak | ΔFWHM | комментарий |
|---:|---|---:|---:|---:|---:|---|
| 1 | passive | 0.004403 | 24.3 | — | — | ≡ cable |
| 1 | psi_k2_5 | 0.01067 | 24.4 | **+142 %** | +0.4 % | amp↑ из `4k/R`; форма почти та же |
| 1 | nextseg | 0.004327 | **22.0** | −1.7 % | **−9.5 %** | late-tail cut; integral &lt; 0 (IPSP aftereffect) |
| 4 | nextseg | ≈passive | 47.2 | ≈0 | −0.4 % | late50: 0.054→0.014 |
| 7 | nextseg | ≈passive | 62.4 | ≈0 | −0.2 % | tip PASS-острова; **FWHM не** → τ = 0.5 мс |
| 10 | psi_k2_5 | 0.003663 | 74.5 | **+143 %** | 0 % | |
| 10 | nextseg | ≈passive | 74.5 | ≈0 | 0 % | |
| 25 | nextseg / psi | см. TSV | 117.5 / 117.6 | psi +143 % / nextseg ~0 | ~0 | |

**Вывод по одиночному импульсу:** ни NextSegInh, ни PSI **не** воспроизводят идеальное узкое ядро τ = 0.5 мс (FWHM ≲ 3 мс для span 25). PSI на одном spike **увеличивает** amp (~×2.4 при k = 2.5) почти без сжатия FWHM — сужение в аудите относится к **мульти-спайковой** параболе `(1−k·p)·p` в пачке. NextSegInh заметно режет **хвост / FWHM** только на **коротких L** (L = 1: ΔFWHM ≈ −9.5 %, отрицательный late-integral); на L ≥ 7 (остров) одиночный IR почти совпадает с passive по FWHM — эффект острова, скорее всего, **паттерн-уровневый** (совместные Inh на L+1 при ISI), а не замена пассивного EPSP на τ = 0.5 мс.

## Как заменить `ideal_inh_proxy` в E1.4 (без полного RERUN)

1. **Не** подставлять measured single-pulse FWHM вместо τ = 0.5 мс — числа не сходятся (62 мс vs ≲ 3 мс).
2. Рабочий путь на следующий cheap offline pass: суперпозиция **measured** nextseg/PSI трасс из этого TSV (или multi-pulse IR: 2–4 spikes с ISI паттерна) вместо `ideal_delay`; сохранить CV-гейт ≤ 0.25.
3. Пока single-pulse nextseg@L≥7 ≈ passive, proxy τ = 0.5 мс остаётся **феноменологическим** стендом Acc-direction (E1.4 6/6); tol для Controller VERIFY — после multi-pulse / Console Branch IR.
4. Полный RERUN E1.4 **не** делался в этом turn (scoped OK).

## Вердикт E1.1d

| Область | Статус | Комментарий |
|---|---|---|
| **AsymRm × NextSegInh × L∈{1,4,7,10,25} × TipR×3 × N=1** | **PARTIAL DONE** | offline dual Euler; ≡ cable на passive |
| **AsymRm × PSI k=2.5** (та же сетка) | **PARTIAL DONE** | amp↑; FWHM≈passive на 1 spike |
| **δ peak/FWHM vs passive** | **PARTIAL DONE** | таблица + TSV |
| **Console PSI / Branch NextSeg якоря** | **PENDING** | prepare OK; Console hang (dbg); Branch probe tool gap |
| **Multi-pulse / pattern-level IR** | **PENDING** | нужно для реальной замены E1.4 proxy |
| **Gen / FastSpan / Rs×8 full / N-grid** | **PENDING** | вне scope |

## Выводы

Одиночные импульсные ядра NextSegInh/PSI для AsymRm **измерены** на scoped-сетке и дают ясную картину относительно passive: PSI масштабирует amp, NextSeg режет хвост только на коротких L. Это **не** оправдывает прямую замену E1.4 `ideal_inh_proxy` τ = 0.5 мс числами FWHM из single-pulse — для острова `br25_nextseg` (L = 7) FWHM остаётся ~62 мс. Следующий логичный дешёвый шаг: multi-pulse IR (ISI из packA span25) offline + починка Console probe hang / Branch-capable probe, затем точечная подстановка в `e1_4_separability_predictor.py` без полного cold RERUN.
