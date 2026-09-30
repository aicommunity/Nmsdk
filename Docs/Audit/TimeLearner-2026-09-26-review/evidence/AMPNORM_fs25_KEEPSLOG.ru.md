# AmpNorm fs25 keep-slog — подтверждение mid-band

Дата: 2026-09-30.  
Bundle: `fs25_gen_20260930T141150Z` · log: `metrics/AMPNORM_fs25_keepslog.log` ·  
`--train-t 640 --no-prune --snap-every 20 --keep-slog --slog-abort-gib 12`.

## Вердикт

| Гипотеза | Итог |
|----------|------|
| Ветка `\|dt\|>5` skip TipR (L775) | **опровергнута** для fs25: AmpDtTrace dend2 **никогда** `\|dt\|>5` |
| NoImprove → ResSt=0 при TipR mid-band | **подтверждена** — основной механизм stall |
| Amp ≈ Initial при TipR≃3.5e7 | **да** — damped-P осциллирует R вокруг mid, не идёт к Rmin |

## Live SNAP (poll#20+)

| | |
|--|--|
| TipR | `2e7 2e7 **~3.493e7** 8.6e7` |
| L | `6 5 4 1` (gold-like) |
| Need | 1 весь прогон |

## StatisticLog (dend2 = col index 4)

Сэмпл mid (~878k строк TipR ∈ (3.2e7, 4e7)):

| метрика | значение |
|---------|----------|
| AmpDt mid min/med/max | ≈ −1.4e-3 / **−6.6e-5** / 1.3e-2 |
| `\|AmpDt\|>5` | **0** |
| NoImprove mid late | **21** (растёт) |
| ResistanceStatus mid-freeze | **0** на всех ~878k frozen steps |
| LastAbsDt | ≈ 5e-4 (length_ok ok) |
| TipR moves late | ±0.1% осцилляция вокруг ~35.0–35.1M |

## Механика EOL-блока

`AllSynapsesNormalized` для dend2:

1. `amp_ok` — ложь (`\|dt\|` часто > `kAmpNormEps=1e-5`)
2. `at_r_min` — ложь (TipR ≫ 2e7)
3. `no_improve_done` — требует `at_r_min` → ложь
4. `ResistanceStatus=0` после NoImprove≥3 → TipR почти не двигается к Rmin

## Fix (W1.2)

Не «только L775»:

1. `AmpDtSkipCount` + escape clamp-step после K skip при `\|dt\|>5` (defense).
2. **Главное:** при NoImprove≥K и `\|dt\|≤kAmpOscillationBand` и TipR>Rmin — **принудительный шаг к Rmin** (не `ResSt=0`).

## Примечание

StatisticLog **сохранён** (`KEEP_SLOG`, 7.6 G work).  
Итог прогона: Need=1 весь `-t 640`; Save TipR=`2e7 2e7 **~3.42e7** 8.6e7` L=`6 5 4 1`; gate phase9 rc=0 но train_incomplete; tipr_class=other.  
Последний SNAP poll#240: TipR dend2≈`3.428e7` — mid-band до конца.
