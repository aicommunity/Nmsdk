# M1 карта границ: полный 25 мс, затем br50_preinh

**Trainer=Branch · Mode=N1** (равн. BR-M1 track). Канон группировки: [RESULT_GROUPING_HIERARCHY.ru.md](RESULT_GROUPING_HIERARCHY.ru.md).  
Ниже сохранён хронологический разбор прогонов; сводные PASS/FAIL читать также в [STATUS…](../STATUS.ru.md) по Span → NeuronModel=baseline → Mod.

## Метод (исправлен 2026-10-18)

Не формальные «соседи по id». Порядок:

1. Все модификации **@25 мс**: `gen`, `nextseg`, `preinh`.
2. Затем **`br50_preinh`**.
3. FAIL → трасса → фикс (не только ярлык Incomplete).

В матрицу добавлен `W10_HIST_br25_gen` (Bin `2c628a85`).

## Seed (исторический)

`W10_HIST_br25_nextseg` на `.17` / PulseLib `2820738`: **PASS 8/8**, L=`[9,8,5,1]`.

## Фикс роста

На `11-05` @25 мс длина осциллировала `5↔6` без NoImprove→best-effort. PulseLib `2f22c26`: scoped edit сохраняет streak; Dissync-`length_ok` только при свежем `DendLastAbsDt`.

## Прогон — `tl-m1-25ms-full-20261018-11-36` (завершён)

Хост `.11`, PulseLib `2f22c26`, Console `0b25d88f…`. Fingerprint `65b47094…`.

| Case | Training | C++ Test fires | Quality | Длины | Вердикт |
|---|---|---|---|---|---|
| `W10_HIST_br25_nextseg` | Need=0, converged | `10000000` FA=0 | **pass / detected** | `[7,6,4,1]` N=`[1,1,1,1]` | **PASS** (короче seed `[9,8,5,1]`) |
| `W10_HIST_br50_preinh` | Need=0, converged | `10000000` FA=0 | **pass / detected** | `[15,12,6,1]` | **PASS** (раньше silence на `11-05`) |
| `W10_HIST_br25_gen` | Need=0, converged | `00000000` silence | fail / not detected | `[7,6,4,1]` | **train OK, Test silence**; train-mid даёт fire-all |
| `W10_HIST_br25_preinh` | refuse phase=5 reason=3 | — | incomplete | `[16,13,3,1]` synced=`[0,1,1,1]` | **InvalidPeakNoRecovery** на pulse0 при TipR↓ |

Очередь: `paused_after_training_or_evaluation_issue` (1 training_stop + 1 quality_failure) — ожидаемо при `--no-commit`.

## Регрессии по пути (закрыты)

| Симптом | Причина | Фикс |
|---|---|---|
| refuse `failure_reason=3` за ≤6 iter | пустые PeakSeen окна | `cb57b08` |
| PeakSeen[2]=0 после L-step | EstDelay poison от sentinel | `35b805c` |
| L=3↔4 stall | full invalidate → Active thrash | `b861f8b` |
| L=5↔6 без stop | NoImprove/LastLengthDelta сброс + stale Dissync length_ok | `2f22c26` |

## Открытые дефекты (после `11-36`)

1. **br25_preinh refuse@3**: pulse0 растёт L 9→16, peak_seen=1, но `invalid_peak_no_action` 0→3 → refuse; TipR mid-pulses уходит в ~2.88e6.
2. **br25_gen silence на C++ Test** при полном sync Train; train-candidate mid → fire-all (порог/амплитуда).
3. Структура nextseg короче исторической — селективность удержана, но запас по delay иной.

## Сводка (иерархия Trainer×Mode → Span → NeuronModel → Mod)

Рост-фикс восстановил **nextseg@25** и **br50_preinh** до C++ PASS. Остров больше не только «старый срез». Следующие оси: InvalidPeak на preinh/pulse0 и post-train amplitude/threshold для gen (silence vs fire-all).

| Span | NeuronModel | Mod | PostTune ON (типичный HIST/N+1) | PostTune OFF (A2.1) |
|---|---|---|---|---|
| 25 | baseline | nextseg | PASS `10000000` | — |
| 25 | baseline | gen | silence thr≈1 | detected `10110000` |
| 25 | baseline | preinh | silence thr≈1 | silence |
| 50 | baseline | preinh | PASS | — |
| 50 | baseline | nextseg | Incomplete D6 | — |
| 100 | baseline | preinh | PASS | — |
| 100 | baseline | nextseg | Incomplete D6 | — |

## P0 rerun + `.17` regress — PulseLib `e23f2e9`

| Run | Host | Console | Итог |
|---|---|---|---|
| `tl-m1-p0-rerun-20261018-17-24` | `.11` | `9d8da6ad` | D2 refuse снят; `br25_preinh` Incomplete (L thrash); `br25_gen` silence |
| `tl-m1-p0-regress-17-20261018-18-25` | `.17` | `26f0d6da` | **PASS×3**: nextseg@25, preinh@50, preinh@100 |

PASS-остров после P0 **не сломан**. Открыто: D2 residual (Incomplete), D3, D6; на M0 — **D7** (early BE vs seg-order).

## M1-ext dt-ось — `tl-m1-dt-axis-20261018-16-12`

Хост `.11`, PulseLib `2f22c26`, Console `0b25d88f…` (тот же срез, что `11-36`). Fingerprint `832dce57…`. Очередь: `paused_infrastructure_or_incomplete_results` (2 Incomplete nextseg) — ожидаемо при `--no-commit`.

| Case | Training | C++ Test fires | Quality | Длины / audit | Вердикт |
|---|---|---|---|---|---|
| `W10_HIST_br100_preinh` | Need=0, converged_posttune | `10000000` FA=0 (cpp_test) | **pass / detected** (train-mid silent) | L=`[21,18,11,1]` synced=`[1,1,1,1]` TipR mid~`[2.88e6,3.98e6,3.57e7,86e6]` | **PASS** — preinh-ось шире 50 мс |
| `W10_HIST_br50_nextseg` | not_converged_at_stop, Need=1 | — | incomplete | L=`[1,1,1,1]` N=`[1,1,1,1]` peak_seen=`[0,0,0,0]` peak_locked=`[1,1,1,0]` last_abs_dt≈1.501 | **Incomplete / peak-blind** (D6) |
| `W10_HIST_br100_nextseg` | not_converged_at_stop, Need=1 | — | incomplete | то же: peak_seen all0, L stuck1 | **Incomplete / peak-blind** (D6) |

Сравнение с seed nextseg@25 L=`[7,6,4,1]` / hist PASS `[9,8,5,1]`: на 50/100 мс Train не видит пики вовсе (не refuse@3 и не silence-после-Need=0).

Классификация: **preinh@100 = PASS**; **nextseg@50/100 = новый класс D6** (peak blindness + peak_locked без PeakSeen), не D1/D2/D3.

## D6 audit: nextseg@25 vs @50 (до кода)

Одинаковый soft-cold tip-1, один SHA `2f22c26`/`e23f2e9` класс. Мембрана/PartsVec/паттерн **не** объясняют разрыв (см. Post-P0 plan).

| | nextseg@25 (PASS) | nextseg@50 (Incomplete) |
|---|---|---|
| PeakSeen | `[1,1,1,1]` | `[0,0,0,0]` |
| PeakLocked | `[1,1,1,1]` | `[1,1,1,0]` |
| L / sync | `[7,6,4,1]` / all1 | `[1,1,1,1]` / all0 |
| last_abs_dt | ~1e-4 (свежий) | `≈IterationGap` sentinel |
| TipR | midband ~2e7…4e7 | flat `86e6` (не трогали) |

**Вердикт D6:** измерительный путь не фиксирует пик при NextSeg@50 (peak_lock без PeakSeen + sentinel LastAbsDt). Гипотеза — **NextSeg-inh / окно peak measure / peak_lock**, не spike-паттерн и не PartsVec. Код не трогать, пока нет трассы PeakLock vs mute/inh на @50.

## D3 evidence: `br25_gen` mid/TipR (`tl-m1-p0-rerun-17-24`)

| Поле | Значение |
|---|---|
| Train | Need=0, L=`[7,6,4,1]`, synced all1 |
| TipR end-train | ~`[20.3e6, 14.5e6, 42.0e6, 86e6]` |
| TipR after (matrix) | `[20e6, 20e6, 20e6, 86e6]` (PostTune CanonRmin flatten) |
| train_candidate_mid | `0.102` |
| C++ Test | fires=`00000000`, `test_mid_nonseparable`, gap≈`-1.7e-4`, mode=silent |

**Гипотеза D3:** структура/sync ок; селекция ломается на **post-train amp/пороге** (CanonRmin flatten + NonSeparable mid), не на growth. Фикс — точечно mid/PostTune/margin, не L/N.

**N+1 cold 2026-10-19 (`tl-m1-n1-d3-silence-…`, PL `20c3e22`):** gen — `train_threshold_test` fires=`11111111` thr≈0.102, `cpp_test` fires=`00000000` thr=`1`; preinh — оба пути silence (train thr≈0.084, cpp thr=`1`).  
Следствие: «не калибровать cpp» у gen даёт **all-fire**, не нейтраль. Новые оси: PostTune off; **amp overshoot** (пик чуть выше эталона); разбор thr=`1`.

### A2.1 PostTune OFF — `tl-m1-n1-a21-ptoff-20261019-10-34` (`.11`, PL `20c3e22`)

| Case | Need | TipR | fires (C++ Test) | detection |
|---|---|---|---|---|
| `br25_gen` | 0 | midband (не CanonRmin `20e6`) | `10110000` | **detected** (не 8/8, не silence) |
| `br25_preinh` | 0 | midband | `00000000` | silence |

**Вывод:** CanonRmin/PostTune flatten был сильным фактором silence у **gen**. Без PostTune — частичный паттерн + target. **preinh** всё ещё silence → нужен A2.3 overshoot / другой рычаг amp.

### A2.3 TipR×0.75 post-Need=0 (`tl-m1-n1-a23-overshoot-20261019-10-52`)

| Case | A2.1 fires | A2.3 fires | thr | вывод |
|---|---|---|---|---|
| `br25_gen` | `10110000` detected | `11111111` fire_all | ≈0.026 | TipR↓ слишком сильный → all-fire |
| `br25_preinh` | `00000000` | `00000000` | ≈0.192 | overshoot×0.75 **не** снимает silence |

Следствие: глобальный TipR-down не лечит preinh; у gen уже был рабочий midband — усиливать amp нельзя. Дальше: A2.4 (cpp thr=1 / mid) или точечный TipR только на undershoot-входах preinh.


## D2 residual fix (код + cold)

**Корневая причина thrash:** `PeakSeen=1` / `SomaPeakValid=0` → invalid-peak length-recovery ±L при `|dt|∈(SyncTol, SyncTol×4]` и TipR@Rmin; каждый ±L → Invalidate → LastAbsDt=Gap → sync не коммитится.

**Фикс:** на TipR@Rmin принимать timing band `SyncTol×kRminLengthTolFactor` (и valid-, и invalid-peak path) → DendStatus=0 + BE.

**Cold** `tl-m1-d2v4-preinh-17-20261018-21-36` (`.17`, SHA `6f6624ab`): Need=0, L=`[16,13,3,1]`, synced all1, **без** Incomplete/L-thrash. C++ Test silence (класс D3 mid/PostTune), не D2.

**PASS regress** `tl-m1-pass-regress-d2v4-17-20261018-21-57`: nextseg@25 / preinh@50 / preinh@100 — **PASS×3** fires=`10000000`.

## Sync-parity Mode=0 vs Mode=1 (P4)

Общий sync-контракт (`PeakSeen` + `length_ok`/`BE` + `seg_ok` → `PulseSynced`) **один** в `FinishTrainingIteration`. Расхождения — **mode-gated amp/BE политики**, не разные правила закрытия пульса:

| | Mode=0 (M0 W04) | Mode=1 (W10 HIST) |
|---|---|---|
| Amp путь | +N / early BE@N≥8 | TipR + InvalidPeak length recovery |
| BE риск | D7: early BE без seg_ok → idle (исправлено) | D2: thrash@Rmin без BE (исправлено) |
| Sync commit | тот же seg_ok / PeakSeen | тот же |

**Вердикт P4:** этап sync **совпадает** по правилам; отличия amp-веток допустимы. Баги контракта были в BE-политиках, ломавших общий seg_ok/length_ok.
