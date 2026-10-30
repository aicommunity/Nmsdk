# F5 CorrectAttenuationGammaForTipR — Span100 LIVE paired cold (2026-10-23)

## Постановка

После tip-noop A/B Span100 ([`F5_GAMMA_SPAN100_2026-10-22.ru.md`](F5_GAMMA_SPAN100_2026-10-22.ru.md)), где Console `f88d1852` / PulseLib `3a599a7` **не** содержали символ `CorrectAttenuationGammaForTipR` и overlay XML был no-op, на tip PulseLib **`9efca9c`** заново посажен F5/A7 (default off; cherry-pick с `6d746ac` конфликтовал с F4-adjacent props, отсутствующими на tip — минимальный UProperty+логика Classic+Branch), собран Console sha256 **`213e70034effa8d7…`**, и повторён **парный** soft-cold **Classic×N1 → Span 100 → AsymRm → PSIoff** на case `W02_CL100_N1_PSIoff`, PostTune **OFF**, W3 **off**, host `.11`, `HOST_LIMIT=8`, `jobs=1`. Цель: закрыть provenance-оговорку «γ не двигает silent, потому что кодpath не активен» и проверить, меняет ли реальный A7 midband TipR / Test на том же case, где H1 уже дал `converged_need0`.

Оверлей очереди: `--train-param CorrectAttenuationGammaForTipR=0|1 --force-posttrain-tuning 0` (канонические inputs не патчились). Без G1 RERUN / F1b / KeepDone / multifactor CL-N1 / правок `matrix.json`.

| Arm | RUN_ID | `CorrectAttenuationGammaForTipR` | `launch.exit` |
|-----|--------|----------------------------------|---------------|
| γ=0 | `F5.S100L.0-11-20261023T040538Z-21224` | **0** | **0** |
| γ=1 | `F5.S100L.1-11-20261023T052744Z-27819` | **1** | **0** |

**Train / Test (канон):**  
[`TimeLearnerMatrix/W02/inputs/W02_CL100_N1_PSIoff/Train`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W02/inputs/W02_CL100_N1_PSIoff/Train) /  
[`…/Test`](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W02/inputs/W02_CL100_N1_PSIoff/Test).

Машиночитаемая сводка: [`F5_GAMMA_SPAN100_LIVE_2026-10-23.tsv`](F5_GAMMA_SPAN100_LIVE_2026-10-23.tsv). Серия: `$REPORTS/F5/span100_live_series.log` → `SERIES_DONE F5.S100L EXIT=0`. Offline-сверка Arm0 vs tip-noop/H1: [`F5_GAMMA_LIVE_OFFLINE_COMPARE_2026-10-23.ru.md`](F5_GAMMA_LIVE_OFFLINE_COMPARE_2026-10-23.ru.md).

## Результаты (Trainer×Mode → Span → NeuronModel → Mod)

**Classic×N1 → 100 ms → AsymRm → PSIoff**, PostTune OFF:

| Arm | Need | L | TipR после Train | test_mid_gap | fires | Acc | Цель | failure_class |
|-----|------|---|------------------|--------------|-------|-----|------|---------------|
| γ=0 | 0 | `54 48 30 1` | `2.880071e6 ×3 + 86e6` | −0.001625 | `00000000` | 7/8 | **нет** | `quality_fail` |
| γ=1 | 0 | `54 48 30 1` | **бит-в-бит ≡ γ=0** | −0.001625 | `00000000` | 7/8 | **нет** | `quality_fail` |

Оба плеча: `training_convergence=converged_need0`, Test `mode=silent`, `target_hit=0`, `detection_quality=target_not_detected`, `separation_quality=fail`. Attempt-local Train XML содержит `<CorrectAttenuationGammaForTipR>0|1</CorrectAttenuationGammaForTipR>`; `run_manifest` фиксирует Console **`213e7003…`**, PulseLib **`9efca9c`**, `strings` Console → символ **present** → кодpath A7 **активен**.

## Сравнение с tip-noop Span100 и H1

| Источник | Console / PulseLib | F5 symbol | γ=0 vs γ=1 | Train / TipR / Test |
|----------|--------------------|----------|------------|---------------------|
| Prior Span100 tip-noop | `f88d1852` / `3a599a7` | **нет** | ≡ silent | Need=0, L=`54 48 30 1`, midband TipR, `quality_fail` |
| **LIVE Span100 (этот cold)** | `213e7003` / **`9efca9c`** | **да** | **≡ silent** | то же |
| H1 baseline | `f88d1852` / `3a599a7` | нет | — | то же Train/TipR/Test |

Live γ=0 **совпадает** с tip-noop γ=0 и H1 по L/TipR/mid/fires — rebuild не сдвинул baseline. Live γ=1 **не** отличается от live γ=0 при активном кодpath.

## Выводы

1. Cold A/B Span100 на Console **с** F5 **выполнен** (`launch.exit=0` обоих); A7 PASS **нет** — оба плеча Need=0 + silent Test `quality_fail`, Acc 7/8 **не** цель.
2. При реальном кодpath **`CorrectAttenuationGammaForTipR=1` по-прежнему no-op** на `W02_CL100_N1_PSIoff` midband относительно γ=0 (бит-идентичные L/TipR/mid/fires).
3. **`DEBT-F5-gamma` остаётся OPEN** как «A7 без PASS / γ noop на midband silent Classic×N1 Span100», уже **не** как «символ отсутствует на tip». Следующий cold по F5 **не** планируется без новой гипотезы (другой case/span или иной механизм mid/TipR); silent Test остаётся на оси **`DEBT-D2-silent-test`**.
4. Provenance-дыра tip-noop Span100 **снята**: повтор на `9efca9c`/`213e7003` подтверждает тот же фенотип при включённом UProperty.

## Infra

| Поле | Значение |
|------|----------|
| Host | `.11` Elder-1, `HOST_LIMIT=8` |
| Lane / ST | main Bin StructTrain (`/home/user/Nmsdk/Bin/.../StructTrain`) |
| Console sha256 | `213e70034effa8d7bcd2b454f0d930edf4bdf39984275fec849bb52b1f88d0cc` |
| PulseLib | `9efca9c` (gitlink; F5 on tip) |
| Bin | `e49a52bf` |
| root at run | `bae546244` |
| SERIES_DONE | `F5.S100L EXIT=0` |
