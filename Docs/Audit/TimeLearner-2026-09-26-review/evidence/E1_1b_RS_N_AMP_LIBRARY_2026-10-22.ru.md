# E1.1b — библиотека amp / Rs / N (scoped, после E1.1 timing PARTIAL)

Постановка: после scoped **E1.1 timing** ([`E1_1_TIMING_LIBRARY_2026-10-22.ru.md`](E1_1_TIMING_LIBRARY_2026-10-22.ru.md), commit **`190543c4a`**) собрать **срез амплитудной библиотеки** для контроллера и F5 (AMP_ALIGN / γ(TipR)): не полный NeuronModel-sweep плана §E1.1, а только **NSPNeuronGen** и **NSPNeuronGenAsymRmD001C1e9** на фиксированных длинах. Ось **Rs** — восемь лог-точек TipR от типичного нижнего пола (~2 × 10⁶, как в F5/W01 low TipR) до канонического **8.6 × 10⁷**, при **N = 1** и **L ∈ {1, 10, 25, 50}**. Ось **N** — кратность со-расположенных синапсов **N ∈ {1, 2, 4, 8, 16, 32, 64, 128}** при TipR = 8.6 × 10⁷ и **L ∈ {1, 10, 25}**. Каждый узел сетки — **независимый** прогон `cable_model` из покоя (семантика **Reset-before-pulse**): один одновременный onset в t = 0, без накопления состояния между точками Rs/N. Trainer×Mode для probe-физики **не применим** (N/A); конфиги Train/Test — **N/A** (offline cable, без cold Console в этом turn).

**Политика источников:** строки peak / t_peak / FWHM — офлайн [`plans/AGENT_PLAN_2026-10-20/tools/cable_model`](../plans/AGENT_PLAN_2026-10-20/tools/cable_model/) (бинарь локальный, **не** в git). Калибровка амплитуды по E1.0 PARTIAL ([`E1_0_CABLE_VS_CONSOLE_2026-10-22.ru.md`](E1_0_CABLE_VS_CONSOLE_2026-10-22.ru.md)): для Gen **peak_calibrated = peak_model / 1.067**; для AsymRm **peak_calibrated = peak_model × 1.46** (oracle-множитель к пассивному Rm = 1 × 10⁷; замена Rm → 1 × 10⁸ в cable **не** воспроизводит Console). Gen **L = 50** помечен **model_only / DEBT-C1-silent-soma** (Console amp invalid). G1 RERUN **не** стартовал; новых Console-якорей amp не снимали.

**Машиночитаемый срез:** [`E1_1b_RS_N_AMP_LIBRARY_2026-10-22.tsv`](E1_1b_RS_N_AMP_LIBRARY_2026-10-22.tsv) (112 строк = 64 Rs + 48 N). Повторяемость: [`tools/e1_1b_rs_n_amp_library.py`](tools/e1_1b_rs_n_amp_library.py). База docs: E1.1 **`190543c4a`**.

**Группировка (probe-only):** Trainer×Mode → Span → NeuronModel → Mod — **N/A** (нет Train/Test / PostTune). Ниже результаты сгруппированы по **NeuronModel → slice (Rs|N) → L**.

## Сетка TipR (8 log)

| i | TipR (Ом) |
|---:|---:|
| 1 | 2.000 × 10⁶ |
| 2 | 3.423 × 10⁶ |
| 3 | 5.858 × 10⁶ |
| 4 | 1.003 × 10⁷ |
| 5 | 1.716 × 10⁷ |
| 6 | 2.936 × 10⁷ |
| 7 | 5.025 × 10⁷ |
| 8 | 8.600 × 10⁷ |

## Сводка: γ(L) почти не зависит от Rs

Колонка `gamma_vs_L1 = −ln(peak(L)/peak(1))/(L−1)` на сыром `peak_model` при N = 1. По всем восьми TipR разброс γ мал (порядка процента от величины), то есть **пассивная пространственная аттенюация почти не смещается уровнем TipR** — в отличие от линейной по 1/Rs силы синапса. Это ограничивает гипотезу F5 «γ(TipR) чинит amp-align»: на пассивном кабеле γ(L) стабильна, а рычаг AMP_ALIGN — именно **Rs / N**, не переоценка γ.

| NeuronModel | L | γ min…max по Rs-сетке | t_peak @ TipR=8.6e7 (мс) | FWHM @ 8.6e7 (мс) |
|---|---:|---|---:|---:|
| NSPNeuronGen | 10 | 0.1075…0.1095 | 99.0 | 73.0 |
| NSPNeuronGen | 25 | 0.0589…0.0597 | 242.0 | 115.0 |
| NSPNeuronGen | 50 | 0.0358…0.0362 | 479.0 | 162.0 |
| NSPNeuronGenAsymRmD001C1e9 | 10 | 0.1193…0.1197 | 100.9 | 74.5 |
| NSPNeuronGenAsymRmD001C1e9 | 25 | 0.0636…0.0638 | 250.1 | 117.5 |
| NSPNeuronGenAsymRmD001C1e9 | 50 | 0.0382…0.0383 | 498.9 | 166.2 |

## Выборка Rs @ L = 10 (N = 1)

| NeuronModel | TipR | peak_model | peak_calibrated | t_peak_ms | FWHM_ms | validity |
|---|---:|---:|---:|---:|---:|---|
| NSPNeuronGen | 2.00e6 | 0.1508 | 0.1413 | 97.0 | 73.0 | model_valid |
| NSPNeuronGen | 8.60e7 | 0.005985 | 0.005609 | 99.0 | 73.0 | model_valid |
| NSPNeuronGenAsymRmD001C1e9 | 2.00e6 | 0.08314 | 0.1214 | 100.3 | 74.5 | model_valid |
| NSPNeuronGenAsymRmD001C1e9 | 8.60e7 | 0.001505 | 0.002198 | 100.9 | 74.5 | model_valid |

Отношение peak(Rs=2e6)/peak(Rs=8.6e7) ≈ **25.2** при отношении Rs **43** — сублинейность из-за шунтирования G = p/Rs на сегменте (не чистый 1/Rs).

## Выборка N @ TipR = 8.6e7, Gen L = 10

| N | peak_model | peak_calibrated | peak / peak(N=1) | t_peak_ms | FWHM_ms |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.005985 | 0.005609 | 1.00 | 99.0 | 73.0 |
| 2 | 0.01210 | 0.01134 | 2.02 | 99.0 | 73.0 |
| 4 | 0.02453 | 0.02299 | 4.10 | 99.0 | 73.0 |
| 8 | 0.04887 | 0.04581 | 8.17 | 99.0 | 72.0 |
| 16 | 0.08942 | 0.08381 | 14.9 | 98.0 | 73.0 |
| 32 | 0.1342 | 0.1257 | 22.4 | 97.0 | 72.0 |
| 64 | 0.1724 | 0.1616 | 28.8 | 98.0 | 73.0 |
| 128 | 0.2100 | 0.1968 | 35.1 | 98.0 | 73.0 |

До N ≈ 8 рост почти линейный; дальше сильное насыщение (шунт). **t_peak и FWHM** почти не зависят от N (сдвиг ≤ 2 мс). Та же картина на L = 1 и L = 25 (см. TSV). Для контроллера: в режиме N0 рычаг «добавить синапсы» эффективен только пока N ≲ 8…16; дальше выгоднее снижать TipR.

## Gen L = 50 (amp)

Все 8 точек Rs для Gen L = 50 помечены `validity=model_only_silent_debt`. Модель даёт конечный peak и timing (согласованный с E1.1), но Console soma на L ≈ 50–51 silent (**DEBT-C1**); калиброванный peak для контроллера на этой длине — **только proxy**, не якорь.

## Вердикт E1.1b (этот scoped pass)

| Область | Статус | Комментарий |
|---|---|---|
| **Rs × 8 log, L ∈ {1,10,25,50}, Gen+AsymRm** | **PARTIAL DONE** | offline cable + E1.0 cal; Gen L50 amp = debt |
| **N ∈ {1…128}, L ∈ {1,10,25}, TipR=8.6e7** | **PARTIAL DONE** | multiplicity + Reset; насыщение N≳16 |
| **γ(Rs) таблица** | **PARTIAL** | γ(L) ≈ const по Rs; F5 TipR-γ слабо поддержан пассивом |
| **Console amp anchors на новой Rs/N сетке** | **PENDING** | не снимались; опора на E1.0 @ TipR=8.6e7 |
| **FastSpan / PSI / NextSegInh** | **PENDING** | вне scope |
| **AsymRm A/B/C, W01/W10 full NeuronModel** | **PENDING** | вне scope |
| **Полный L=1…100 × Rs × N** | **PENDING** | план §E1.1 целиком |

## Выводы

На пассивном кабеле амплитуда одиночного EPSP управляется **TipR и кратностью N** при почти неизменных **t_peak/FWHM** (сдвиг миллисекунды), а оценка **γ(L)** остаётся почти постоянной по всей лог-сетке TipR. Для F5/AMP_ALIGN это означает, что коррекция «γ от текущего TipR» на пассиве не заменяет бисекцию по log Rs / N; paired cold F5 (γ=0 ≡ γ=1) согласуется с этой картиной. Калибровка Gen (**÷1.067**) и AsymRm oracle (**×1.46**) переносится на всю сетку как постоянный множитель к `peak_model`; новых Console-проверок на крайних TipR/N в этом turn не было. Gen L = 50 amp остаётся долгом silent-soma.

**Train / Test:** N/A (probe-only offline).

**Следующий логичный шаг:** либо точечные Console-якоря amp на 1–2 крайних TipR (если слоты `.11`/`.17` свободны), либо расширение моделей (FastSpan / NextSegInh / PSI), либо CL-N1 bisect / margin H1/H4 по плану синтеза — не повтор G1 RERUN.
