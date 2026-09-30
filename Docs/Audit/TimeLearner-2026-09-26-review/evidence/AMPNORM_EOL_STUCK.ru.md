# Amp-norm / EOL stuck — классификация и разбор кода

Дата: 2026-09-30.  
План: [AMPNORM_EOL_INVESTIGATE.plan.md](AMPNORM_EOL_INVESTIGATE.plan.md).  
Diagnostic: `metrics/AMPNORM_fs25_noprune.log` · `fs25_gen_20260930T101032Z`.

## Полнота хвостов (вход)

- `DONE_TAILS` 2026-09-30T10:05:51Z · 4 ext + 24 C1+C2 · `missing_count=0` · все `rc=1`
- SoftCold desync снят; здесь только **Need≠0 / EOL**

## Классификация

| case | live TipR | L | Need | класс |
|------|-----------|---|------|-------|
| `fs25_gen` ext/diag | `2e7 2e7 **~3.4–3.5e7** 8.6e7` | ≈gold `6–7 5 4 1` | 1 | **(a) TipR not-at-Rmin** dend2 |
| `asym50/100_*` ext | `2e7×3` (=Rmin) | live growth | 1 | **(b) TipR@Rmin Need=1** |

## Diagnostic fs25 `--no-prune` (DONE)

- Need=1 все **369** polls; NM exit по `-t 640`; slog **7.49 G**; abort 8 G не сработал
- dend2 SNAP: полоса **34.2–35.0 M** весь прогон (freeze #180–320 на `34977812…`)
- Save: TipR `…34199674…`, L=`6 5 4 1`; gate OK, `train_incomplete`
- StatisticLog **стёрт** post-run cleanup → AmpDt traces потеряны (исправлено: `--keep-slog`)

## Разбор кода (`NNeuronTimeLearner.cpp`) — шаг 4 плана

`EndOfLearning` = `AllDendritesSynced() && AllSynapsesNormalized()`; PostTune Need не сбрасывает сразу.

### Gate `AllSynapsesNormalized` (parametric, non-ref dendrites)

Для каждого i∈{0..N-2} Done только если одно из:

1. `amp_ok`: `length_ok && |Initial−MaxAmp|≤kAmpNormEps (1e-5)`
2. `at_r_min && dt_positive && length_ok` (R≤Rmin·(1+1e-6), Initial>MaxAmp+eps)
3. `dead_tip && length_ok && PeakSeen`
4. `oscillation_ok` / `no_improve_done` (NoImprove≥3 + near band / at_r_min)

**fs25 (a):** dend2 R≈3.5e7 ≫ Rmin=2e7 → (2)(4-at_rmin) ложны. Без `amp_ok` EOL блокируется **этим** дендритом.

**asym\* (b):** TipR@Rmin → (2) должен сработать при `dt_positive && length_ok`. Need=1 ⇒ либо `!length_ok` (H3), либо `dt≤eps` при плохом sync/ResistanceStatus, либо `!dt_positive`.

### TipR update — `ChangeSynapseResistanceStatus`

Порядок веток (после `length_settled` / `ready_for_r_tune`):

| ветка | условие | эффект на TipR |
|-------|---------|----------------|
| A | `!ready_for_r_tune` | TipR **не** меняет; только `ResistanceStatus` |
| B | `same_pattern && \|dt\|≤eps` | Done local (`ResistanceStatus=0`) |
| C | **`\|dt\|>5.0`** | **skip TipR update**; Status без изменений |
| D | `eps<\|dt\|≤5` | damped-P / min-step → `ApplyComputedResistance` |
| E | NoImprove≥3 после D | `ResistanceStatus=0` **без** гарантированного EOL |

**Сопоставление с SNAP fs25:** TipR dend2 долго **бит-идентичен** → либо ветка **C** (`|ampDt|>5` pathological skip), либо **A** (`!length_settled` / DendStatus), либо **E** (Status=0 при \|dt\|>eps и не Rmin).  
Dend0/1 дошли до Rmin → r_tune в целом работает; проблема **селективна к dend2**.

Ветка C — главный кодовый кандидат для mid-band freeze: частичный спуск R останавливается, когда \|dt\| становится >5, и R больше не двигается к Rmin → `at_r_min` никогда не открывает Done.

### H-таблица (итог расследования)

| H | Вердикт |
|---|---------|
| H1 mid-band / residual | **(a) подтверждён** empirically; код: ветка C / E |
| H2 NoImprove | возможен (E); traces не пойманы |
| H3 length_ok | главный кандидат для **(b)**; для fs25 слабее (L≈gold) |
| H4 harness wipe | подтверждён; **mitigation: `--keep-slog`** (+ `--no-prune`) |
| H5 softcold tip-1 | снят |

## Вердикт плана AMPNORM

Расследование **закрыто** на уровне классификации + code-map.  
Cold PASS / правка PulseLib **не** входят в этот план (отдельный fix-план).

**Рекомендуемый fix-план (вне scope):**

1. Diagnostic с `--no-prune --keep-slog --snap-every 20`: подтвердить `|dt|>5` / NoImprove на dend2 из traces.
2. Для (a): пересмотреть skip `@|dt|>5` (не оставлять TipR навечно mid-band без escape) **или** best-effort Done при prolonged skip.
3. Для (b): diagnostic asym50 + проверка `DendLastAbsDt` / `length_ok` vs `at_r_min`.
4. LandscapeOk / gate **не** ослаблять.

## Не смешивать

- A_nonseparable, phase6 EstDelay, SoftCold SBM — отдельно / снято.
