# E1.1c — scoped библиотека FastSpan (timing ± amp Rs/N)

Постановка: закрыть **PENDING FastSpan** из E1.1 / E1.1b для Stage1-физики контроллера: собрать **офлайн** библиотеку **t_peak / FWHM / peak** для нейрон-модели матричных волн W10 / W12 / W48 / FastSpanLtzCal — **`NSPNeuronGenD002C25e11`** — по тому же каркасу, что E1.1 timing и E1.1b amp, без полного §E1.1-sweep (PSI / NextSegInh / AsymRm A–C вне scope). Trainer×Mode для probe-физики **N/A**; конфиги Train/Test — **N/A** (offline `cable_model`, Console-якоря в этом turn **не** снимались). G1 RERUN / F1b cold / KeepDone W33 **не** трогались; S0 sep_margin уже DONE.

**Идентификация NeuronModel и кабельных параметров** (из XML + аудит-план + C2):

| Источник | NeuronClassName | τ = Rm·C | D (DissocTC) | f | Rm |
|---|---|---:|---:|---:|---:|
| `SelectivityFastSpan/EXP_span*ms_fast` (gen) | `NSPNeuronGenD002C25e11` | **2.5 мс** (C=2.5×10⁻¹⁰) | **2 мс** | **2000 Гц** (`Project.ini`) | 10 МОм |
| `SelectivityLtzCalibrate/FastSpanLtzCal/*_gen` | тот же | 2.5 мс | 2 мс | 2000 Гц | 10 МОм |
| `SelectivityBranchFastSpan/EXP_br_fs_*` | кинетика D002/C≈2.5e-10 на Branch-топологии | 2.5 мс | 2 мс | 2000 Гц | 10 МОм |
| preinh-варианты | `NSPNeuronGenPreinh2_5D002C25e11` | те же **пассивные** возбуждающие параметры для одиночного tip-EPSP | | | |

Имя класса `…C25e11` историческое; фактическая ёмкость в Parameters — **2.5×10⁻¹⁰** (τ=2.5 мс), согласовано с [`TIMELEARNER_AUDIT_AND_PLAN_2026-10-20.ru.md`](../TIMELEARNER_AUDIT_AND_PLAN_2026-10-20.ru.md) и C2_MATCH строк `(2.5, 2.0, span)`.

**Политика источников:** все строки — офлайн [`plans/AGENT_PLAN_2026-10-20/tools/cable_model`](../plans/AGENT_PLAN_2026-10-20/tools/cable_model/). Калибровка amp Console↔model для FastSpan в E1.0 **отсутствует** → `peak_calibrated = peak_model`, `cal_mode=none_pending_console`. Timing опирается на C2_MATCH для (τ=2.5 мс, D=2 мс); относительная ошибка t_peak/FWHM vs Console для FastSpan **не** измерена в этом turn (в отличие от Gen/AsymRm E1.0 ≤5 % на опорных L).

**Машиночитаемый срез:** [`E1_1c_FASTSPAN_LIBRARY_2026-10-22.tsv`](E1_1c_FASTSPAN_LIBRARY_2026-10-22.tsv) (**148** строк = 100 timing + 24 Rs + 24 N). Повторяемость: [`tools/e1_1c_fastspan_library.py`](tools/e1_1c_fastspan_library.py). База docs: HEAD до коммита этого отчёта.

**Группировка (probe-only):** Trainer×Mode → Span → NeuronModel → Mod — **N/A**. Ниже — **NeuronModel → slice (timing|Rs|N) → L**.

## Сетки (scoped / truncated)

| Slice | Параметры | Размер | Примечание |
|---|---|---:|---|
| **timing** | L = 1…100, TipR = 8.6×10⁷, N = 1 | 100 | полный аналог E1.1 |
| **Rs** | 8 log TipR ∈ [2×10⁶ … 8.6×10⁷], L ∈ {1, 10, 25}, N = 1 | 24 | **усечено** vs E1.1b (нет L = 50) |
| **N** | N ∈ {1,2,4,…,128}, TipR = 8.6×10⁷, L ∈ {1, 10, 25} | 24 | 4 точки `model_unstable` (см. ниже) |

## Сводка δ / γ vs Gen / AsymRm

Линейная оценка **δ ≈ (t_peak(L) − t_peak(1)) / (L − 1)** и **γ(L) = −ln(peak(L)/peak(1))/(L−1)** на TipR = 8.6×10⁷, N = 1 (модель):

| NeuronModel | δ (мс/сег) @ L→100 | t_peak(1) мс | t_peak(10) мс | t_peak(50) мс | FWHM(10) мс | γ(10) | γ(25) |
|---|---:|---:|---:|---:|---:|---:|---:|
| **NSPNeuronGenD002C25e11** (E1.1c) | **≈ 1.99** | 4.0 | 21.0 | 101.0 | 17.0 | 0.0967 | 0.0544 |
| NSPNeuronGen (E1.1) | ≈ 9.48 | 15.0 | 99.0 | 479.0 | 73.0 | ≈0.108 | ≈0.059 |
| NSPNeuronGenAsymRmD001C1e9 (E1.1) | ≈ 9.96 | 10.05 | 100.9 | 498.9 | 74.5 | ≈0.119 | ≈0.064 |

**Ключ:** FastSpan даёт **~5× меньшую** задержку на сегмент и **~4× уже** FWHM на L = 10 при **сопоставимом** порядке γ(L) с Gen на каноническом TipR. Peak на TipR = 8.6e7 / L = 10 ≈ **0.0111** vs Gen **0.0060** / AsymRm **0.0015** (пассивный cable) — выше Gen за счёт более короткого τ при том же Rm/TipR.

По лог-сетке TipR (L = 10) γ почти константна (**0.095…0.100**) для TipR ≥ 3.4×10⁶; выброс **γ ≈ 0.194** только на TipR = 2×10⁶ (сильный шунт / насыщение peak) — качественно та же картина «γ(TipR) не рычаг AMP_ALIGN», что в E1.1b, с оговоркой на нижний край Rs.

## Выборка timing (TipR = 8.6e7)

| L | t_peak_ms | FWHM_ms | peak_model | δ_vs_L1_ms | γ_vs_L1 |
|---:|---:|---:|---:|---:|---:|
| 1 | 4.0 | 7.0 | 0.02646 | — | — |
| 4 | 9.0 | 11.0 | 0.01655 | 1.67 | 0.156 |
| 10 | 21.0 | 17.0 | 0.01108 | 1.89 | 0.0967 |
| 25 | 51.0 | 25.0 | 0.00718 | 1.96 | 0.0544 |
| 50 | 101.0 | 37.0 | 0.00511 | 1.98 | 0.0335 |
| 100 | 201.0 | 51.0 | 0.00363 | 1.99 | 0.0201 |

## Выборка Rs @ L = 10 (N = 1)

| TipR | peak_model | t_peak_ms | FWHM_ms | γ_vs_L1 |
|---:|---:|---:|---:|---:|
| 2.00×10⁶ | 0.2129 | 21.0 | 16.0 | 0.194 |
| 3.42×10⁶ | 0.1710 | 21.0 | 16.0 | 0.0950 |
| 8.60×10⁷ | 0.01108 | 21.0 | 17.0 | 0.0967 |

Отношение peak(2e6)/peak(8.6e7) ≈ **19.2** при отношении Rs **43** — сублинейность шунта, как у Gen/AsymRm. **t_peak/FWHM** почти не зависят от TipR (сдвиг ≤ 1 мс на сетке 2000 Гц).

## Выборка N @ TipR = 8.6e7, L = 10

| N | peak_model | peak / peak(N=1) | t_peak_ms | FWHM_ms | validity |
|---:|---:|---:|---:|---:|---|
| 1 | 0.01108 | 1.00 | 21.0 | 17.0 | model_valid |
| 2 | 0.02217 | 2.00 | 21.0 | 17.0 | model_valid |
| 4 | 0.04388 | 3.96 | 21.0 | 16.0 | model_valid |
| 8 | 0.08282 | 7.47 | 21.0 | 16.0 | model_valid |
| 16 | 0.1364 | 12.3 | 21.0 | 16.0 | model_valid |
| 32 | 0.1895 | 17.1 | 21.0 | 16.0 | model_valid |
| 64 | 0.1901 | 17.2 | 21.0 | 18.0 | model_valid (насыщение) |
| 128 | 61.54 | — | 32.0 | 12.0 | **model_unstable** |

До N ≈ 8 рост почти линейный; к N = 32–64 сильное насыщение. На **коротком τ** точки **N ≥ 64 @ L = 1** и **N = 128 @ L ∈ {10,25}** дают peak ≫ 1 (явный Euler blow-up) — помечены `model_unstable` и **не** для контроллера. У Gen (E1.1b) N = 128 на L = 10 ещё стабилен (~0.21); FastSpan требует более жёсткого потолка N в amp-библиотеке.

## Console-якоря

**Нет** в этом turn. Слоты `.17` были свободны, но для PARTIAL close достаточно offline + C2_MATCH; снятие soma-kernel FastSpan (аналог E1.0) остаётся **PENDING** (1–4 L на W46/`SelectivityFastSpan` Test).

## Вердикт E1.1c (этот scoped pass)

| Область | Статус | Комментарий |
|---|---|---|
| **NeuronModel FastSpan (D002C25e11)** | **PARTIAL DONE** | τ=2.5 мс, D=2 мс, f=2000; preinh = те же passive EPSP |
| **t_peak/FWHM L=1…100 @ TipR=8.6e7** | **PARTIAL DONE** | offline; δ≈1.99 мс/сег |
| **Rs × 8, L ∈ {1,10,25}** | **PARTIAL DONE** | L=50 **усечено**; γ≈const при TipR≳3e6 |
| **N ∈ {1…128}, L ∈ {1,10,25}** | **PARTIAL DONE** | 4 unstable точки задокументированы |
| **Console amp/timing anchors FastSpan** | **PENDING** | не снимались |
| **PSI / NextSegInh** | **PENDING** | вне scope |
| **Amp cal FastSpan (bias vs Console)** | **PENDING** | cal_mode=none_pending_console |

## Выводы

Для матричных FastSpan-конфигов пассивный кабель с **τ = 2.5 мс / D = 2 мс** даёт задержку и ширину EPSP, согласованные с замыслом коротких span 25–100 мс: δ ≈ **2 мс/сегмент** вместо ~10 мс у Gen/AsymRm, FWHM(L=10) ≈ **17 мс** вместо ~73 мс. Пространственная аттенюация γ(L) на каноническом TipR того же порядка, что у Gen, и почти не зависит от TipR вне нижнего края Rs — рычаг amp по-прежнему **Rs / N**, не «γ(TipR)». Кратность N эффективна примерно до 8…16, далее насыщение; при N ≳ 64–128 короткая постоянная времени делает офлайн-кабель **численно нестабильным** — контроллеру нужен потолок N жёстче, чем для Gen. Без Console-калибровки amp FastSpan библиотека пригодна для **F1-поиска L\* по задержке** и качественных оценок amp; количественный AMP_ALIGN на FastSpan — после точечных якорей.

**Train / Test:** N/A (probe-only offline). Опорные каталоги кинетики (не прогон): [`Bin/Configs/SpikeSamples/StructTrain/SelectivityFastSpan/`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityFastSpan/), [`SelectivityBranchFastSpan/`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranchFastSpan/), [`SelectivityLtzCalibrate/FastSpanLtzCal/`](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityLtzCalibrate/FastSpanLtzCal/).

**Следующий логичный шаг:** Console kernel FastSpan на 2–4 L (если слоты свободны); либо stub PSI/NextSegInh; либо CL-N1 / margin — **не** G1 RERUN и **не** F1b cold без senior.
