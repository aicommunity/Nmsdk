---
name: Cold follow-up remediations
overview: "Follow-up W0–W6: код/конфиги/docs; автокоммиты после каждого завершённого куска; обязательный 10‑мин мониторинг длинных SoftCold/diagnostic. LandscapeOk не ослаблять."
todos:
  - id: w0-docs-registry
    content: "W0: docs/реестры → автокоммит Bin+Docs (gitlinks)"
    status: completed
  - id: w1-ampnorm-a
    content: "W1: fs25 keep-slog (+монитор) → TipR fix → rebuild commit → SoftCold fs* (+монитор) → commit"
    status: completed
  - id: w2-ampnorm-b
    content: "W2: asym50 keep-slog (+монитор) → fix → SoftCold asym* (+монитор) → commit"
    status: completed
  - id: w3-phase6-estdelay
    content: "W3: XML EstDelay → commit; SoftCold phase6×3 (+монитор) → commit"
    status: completed
  - id: w4-nonseparable
    content: "W4: mid research/fix → SoftCold asym25/br25 (+монитор если Train) → commit"
    status: completed
  - id: w5-r01-r04
    content: "W5: R01/R04 (+монитор длинных циклов) → commit шапок/STATUS"
    status: completed
  - id: w6-final-matrix
    content: "W6: матрица 37 RC → SUCCESSFUL+STATUS → финальный commit"
    status: completed
isProject: false
---

# План доработок (максимальная детализация: код / конфиги / документы)

## 0. Словарь


| Термин             | Смысл                                                                                                                               |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| **evidence**       | `Docs/Audit/TimeLearner-2026-09-26-review/evidence/` — отчёты прогонов (не исходники обучалки)                                      |
| **desync снят**    | Рост TipR/L после SoftCold-фикса **стартует**; это ещё не Cold PASS                                                                 |
| **Cold PASS**      | `Need=0` + сохранённые веса + gate Acc/mid OK                                                                                       |
| **Need**           | `IsNeedToTrain` в `Train/Parameters_00.xml`                                                                                         |
| **TipR / Rmin**    | `TipSynapseResistance`; минимум часто `20000000` (`ResistanceMin`)                                                                  |
| **mid-band**       | TipR застрял между cold `86e6` и Rmin (у fs25 dend2 ≈ `3.4–3.5e7`)                                                                  |
| **EOL / amp-norm** | `EndOfLearning` ← `AllDendritesSynced && AllSynapsesNormalized`                                                                     |
| **LandscapeOk**    | `[NNeuronPostTrainTune.h](Libraries/Nmsdk-PulseLib/Core/NNeuronPostTrainTune.h)` L86–99 — foil строго ниже target; **не ослаблять** |
| **bundle**         | `_repro/runs/<case>_<UTC>/` (+ `_work` не коммитить)                                                                                |


Корень StructTrain: `Bin/Configs/SpikeSamples/StructTrain/`.
Orchestrator: `[scripts/posttune_verify.py](Bin/Configs/SpikeSamples/StructTrain/scripts/posttune_verify.py)`.
Соборка: скилл `nmsdk-build`. Коммиты: `nmsdk-gitlinks`.

---

## 0.1 Автокоммиты по мере выполнения (обязательно)

Агент **сам** создаёт git-коммиты после каждого логически законченного куска работы — не ждать конца всего плана и не ждать отдельной просьбы «закоммить», кроме случаев из запретов ниже.

### Когда коммитить (чекпоинты)


| После чего                                      | Что в коммите                                                   | Где репо                         | Пример сообщения                                              |
| ----------------------------------------------- | --------------------------------------------------------------- | -------------------------------- | ------------------------------------------------------------- |
| **W0** docs/реестры готовы                      | EXPERIMENTS, SUCCESSFUL, FAIL_TAXONOMY, STATUS, чеклисты планов | Bin → root Docs+gitlink          | `docs(audit): sync SoftCold registries after DONE_TAILS`      |
| **W1.2** TipR-fix скомпилирован                 | PulseLib `.cpp/.h`                                              | PulseLib → root gitlink          | `fix(TimeLearner): escape TipR skip when |dt|>5 stalls`       |
| **W1.1** keep-slog отчёт написан (код ещё нет)  | только evidence `.md` (не StatisticLog)                         | root Docs                        | `docs(audit): AmpNorm fs25 keep-slog confirm`                 |
| **W1.3** SoftCold fs* прогнаны + строки реестра | EXPERIMENTS/SUCCESSFUL + evidence retest                        | Bin → root                       | `docs(structtrain): SoftCold fs* after TipR mid-band fix`     |
| **W2.2** код asym EOL                           | PulseLib                                                        | PulseLib → root                  | `fix(TimeLearner): …`                                         |
| **W2.3** asym SoftCold                          | Bin реестры + evidence                                          | Bin → root                       | `docs(structtrain): SoftCold asym* after AmpNorm(b)`          |
| **W3** XML EstDelay в 3 EXP                     | только XML (+ короткий PHASE6 doc)                              | Bin → root                       | `fix(structtrain): Phase6 EstDelayPerSeg for SoftCold L≈gold` |
| **W3** retest phase6                            | реестры + PHASE6_ESTDELAY_FIX                                   | Bin → root                       | `docs(structtrain): SoftCold phase6 after EstDelay`           |
| **W4** mid-fix + retest                         | PulseLib и/или gate scripts + evidence A_*                      | соответствующие submodule → root | …                                                             |
| **W5** R01/R04 этап                             | код + status.json + R04 doc                                     | PulseLib/Docs                    | …                                                             |
| **W6** матрица                                  | SOFTCOLD_FINAL_MATRIX + STATUS                                  | Docs (+ Bin если реестры)        | `docs(audit): SoftCold final PASS/FAIL matrix`                |


Правило: **один смысловой коммит на чекпоинт**; не смешивать PulseLib-fix с Bin XML в одном submodule-коммите. Порядок всегда: submodule(s) → root gitlink(s) по скиллу `nmsdk-gitlinks`.

### Как коммитить

- Стиль сообщений репо: `docs(audit):…`, `docs(structtrain):…`, `fix(TimeLearner):…`, `fix(structtrain):…`.
- HEREDOC для `-m`; без `--no-verify` / amend чужих коммитов / `git config`.
- После коммита: `git status -sb`, `git submodule status` для затронутых gitlink.
- Обновить todo workstream → completed только после успешного коммита этого чекпоинта (если коммит обязателен для куска).

### Не коммитить никогда

- `*_work/`, `StatisticLog/`, `EventsLog/`, огромные `archives/statisticlog*`
- `host_metrics.jsonl`, `.partial`, `__pycache__`, secrets
- Грязный overwrite `_repro/POSTTUNE_VERIFY_RESULT.md`, если это только локальный хвост прогона без ценности (по желанию коммитить только если W* явно обновил сводку)

### Push

На remote **не** пушить, пока пользователь явно не попросит.

---

## 0.2 Периодический мониторинг длинных экспериментов (обязательно)

Любой SoftCold / diagnostic / R04 Train с ожидаемым wall **> ~15–20 мин** (практически: `--train-t` ≥ 160 с на тяжёлых кейсах, keep-slog, phase6 `train_t=900`, dual-cycle R04) запускается **только вместе** с мониторами.

### Что включить сразу после старта прогона

1. **Тик статуса каждые 10 минут** (local loop + `notify_on_output` на sentinel), как уже делали для AmpNorm:
  - sentinel: `AGENT_LOOP_TICK_<purpose>` (например `ampnorm_fs25`, `softcold_w1_fs`, `phase6_retest`);
  - на тике агент кратко пишет: poll# / Need / slog GiB / live TipR+L (если есть `posttune_tipr_live.txt`) / жив ли `NeuroModelerConsole` / ETA до slog-abort если `--no-prune`.
2. **Wake на конец** (отдельный watcher, sleep 60 с):
  - срабатывает на `WROTE …POSTTUNE_VERIFY_RESULT`, `ABORT StatisticLog`, исчезновение `posttune_verify.py --case …`;
  - sentinel: `AGENT_LOOP_WAKE_<purpose>_done`;
  - по wake: разобрать итог, обновить evidence/реестр, **остановить оба loop**, затем автокоммит чекпоинта (§0.1).

### Шаблон (bash)

```bash
# status every 10m
while true; do sleep 600
  echo 'AGENT_LOOP_TICK_<purpose> {"prompt":"Краткий статус <case>: poll/Need/TipR/L/slog; при конце — разбор+стоп loops+commit."}'
done

# done wake
LOG=…/evidence/metrics/<run>.log
while true; do
  if grep -qE 'WROTE |ABORT StatisticLog|gate rc' "$LOG" 2>/dev/null; then
    echo 'AGENT_LOOP_WAKE_<purpose>_done {"prompt":"Прогон <case> закончен — разбор, стоп loops, commit чекпоинта."}'
    exit 0
  fi
  pgrep -f 'posttune_verify.py --case <case>' >/dev/null || {
    sleep 5
    echo 'AGENT_LOOP_WAKE_<purpose>_done {"prompt":"posttune_verify <case> исчез — проверить лог, стоп loops, commit."}'
    exit 0
  }
  sleep 60
done
```

### Обязательные прогоны с монитором


| Workstream  | Прогон                                           |
| ----------- | ------------------------------------------------ |
| W1.1        | `fs25_gen` keep-slog `-t 640`                    |
| W1.3        | каждый SoftCold `fs*` (особенно с extended `-t`) |
| W2.1 / W2.3 | `asym50` keep-slog и SoftCold asym*              |
| W3          | каждый `phase6_*` SoftCold (`train_t=900`)       |
| W4          | SoftCold asym25/br25 если Train не skip          |
| W5 R04      | полные dual Train циклы                          |


Короткий docs-only W0 и правки XML без Train — монитор **не** нужен.

### Поведение на тике / конце

- Тик: 3–6 строк статуса пользователю; **не** перезапускать прогон.
- Конец: стоп loops (kill PID тика/wake), дописать evidence, выполнить автокоммит §0.1.
- Если slog → abort threshold при `--no-prune`: на тике явно сказать «приближается abort GiB», не путать с концом диска.

---

## 1. Исходные планы → что закрыто / что нет


| План                                                                           | Закрыто                                                   | Открыто → этот follow-up                 |
| ------------------------------------------------------------------------------ | --------------------------------------------------------- | ---------------------------------------- |
| [cold_audit_fixes](/home/user/.cursor/plans/cold_audit_fixes_e6d3a0e9.plan.md) | P0–P4, eps, harness; DEFER фактически через SoftCold S3.c | R01/R04; шапки реестров; 0 SoftCold PASS |
| SoftCold fix                                                                   | SBM=2 + tip-1 strip; desync снят; S3.c/d done             | Amp-norm, Phase6 EstDelay, mid A         |
| Extended-time                                                                  | 4 P0 прогона (`EXTENDED_TIME_MANIFEST.txt`)               | Stop ×t; чинить код/XML                  |
| AmpNorm investigate                                                            | Классификация (a)/(b) + code-map                          | PulseLib fix + keep-slog confirm         |


RC всех SoftCold after-fix: `[_repro/SOFTCOLD_DEFER_rcs_after_softcold_fix.txt](Bin/Configs/SpikeSamples/StructTrain/_repro/SOFTCOLD_DEFER_rcs_after_softcold_fix.txt)` — **37** строк, **0× rc=0**.

---

## 2. Карта конфигов SoftCold (`CASES` в posttune_verify)

Определение кейсов: `[posttune_verify.py` ~L76–230](Bin/Configs/SpikeSamples/StructTrain/scripts/posttune_verify.py).


| case id                          | Archive root (Train/Test)                                                  | train_t | span | kind → gate         |
| -------------------------------- | -------------------------------------------------------------------------- | ------- | ---- | ------------------- |
| `fs25_gen`                       | `SelectivityFastSpan/EXP_span25ms_fast_C1e9`                               | 160     | 25   | asym → phase9       |
| `fs25_preinh`                    | `…/EXP_span25ms_fast_preinh_C1e9`                                          | 160     | 25   | phase9              |
| `fs50_preinh`                    | `…/EXP_span50ms_fast_preinh_C1e9`                                          | 320     | 50   | phase9              |
| `fs100_gen` / `fs100_preinh`     | `…/EXP_span100ms_fast[_preinh]_C1e9`                                       | 640     | 100  | phase9              |
| `asym25_preinh`                  | `SelectivityAsymRm/EXP_span25ms_packA_preinh`                              | 160     | 25   | phase9              |
| `asym50_preinh`                  | `…/EXP_span50ms_packA_preinh`                                              | 640     | 50   | phase9              |
| `asym100_gen` / `asym100_preinh` | `…/EXP_span100ms_packA_{gen,preinh}`                                       | 640     | 100  | phase9              |
| `br25_on`                        | `SelectivityBranch/EXP_br_span25_packA_gen_C1e9_posttune` (gold packA gen) | 320     | 25   | **branch → phase8** |
| `phase6_thr_only`                | `SelectivityPhaseA/Phase6/EXP_480_gen_thr_only`                            | 900     | 480  | phase9              |
| `phase6_preinh250`               | `…/EXP_480_preinh250_tiprmin`                                              | 900     | 480  | phase9              |
| `phase6_ltzcal_twin`             | `…/EXP_480_ltzcal_twin_gen`                                                | 900     | 480  | phase9              |
| C2 ltz/pa/psi/tn                 | см. `CASES` L207+                                                          | …       | …    | phase9              |


Gates:

- Asym/FastSpan/Phase6: `[SelectivityAsymRm/scripts/phase9_preinh_bc_gate.py](Bin/Configs/SpikeSamples/StructTrain/SelectivityAsymRm/scripts/phase9_preinh_bc_gate.py)` (`--skip-tipr-mid` часто включён из case).
- Branch: `[SelectivityBranch/scripts/phase8_tiprmin_gate.py](Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/scripts/phase8_tiprmin_gate.py)`.

Harness SoftCold reset: `[scripts/repro_cold_lib.py](Bin/Configs/SpikeSamples/StructTrain/scripts/repro_cold_lib.py)` — `soft_cold_reset_train`, SBM=2 all, tip-1 strip (`softcold_fix=2026-09-27_sbm2_strip_tip1`).

Уже есть CLI диагностики (Bin `2beab6c`):

- `--train-t`, `--max-polls`
- `--no-prune`, `--snap-every N`, `--slog-abort-gib`
- `--keep-slog` — не удалять `Train/StatisticLog` после case ([~L1420–1427](Bin/Configs/SpikeSamples/StructTrain/scripts/posttune_verify.py))

Трассировки, которые harness уже читает: `TipSynapseResistanceTrace`, `DendriteLengthTrace`.
Для W1/W2 дополнительно смотреть в StatisticLog (если пишутся): `NoImproveResistanceTrace`, amp/ResistanceDifference / AmpDtAudit в NM log при `EnableDebug=1`.

---

## 3. Код PulseLib — точки правок по workstream

### 3.1 Amp-norm (W1 / W2) — classic learner

Файл: `[Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearner.cpp](Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearner.cpp)`
Заголовок констант: `[NNeuronTimeLearner.h](Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearner.h)` (`kAmpNormEps=1e-5` double уже; `kNoImproveResistanceLimit=3`; `kDelayPerSegDefault=0.005`).


| Символ                          | Примерно         | Роль                                                                   |
| ------------------------------- | ---------------- | ---------------------------------------------------------------------- |
| `ChangeSynapseResistanceStatus` | L680–854         | Обновление TipR / `ResistanceStatus`                                   |
| ветка `|dt|>5.0` **skip TipR**  | **L775–788**     | Главный кандидат mid-band freeze (a)                                   |
| damped-P + min-step             | L792–846         | Нормальный amp-tune                                                    |
| NoImprove → Status=0            | L825–841         | Кандидат stall без Done                                                |
| `AllSynapsesNormalized`         | L3484–3580       | EOL amp gate (amp_ok / at_r_min / dead_tip / oscillation / no_improve) |
| `AllDendritesSynced`            | L3446–3481       | EOL length gate (`DendLastAbsDt` / BestEffort)                         |
| `EndOfLearning`                 | L3583+           | Совместный Done → Save/`Need=0`                                        |
| `DelayLenOf` / EstDelay         | L970–975, L3169+ | Phase6 length (W3)                                                     |
| `ComputeDampedTipResistance`    | L551–598         | Не трогать без нужды                                                   |


Зеркало Branch (если кейс Branch или общий баг):
`[NNeuronTimeLearnerBranch.cpp](Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearnerBranch.cpp)` — те же ветки TipR / `AllSynapsesNormalized` (искать `fabs(dt) > 5.0`).

PostTune / mid (W4):
`[NNeuronPostTrainTune.h](Libraries/Nmsdk-PulseLib/Core/NNeuronPostTrainTune.h)` — `LandscapeOk` L86–99, `kResultNonSeparable=2`.
Реализацию mid/inference смотреть в `NNeuronPostTrainTune.cpp` + Analyzer; gate читает mid через phase8/9.

### 3.2 Жёсткий выбор фикса W1 (после confirm traces)

**Подтверждение:** если на dend2 при TipR≈3.5e7 стабильно `|Initial−MaxAmp|>5` и TipR не меняется → виновата ветка L775–788.

**Правка (зафиксировать в плане исполнения):** не оставлять вечный skip:

1. Счётчик `AmpDtSkipCount[dend]` (++ на входе в L775; reset при реальном ApplyComputedResistance).
2. При `AmpDtSkipCount >= K` (начать с K=3, как NoImprove): **не** skip — либо безопасный clamp-step к Rmin при `dt>0`, либо existing `no_improve_done` / `at_r_min` escape после принудительного шага.
3. Лог `AmpDtAudit` при EnableDebug оставить.
4. Unit: расширить комментарий/док-контракт в evidence; C++ static path — ручная проверка на SoftCold + optional harness assert live TipR.

**Не делать в W1:** менять `kAmpNormEps`, LandscapeOk, Acc/fires, soft-cold SBM.

Сборка после правки:

```bash
cmake --build build/linux-gcc-debug-local \
  --target Nmsdk-PulseLib.core NeuroModelerConsole -j"$(nproc)"
sha256sum Bin/Platform/Linux/NeuroModelerConsole
```

Коммит: PulseLib → root gitlink PulseLib (отдельно от Bin docs).

---

## 4. Workstreams с файлами / командами / документами

### W0 — Документы и реестры (без Train)

**Документы планов (чеклисты устарели):**

1. `[evidence/SOFTCOLD_FIX_THEN_RETEST.plan.md](Docs/Audit/TimeLearner-2026-09-26-review/evidence/SOFTCOLD_FIX_THEN_RETEST.plan.md)` L104–109 → `[x]` S3.c/d, commit, AmpNorm; статус **done (desync; no Cold PASS)**.
2. `[evidence/RETEST_EXTENDED_TIME.plan.md](Docs/Audit/TimeLearner-2026-09-26-review/evidence/RETEST_EXTENDED_TIME.plan.md)` — статус **done**; §5 checklist; вывод «stop extended → AmpNorm W1/W2».
3. `[STATUS.ru.md](Docs/Audit/TimeLearner-2026-09-26-review/STATUS.ru.md)` — таблица W0–W6 open/done.

**Реестры Bin:**

1. `[EXPERIMENTS.md](Bin/Configs/SpikeSamples/StructTrain/EXPERIMENTS.md)` секция **L257+** `## SoftCold wave C DEFER` — убрать «остаток в очереди»; для каждого case из RC: bundle, `failure_class`, subtype, live TipR/L если известны; extended/diag runs:
  - `fs25_gen_20260928T065707Z`, `fs25_gen_20260930T101032Z`
  - `asym50_preinh_20260928T085626Z`, `asym100_preinh_20260928T154111Z`, `asym100_gen_20260928T222626Z`
2. `[SUCCESSFUL_EXPERIMENTS.md](Bin/Configs/SpikeSamples/StructTrain/SUCCESSFUL_EXPERIMENTS.md)` L278 / L301 — SoftCold after-fix: **0 PASS**; провалы со ссылкой на `SOFTCOLD_PLAN_RESULT.md`.
3. Шапка обоих файлов (TL-06): `Console SHA · PulseLib · Bin · date` (сейчас Console SoftCold: `ec86430e…` до W1 rebuild).

**Таксономия:**

1. Скрипт `[evidence/metrics/refresh_fail_taxonomy_after_fix.py](Docs/Audit/TimeLearner-2026-09-26-review/evidence/metrics/refresh_fail_taxonomy_after_fix.py)` → перезаписать `[FAIL_TAXONOMY.json](Docs/Audit/TimeLearner-2026-09-26-review/evidence/FAIL_TAXONOMY.json)` по всем 37 RC + diag; asym50/100 after-fix **не** `B_tipr_frozen_cold`.
2. При необходимости абзац в `[SOFTCOLD_PLAN_RESULT.md](Docs/Audit/TimeLearner-2026-09-26-review/evidence/SOFTCOLD_PLAN_RESULT.md)` / ссылка на этот follow-up plan.

**Коммит:** Bin (EXPERIMENTS/SUCCESSFUL) + root Docs; без `_work`, без `host_metrics.jsonl`, без `.partial`.

---

### W1 — fs25 TipR mid-band (код + конфиг прогона + evidence)

**Конфиг кейса:** archive `SelectivityFastSpan/EXP_span25ms_fast_C1e9`; default `train_t=160`; diagnostic/extended уже использовали `-t 640`.
Типичные XML после soft-cold: `ResistanceMin=2e7`, `EnableDebug=1`, cold TipR `86e6×4`, L=`1 1 1 1`.
Эталон длины после роста: ≈ `6 5 4 1` (gold-like).

**W1.1 Confirm (до правки кода)**

Сразу после старта: включить §0.2 — тик **каждые 10 мин** + wake на конец (`AGENT_LOOP_TICK_ampnorm_fs25` / `AGENT_LOOP_WAKE_ampnorm_fs25_done`). Без монитора прогон не оставлять.

```bash
cd /home/user/Nmsdk
python3 -u Bin/Configs/SpikeSamples/StructTrain/scripts/posttune_verify.py \
  --case fs25_gen --train-t 640 --max-polls 801 \
  --no-prune --snap-every 20 --keep-slog --slog-abort-gib 12 \
  | tee Docs/Audit/TimeLearner-2026-09-26-review/evidence/metrics/AMPNORM_fs25_keepslog.log
```

Артефакты:

- work: `_repro/runs/fs25_gen_<UTC>_work/Train/StatisticLog/**`
- live snaps: `Train/posttune_tipr_live.txt`
- новый отчёт: `evidence/AMPNORM_fs25_KEEPSLOG.ru.md` — таблица dend2: TipR, |dt|, NoImprove, DendLastAbsDt, resistanceStatus по времени; вывод «ветка L775 да/нет».
- После отчёта: **автокоммит Docs** (§0.1); loops остановить.

**W1.2 Код** — §3.1–3.2 выше; правка classic (+ Branch mirror если тот же код).

**W1.3 Retest SoftCold**

```bash
python3 …/posttune_verify.py --case fs25_gen
# при том же mid-band симптоме на соседних:
python3 …/posttune_verify.py --case fs25_preinh
python3 …/posttune_verify.py --case fs50_preinh
python3 …/posttune_verify.py --case fs100_gen
python3 …/posttune_verify.py --case fs100_preinh
```

Критерий успеха W1: `Need=0` **или** live TipR dend2 ≤ Rmin·(1+ε) и дальнейший путь в `AllSynapsesNormalized`; gate может ещё FAIL по mid — тогда это уже корзина A, не (a).
Обновить `[AMPNORM_EOL_STUCK.ru.md](Docs/Audit/TimeLearner-2026-09-26-review/evidence/AMPNORM_EOL_STUCK.ru.md)` секцией «после фикса».
Не трогать в W1: asym25, br25, phase6.

---

### W2 — asym* TipR@Rmin но Need=1

**Конфиги:**


| case                             | archive                                       | EstDelayPerSeg в Train XML |
| -------------------------------- | --------------------------------------------- | -------------------------- |
| `asym50_preinh`                  | `SelectivityAsymRm/EXP_span50ms_packA_preinh` | обычно `0.002`             |
| `asym100_preinh` / `asym100_gen` | packA preinh/gen                              | `0.002`                    |


Эталон live после fix SoftCold: TipR `2e7×3 8.6e7`, L≈`29 22 15 1` (50 ms) / ≈`52 43 30 1` (100 ms).
Проблема: XML часто flat (нет Save при Need=1) — смотреть **live**/traces, не только Parameters.

**W2.1 Diagnostic**

```bash
python3 …/posttune_verify.py --case asym50_preinh \
  --train-t 640 --max-polls 801 \
  --no-prune --snap-every 20 --keep-slog --slog-abort-gib 12
```

Разбор traces + сверка с `AllSynapsesNormalized` L3491–3550:

- `length_ok` = `DendLastAbsDt[i]≤SyncTolerance` OR `DendBestEffortSynced[i]`
- `at_r_min` + `dt_positive`
- pending `ResistanceStatus[i]`
- `AllDendritesSynced` (PeakValid / BestEffort)

Документ: `evidence/AMPNORM_asym50_KEEPSLOG.ru.md`.

**W2.2 Код (по результату traces — один фактор)**


| Находка                               | Куда править                                                                                             |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `!length_ok` при L≈gold               | sync path / `DendLastAbsDt` refresh / BestEffort (`NNeuronTimeLearner.cpp` length settle ~L688+, L3353+) |
| все флаги Done true, но функция false | баг цикла `AllSynapsesNormalized` / ref index N-1                                                        |
| `ResistanceStatus` вечно 1            | ApplySynapseResistanceChange / NoImprove                                                                 |
| `!dt_positive` (amp > Initial)        | ветка знака dt в ChangeSynapseResistanceStatus                                                           |


**W2.3 Retest**

```bash
python3 …/posttune_verify.py --case asym50_preinh
python3 …/posttune_verify.py --case asym100_preinh
python3 …/posttune_verify.py --case asym100_gen
```

Без нового ×1280, пока EOL-gate не чинится. Обновить EXPERIMENTS строки asym* + STUCK doc.

---

### W3 — Phase6 EstDelay vs span 480

Уже разобрано в `[TIMING_SPAN_MISMATCH.ru.md](Docs/Audit/TimeLearner-2026-09-26-review/evidence/TIMING_SPAN_MISMATCH.ru.md)`:

- Archive **без** тега `EstDelayPerSeg` → runtime default `**0.005` с** (`kDelayPerSegDefault`).
- SoftCold L=1 → равновесие `1 + 0.480/0.005 ≈ 97` ≈ факт SoftCold конца.
- Gold в archive: L≈`49 41 25 1` / `51 43 25 1` — **не** совпадает с naive span/EstDelay.

**Конфиги (править Train XML архивов SoftCold-source):**


| case                 | путь Parameters                                                         | Действие                                          |
| -------------------- | ----------------------------------------------------------------------- | ------------------------------------------------- |
| `phase6_thr_only`    | `SelectivityPhaseA/Phase6/EXP_480_gen_thr_only/Train/Parameters_00.xml` | **добавить** `<EstDelayPerSeg>…</EstDelayPerSeg>` |
| `phase6_preinh250`   | `…/EXP_480_preinh250_tiprmin/Train/…`                                   | то же                                             |
| `phase6_ltzcal_twin` | `…/EXP_480_ltzcal_twin_gen/Train/…`                                     | то же                                             |


Расчёт one-factor (зафиксировать в отчёте):
`EstDelayPerSeg ≈ span_eff / (L_gold[0]−1)`.
Для gold L0=49 и эффективной задержки ~240 мс (половина span, как в TIMING doc): `0.240/48 = 0.005` — это как раз default и даёт runaway; для сходимости к gold 49 нужна **другая** модель needed/delay (см. TIMING §2) **или** явный EstDelay согласованный с тем, что learner считает `needed` из паттерна.

Практический one-factor из TIMING рекомендаций:

1. Выставить в XML `EstDelayPerSeg` так, чтобы SoftCold L сходился к gold (±tol), **или**
2. Документировать и править формулу needed vs span (код DelayLenOf / ApplyPending) — только если XML-подбора недостаточно.

Не трогать: SoftCold SBM strip, LandscapeOk, MaxDendriteLength=100 как «лечение».

**Документ:** дополнить TIMING или новый `evidence/PHASE6_ESTDELAY_FIX.ru.md` (до/после L, TipR, Need).

**Retest:**

```bash
python3 …/posttune_verify.py --case phase6_thr_only
python3 …/posttune_verify.py --case phase6_preinh250
python3 …/posttune_verify.py --case phase6_ltzcal_twin
```

Extended `-t` на phase6 **не** открывать, пока L не упирается в gold-окрестность.
Коммит Bin: XML EXP + EXPERIMENTS phase6 строки.

---

### W4 — NonSeparable mid (asym25 / br25)

**Факт:** Train Done (`Need=0`, tipr=canon), gate FAIL — корзина A.
Bundles-ориентиры: `asym25_preinh_20260927T172618Z`, `br25_on_20260927T173802Z` (+ [P4_br25_B1.md](Docs/Audit/TimeLearner-2026-09-26-review/evidence/P4_br25_B1.md)).

**Код / скрипты (только исследование → точечный патч):**


| Компонент             | Путь                                                          |
| --------------------- | ------------------------------------------------------------- |
| LandscapeOk           | `NNeuronPostTrainTune.h` L86–99                               |
| PostTune mid / Result | `NNeuronPostTrainTune.cpp`                                    |
| Gate asym             | `phase9_preinh_bc_gate.py` (`--skip-tipr-mid`, inference mid) |
| Gate branch           | `phase8_tiprmin_gate.py`                                      |
| Case tags TipRMode    | `posttune_verify.py` TipRMode map: `br25_on→1`, default Canon |


**Запрет:** снижать eps LandscapeOk; менять Acc/fires ожидания; крутить `--train-t`.

**Документ:** `evidence/A_NONSEPARABLE_MID.ru.md` — mid silent vs NonSeparable, foil gaps, нужен ли Analyzer/wiring.
**Retest** только после гипотезы+патча: `--case asym25_preinh`, `--case br25_on`.

---

### W5 — R01 / R04 + шапки реестров

Из `[PLAN.ru.md` §9](Docs/Audit/TimeLearner-2026-09-26-review/PLAN.ru.md) и cold_audit Phase 6:

**R01 (код Dataset/Analyzer, не SoftCold):**

- Файлы: `[NDatasetBase.cpp/.h](Libraries/Nmsdk-PulseLib/Core/NDatasetBase.cpp)`, `[NPatternResponseAnalyzer.cpp/.h](Libraries/Nmsdk-PulseLib/Core/NPatternResponseAnalyzer.cpp)` — production wiring, не probe stubs.
- Инструментация: sample id, stimulus/response timestamps, expected count, incomplete/censored, closing event.
- Сценарии: advance до конца старого паттерна; смена sample без stimulus edge; coincident sample/stimulus.
- Статус: `[Docs/Audit/TimeLearner-2026-09-24-review/status.json](Docs/Audit/TimeLearner-2026-09-24-review/status.json)` ключ `R01`.

**R04:**

- Два полных Train→PostTune→Test на одном объекте: classic TL + Branch.
- Проверить сброс `PostTuneResult`, metrics, flags, mid; второй цикл не наследует Success первого.
- Evidence: `evidence/R04_dual_cycle.ru.md` + два bundle.

**Документы:**

- Шапки `[EXPERIMENTS.md](Bin/Configs/SpikeSamples/StructTrain/EXPERIMENTS.md)` L3 и `[SUCCESSFUL_EXPERIMENTS.md](Bin/Configs/SpikeSamples/StructTrain/SUCCESSFUL_EXPERIMENTS.md)` L3.
- `[README.md](Docs/Audit/TimeLearner-2026-09-26-review/README.md)` / PLAN статус Phase 6.
- Нет времени → в STATUS явно `blocked: time` (не «DEFER без причины»).

---

### W6 — Финальная матрица

1. Таблица всех case из RC-файла (37) → PASS / A / AmpNorm(a|b) / Phase6 / other; колонки: bundle, Console SHA, Need, TipR live, L, gate_rc, failure_class.
2. Файл: `evidence/SOFTCOLD_FINAL_MATRIX.ru.md` (+ обновить FAIL_TAXONOMY).
3. SUCCESSFUL — только реальные PASS строки.
4. STATUS: критерии cold_audit 1–6 + AmpNorm/Phase6/mid/R01–R04.

---

## 5. Порядок исполнения

1. **W0** docs/registry → **автокоммит**
2. **W1.1** keep-slog fs25 **+ монитор 10 м / done-wake** → отчёт → автокоммит Docs
3. **W1.2** PulseLib TipR skip-fix → rebuild → **автокоммит PulseLib+gitlink**
4. **W1.3** SoftCold fs* **+ монитор** → реестр → **автокоммит**
5. **W2** asym keep-slog **+ монитор** → fix → SoftCold **+ монитор** → **автокоммиты** по чекпоинтам
6. **W3** XML EstDelay → коммит → SoftCold phase6 **+ монитор** → коммит
7. **W4** mid (монитор если Train) → коммит
8. **W5** R01/R04 (монитор длинных циклов) → коммит
9. **W6** матрица → **финальный автокоммит**

Параллель Train ≤1–2. Без монитора длинный Train **не** оставлять «в фоне вслепую».

---

## 6. Критерии готовности

1. W0: нет текста «DEFER ещё в очереди»; taxonomy согласована; **есть коммит** чекпоинта.
2. W1: fs25 не mid-band stall **или** keep-slog отчёт + патч; diagnostic/retest шли **с монитором**; коммиты PulseLib + retest docs сделаны.
3. W2: asym50 `Need=0` **или** code pointer + traces; монитор на длинных прогонах; коммиты на месте.
4. W3: SoftCold phase6 L≈gold **или** blocked в PHASE6 doc; монитор на retest; XML+результаты закоммичены.
5. W4: mid PASS или A_NONSEPARABLE_MID с rootcause; коммит после этапа.
6. W5: R01/R04 done или `blocked: time`; коммит.
7. W6: матрица + STATUS;89 финальный коммит.
8. LandscapeOk / Acc / fires не ослаблены; `_work`/StatisticLog не в git; **push только по просьбе**.
9. Процесс: ни один длинный прогон W1–W5 не завершён без тиков статуса и done-wake.

