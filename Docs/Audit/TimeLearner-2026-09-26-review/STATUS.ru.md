# Статус аудита TimeLearner Cold 2026-09-26

Дата обновления: 2026-10-08 (SoftCold full49 HEAD).

## Повторная диагностическая выборка (2026-10-08)

Выполнена на отдельном checkout и Linux Console с read-only C++ audit: два положительных контроля и семь выбранных случаев; full49 не повторялась. Отчёт с раздельными полями **сходимость тренера / PostTune-разделимость / детекция на Test**, доказательствами и планом продолжения: [REPEAT_CHECK_RESULT.ru.md](evidence/REPEAT_CHECK_RESULT.ru.md).

Ключевое различие: C++ может штатно завершить обучение (`Need=0`, `TrainingPhase=Done`) с `PostTuneResult=NonSeparable`; это не одно и то же, что отсутствие сходимости. Два PASS-контроля прошли Test gate, несмотря на `NonSeparable` в тренировочном PostTune. Три D-кейса остановлены примерно через 15 минут при `Need=1`, поэтому их дальнейший исход не установлен.

## Повторная классификация full49 и `br25_on` threshold sweep (2026-10-08)

49/49 исторических bundles сопоставлены с provenance и финальными Train/Test артефактами: 26 не достигли PostTune (`Need=1` в лимите), 8 CanonRmin-моделей сошлись, но не прошли quality/detection, отдельно классифицированы 1 Keep и 1 Search/revert FAIL; 12 стандартных PASS и 1 отдельный SoftColdOff PASS. Восьмиточечный C++ threshold sweep готового `br25_on` не нашёл маску `10000000`; цель теряется при пороге, на котором ещё firing два foil. Полный разбор, все категории и ограничения вывода: [SOFTCOLD_FULL49_RECLASSIFICATION.ru.md](evidence/SOFTCOLD_FULL49_RECLASSIFICATION.ru.md).

## SoftCold full49 HEAD (2026-10-07/08)

| | |
|--|--|
| Результат | **49/49 DONE · 13 PASS / 36 FAIL** |
| Console / PulseLib | `18f0ef414b1f9c06` / `dc2866a` · PARALLEL=6 |
| RCS / LOG | [`SOFTCOLD_HEAD_rcs.txt`](../../Bin/Configs/SpikeSamples/StructTrain/_repro/SOFTCOLD_HEAD_rcs.txt) · [`metrics/SOFTCOLD_full_matrix_20261007.log`](evidence/metrics/SOFTCOLD_full_matrix_20261007.log) |
| SNAP / аудит | [`SOFTCOLD_FULL49_SNAP.md`](evidence/SOFTCOLD_FULL49_SNAP.md) · [`SOFTCOLD_CONVERGENCE_AUDIT.ru.md`](evidence/SOFTCOLD_CONVERGENCE_AUDIT.ru.md) |
| История планов | [`SOFTCOLD_RESEARCH_HISTORY.ru.md`](evidence/SOFTCOLD_RESEARCH_HISTORY.ru.md) · копии Cursor [`evidence/plans/`](evidence/plans/) |
| Корзины FAIL | D=20 · E=6 · B=4 · A=3 · N=1 · G=2 |
| Примечание | PASS-набор = rematrix 2026-10-05; AmpNorm DEFERRED не снимался |

## SoftCold / AmpNorm (закрытые кампании)

| Фаза | Статус | Кратко |
|------|--------|--------|
| SoftCold S1+S2 | **done** | фикс + smoke OK |
| SoftCold S3.a+b | **done** | desync lifted; Cold PASS нет |
| SoftCold S3.c/d | **done** | 4 ext + 24 C1+C2; all rc=1 |
| Checkpoint commit | **done** | Bin + Docs gitlinks |
| Amp-norm / EOL investigate | **done** | [AMPNORM_EOL_STUCK.ru.md](evidence/AMPNORM_EOL_STUCK.ru.md) — (a)/(b) + code-map |

**Вердикт SoftCold:** desync **успех**; Cold PASS / NonSeparable / phase6 — **не** тем планом.

## Follow-up remediations (W0–W6)

| WS | Статус | Кратко |
|----|--------|--------|
| **W0** docs/реестры | **done** | SoftCold DEFER→closed; SUCCESSFUL 0 PASS; FAIL_TAXONOMY after_fix 37+diag |
| **W1** AmpNorm(a) TipR mid-band | **done** | keep-slog: NoImprove mid; fix midband→Rmin; fs50 TipR@Rmin; Need=1 → W2 |
| **W2** AmpNorm(b) TipR@Rmin Need=1 | **done** | keep-slog LastAbsDt>SyncTol; `kRminLengthTolFactor=2`; SoftCold asym* **0 PASS** ([SOFTCOLD_W2_ASYM.ru.md](evidence/SOFTCOLD_W2_ASYM.ru.md)) |
| **W3** Phase6 EstDelay | **done** | EstDelay XML → SoftCold L≈gold (не 97); **0 PASS** Need/TipR/gate ([PHASE6_ESTDELAY_FIX.ru.md](evidence/PHASE6_ESTDELAY_FIX.ru.md)) |
| **W4** NonSeparable mid | **done** | SoftCold asym25/br25 **0 PASS**; LandscapeOk не трогали ([A_NONSEPARABLE_MID.ru.md](evidence/A_NONSEPARABLE_MID.ru.md)) |
| **W5** R01/R04 + шапки | **done** | TL-06 headers updated; R01/R04 **blocked: time** ([W5_R01_R04.ru.md](evidence/W5_R01_R04.ru.md)) |
| **W6** final matrix | **done** | 37 RC → **0 PASS**; remediations W1–W4 без Cold PASS ([SOFTCOLD_FINAL_MATRIX.ru.md](evidence/SOFTCOLD_FINAL_MATRIX.ru.md)) |

Harness: `--no-prune` / `--snap-every` / `--keep-slog`. LandscapeOk / Acc / fires **не** ослаблять.

## Closeout

Кампания follow-up W0–W6 **закрыта** 2026-10-01: desync OK; EstDelay L-fix OK; AmpNorm mid→Rmin OK на части кейсов; **Cold SoftCold PASS = 0**. R01/R04 — blocked:time.

## Следующая волна (Working / SoftCold + autosave)

- Реестр: [PROTOCOL_WORKING_VS_LASTCHECK.ru.md](evidence/PROTOCOL_WORKING_VS_LASTCHECK.ru.md) — Working ≠ SoftCold; колонки SoftCold/SoftColdDetail.
- Границы FAIL: [SOFTCOLD_FAIL_BOUNDS.ru.md](evidence/SOFTCOLD_FAIL_BOUNDS.ru.md).
- Model-time autosave / полная SoftCold-матрица — цель `Working=SoftCold` где объективно возможно.

## SoftCold full matrix (после autosave)

- Инвентарь закрыт: [`SOFTCOLD_CANON_INVENTORY.md`](../../Bin/Configs/SpikeSamples/StructTrain/_repro/SOFTCOLD_CANON_INVENTORY.md).
- Очередь: `scripts/softcold_full_matrix.sh` → `metrics/SOFTCOLD_full_matrix.log`.
- PulseLib Branch: зеркало `kRminLengthTolFactor` (AmpNorm b).
