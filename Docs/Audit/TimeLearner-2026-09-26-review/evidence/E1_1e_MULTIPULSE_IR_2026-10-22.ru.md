# E1.1e — multi-pulse tip IR NextSegInh / PSI vs passive (scoped)

Постановка: **E1.1d** показал, что одиночный импульс NextSegInh на tip PASS-острова `br25_nextseg` (L = 7) почти совпадает с passive по FWHM (~62 мс) и **не** воспроизводит полосу E1.4 `ideal_inh_proxy` (τ = 0.5 мс / FWHM/span ≲ 0.13 ⇒ FWHM ≲ 3.25 мс при span 25). Гипотеза аудита: сужение проявляется на **паттерн-уровне** при пачке. Этот scoped-проход проверяет **офлайн** tip-drive 2–4 импульсов с Pack-A ISI (и абсолютные времена target Pack-A) для **AsymRm**, mods **passive / nextseg / psi_k2_5**, L ∈ {1, 7, 10, 25}, TipR = 8.6×10⁷. Полный Rs-grid, Console Branch IR и полная 4-дендритная суперпозиция Pack-A **не** входили в scope.

**Политика источников:** тот же dual-channel Euler, что E1.1d (`NPulseChannel`/`NPulseSynapse`). Метрики: envelope peak/FWHM пачки **и** локальные **last_*** после последнего импульса (baseline-subtract, half-decay, late50) — именно last_fwhm сравнивается с гейтом E1.4. **Console** в этот turn **не** запускался (E1.1d hang на probe; слоты `.11` свободны, но якорь не критичен для отрицательного offline-вердикта). G1 RERUN / F1b / KeepDone **не** трогались.

**Машиночитаемый срез:** [`E1_1e_MULTIPULSE_IR_2026-10-22.tsv`](E1_1e_MULTIPULSE_IR_2026-10-22.tsv) (132 строки = 4 L × 1 TipR × 11 протоколов × 3 mod). Инструмент: [`tools/e1_1e_multipulse_ir.py`](tools/e1_1e_multipulse_ir.py). База: HEAD с E1.1d **`da88a998c`**.

**Группировка:** Trainer×Mode → Span → NeuronModel → Mod — для tip-probe Trainer/PostTune **N/A**; Span ориентир **25 мс Pack-A**; **NeuronModel = AsymRm → Mod ∈ {passive, psi_k2_5, nextseg} → L → protocol**. Конфиги Train/Test: **N/A** (offline); ориентиры острова: [Train nextseg](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_nextseginh_C1e9/Train) · [Test nextseg](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_nextseginh_C1e9/Test); Classic PSI: [Train PSI25](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N1_PSI25/Train) · [Test PSI25](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N1_PSI25/Test).

## Сетка

| Ось | Значения |
|---|---|
| NeuronModel | `NSPNeuronGenAsymRmD001C1e9` |
| L | 1, **7** (tip острова), 10, 25 |
| TipR | 8.6×10⁷ |
| Protocols | `n1_single`; n ∈ {2,3,4} × ISI ∈ {4.167, 8.333, 12.5} мс; `packA_tgt4` = {0, 4.17, 12.5, 25} мс |
| Mod | `passive` / `psi_k2_5` / `nextseg` |
| E1.4 gate | last_fwhm ≤ 3.25 мс (FWHM/span25 ≤ 0.13) |

## Ключевые результаты @ TipR = 8.6e7

### Остров L = 7 (nextseg vs passive)

| Protocol | last_fwhm nextseg | Δ last_fwhm | half_decay | late50 | meets gate |
|---|---:|---:|---:|---:|:---:|
| n1_single | 62.4 мс | −0.16 % | 35.9 мс | 0.29 | **нет** |
| n4_isi8.333ms | 65.4 мс | 0 % | 36.6 мс | 0.30 | **нет** |
| packA_tgt4 | 65.8 мс | 0 % | 36.9 мс | 0.30 | **нет** |
| n4_isi4.167ms | 63.3 мс | 0 % | 36.2 мс | 0.30 | **нет** |

На tip острова multi-pulse **не** сужает last_fwhm относительно passive; отношение last_fwhm/span25 ≈ 2.5–2.6 (нужно ≲ 0.13). PSI k = 2.5 по-прежнему даёт amp ≈ ×2.3–2.4 при Δ last_fwhm ≲ +0.5 % (чуть **шире**, не уже).

### L = 1 (где E1.1d уже видел хвост-cut)

| Protocol | last_fwhm nextseg | Δ vs pas | half_decay | late50 | gate |
|---|---:|---:|---:|---:|:---:|
| n1_single | 22.0 мс | −9.5 % | 14.7 мс | −0.33 | нет |
| n4_isi8.333ms | 6.3 мс | −18 % | 3.5 мс | ≪0 (IPSP) | нет |
| packA_tgt4 | **4.1 мс** | **−32 %** | 2.2 мс | ≪0 | **нет** (порог 3.25) |

На L = 1 пачка усиливает late-IPSP aftereffect NextSeg и локально режет last_fwhm, но даже лучший случай (4.1 мс) **не** входит в полосу τ = 0.5 мс / gate 3.25 мс; числа частично отражают биполярный хвост, а не «идеальный EPSP».

### L ∈ {10, 25}

NextSeg ≡ passive по last_fwhm / half_decay / late50 (Δ ≈ 0). PSI — amp↑ без сужения.

**Сводка по гейту:** **0 / 132** строк с `meets_e14_fwhm_gate=1`.

## Вердикт: можно ли снять `ideal_inh_proxy`?

**Нет.** Tip multi-pulse (Pack-A ISI / packA_tgt4) **не** объясняет островное сужение ядра до τ ≈ 0.5 мс. Для L = 7 nextseg-трассы пачки неотличимы от passive по ширине; proxy в E1.4 остаётся **феноменологическим** стендом Acc-direction (gate 6/6), а не измеренным ядром.

Возможный следующий gap (вне этого PARTIAL): **4-дендритная** суперпозиция с NextSegInh на каждом входе при Pack-A timing (coincidence / foil rejection), а не tip-train IR; либо Console Branch soma-trace на Train `br25_nextseg`. Дешёвый tip multi-pulse эту дыру **закрыл отрицательно**.

## Вердикт E1.1e

| Область | Статус | Комментарий |
|---|---|---|
| Offline multi-pulse tip IR AsymRm × L∈{1,7,10,25} × Pack-A ISI | **PARTIAL DONE** | 132 строки; инструмент + TSV |
| NextSeg @ L=7 vs E1.4 FWHM gate | **DONE (negative)** | ≈passive; gate 0/132 |
| PSI multi-pulse amp / shape | **PARTIAL DONE** | amp×~2.3–2.4; FWHM не ↓ |
| Retire `ideal_inh_proxy` | **NO** | proxy остаётся |
| 4-dendrite Pack-A IR | **DONE negative → E1.1f** | sep&lt;0; proxy не retired — [`E1_1f_FOUR_DENDRITE_PACKA_2026-10-22.ru.md`](E1_1f_FOUR_DENDRITE_PACKA_2026-10-22.ru.md) |
| Console Branch soma IR | **PENDING** | вне scope; см. TECH_DEBT `DEBT-E1.1f` |

## Выводы

Офлайн multi-pulse tip-drive NextSegInh/PSI для AsymRm **измерен** на scoped-сетке и даёт отрицательный ответ на главный вопрос E1.1e: пачка с Pack-A ISI **не** превращает островный EPSP (L = 7) в узкое ядро τ = 0.5 мс. Сужение NextSeg остаётся заметным только на очень коротких L и усиливается late-IPSP, но не достигает порога FWHM/span ≲ 0.13. Следовательно, замена E1.4 `ideal_inh_proxy` измеренными tip-ядрами **по-прежнему не оправдана**; Controller VERIFY tol не должен опираться на FWHM из E1.1d/e. Открытый долг смещается к pattern-level / Console Branch IR или к явному сохранению proxy как intentional phenomenological stand-in.
