# M1 карта границ: полный 25 мс, затем br50_preinh

## Метод (исправлен 2026-10-18)

Не формальные «соседи по id». Порядок:

1. Все модификации **@25 мс**: `gen`, `nextseg`, `preinh`.
2. Затем **`br50_preinh`**.
3. FAIL → трасса → фикс (не только ярлык Incomplete).

В матрицу добавлен `W10_HIST_br25_gen` (Bin `2c628a85`).

## Seed (исторический)

`W10_HIST_br25_nextseg` на `.17` / PulseLib `2820738`: **PASS 8/8**, L=`[9,8,5,1]`.

## Прогон после фиксов — `tl-m1-25ms-full-20261018-11-05`

Хост `.11`, PulseLib `b861f8b`, Console `5b91bddb…`.

| Case | Training | Quality | Длины (live/final) | Вердикт |
|---|---|---|---|---|
| `W10_HIST_br25_gen` | running (pulse1 R-tune) | — | ~`[1,5,4,1]` | **in progress** |
| `W10_HIST_br25_nextseg` | running (pulse1 R-tune) | — | ~`[1,6,4,1]` | **in progress** |
| `W10_HIST_br25_preinh` | running (pulse1 R-tune) | — | ~`[1,4,3,1]` | **in progress** |
| `W10_HIST_br50_preinh` | `converged_posttune_finalized` | fires=`00000000` silence / nonseparable | `[11,9,6,1]` | **train OK, quality FAIL** |

Прогресс алгоритма: после scoped reopen Active больше не thrash’ит 2↔3; pulse2 стабильно sync’ится (`synced=[0,0,1,1]`→ дальше). br50 дошёл до полного sync и EOL, но Test молчит — отдельный разбор TipR/mid.

## Регрессии по пути (закрыты)

| Симптом | Причина | Фикс |
|---|---|---|
| refuse `failure_reason=3` за ≤6 iter | пустые PeakSeen окна → InvalidPeakNoRecovery | `cb57b08` |
| PeakSeen[2]=0 навсегда после L-step | `EstDelayPerSeg` 0.005→0.15 от sentinel Dissync | `35b805c` + не травить Dissync |
| L=3↔4 stall @25 мс | full invalidate → Active=N−1 каждый ±1 | `b861f8b` scoped reopen |

## Сводка

Остров PASS на старом срезе: 25 мс nextseg/preinh. На текущем коде с фиксом sync: обучение br50_preinh сходится, качество silence; 25 мс ещё в R-tune на pulse1. Дописать fires/Acc по завершении `11-05`, затем чинить silence br50 при необходимости.
