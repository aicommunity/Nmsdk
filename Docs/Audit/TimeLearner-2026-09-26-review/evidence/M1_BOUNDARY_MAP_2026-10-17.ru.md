# M1 карта границ: полный 25 мс, затем br50_preinh

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

## Сводка

Рост-фикс восстановил **nextseg@25** и **br50_preinh** до C++ PASS. Остров больше не только «старый срез». Следующие оси: InvalidPeak на preinh/pulse0 и post-train amplitude/threshold для gen (silence vs fire-all).
