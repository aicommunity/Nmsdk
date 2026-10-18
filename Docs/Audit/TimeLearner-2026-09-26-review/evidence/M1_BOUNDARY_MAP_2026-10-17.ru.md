# M1 карта границ: полный 25 мс, затем br50_preinh

## Метод (исправлен 2026-10-18)

Не формальные «соседи по id». Порядок:

1. Все модификации **@25 мс**: `gen`, `nextseg`, `preinh`.
2. Затем **`br50_preinh`**.
3. FAIL → трасса → фикс (не только ярлык Incomplete).

В матрицу добавлен `W10_HIST_br25_gen` (Bin `2c628a85`).

## Seed (исторический)

`W10_HIST_br25_nextseg` на `.17` / PulseLib `2820738`: **PASS 8/8**, L=`[9,8,5,1]`.

## Фикс роста (после `11-05`)

На `tl-m1-25ms-full-20261018-11-05` @25 мс длина осциллировала `5↔6` без NoImprove→best-effort: scoped invalidate обнулял `NoImproveCount`/`LastLengthDelta`, а `length_ok` принимал stale Dissync сразу после reopen.

PulseLib `2f22c26` / root `da341d78e`: на scoped edit сохраняем streak; Dissync-`length_ok` только при свежем `DendLastAbsDt`. Console SHA-16 `0b25d88fb439d57b`.

## Прогон — `tl-m1-25ms-full-20261018-11-36`

Хост `.11`, PulseLib `2f22c26`, Console `0b25d88f…`. Статус: **запущен**.

| Case | Training | Quality | Длины | Вердикт |
|---|---|---|---|---|
| `W10_HIST_br25_gen` | queued/running | — | — | **in progress** |
| `W10_HIST_br25_nextseg` | queued/running | — | — | **in progress** |
| `W10_HIST_br25_preinh` | queued/running | — | — | **in progress** |
| `W10_HIST_br50_preinh` | queued/running | — | — | **in progress** |

Предыдущий `11-05`: br50 train OK / Test silence; 25 мс застряли в L-oscillation (причина закрыта выше).

## Регрессии по пути (закрыты)

| Симптом | Причина | Фикс |
|---|---|---|
| refuse `failure_reason=3` за ≤6 iter | пустые PeakSeen окна → InvalidPeakNoRecovery | `cb57b08` |
| PeakSeen[2]=0 навсегда после L-step | `EstDelayPerSeg` 0.005→0.15 от sentinel Dissync | `35b805c` + не травить Dissync |
| L=3↔4 stall @25 мс | full invalidate → Active=N−1 каждый ±1 | `b861f8b` scoped reopen |
| L=5↔6 без stop @25 мс | scoped invalidate сбрасывал NoImprove/LastLengthDelta; Dissync length_ok без свежего LastAbsDt | `2f22c26` |

## Сводка

Остров PASS на старом срезе: 25 мс nextseg/preinh. Повтор после фикса роста: `11-36` (M1 затем M0 W04 Step86M в той же tmux-сессии). Дописать fires/Acc по завершении.
