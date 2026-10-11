# Расследование сходимости TimeLearner и исторических решений

**Дата среза:** 2026-10-11. **Ветка:** `codex/historical_view`. **Объём:** аудит W01–W04, имеющихся исторических свидетельств и текущей реализации; полный прогон матрицы не выполнялся.

## Выводы на текущем уровне доказательств

1. В сохранённых W01–W04 имеется **32 случая**, а не 24: W03 был опубликован отдельным коммитом Bin. Результат: **4 обучения дошли до `Need=0`, 28 остановлены при `Need=1`, строгих PASS по качеству нет**.
2. Из 28 незавершённых только `W02_CL480_N1_PSIoff` явно классифицирован как `abort_tipr_rmax_stall` при `TipR=Rmax=10^10`. Это подтверждённый отказ по ограничению текущего параметрического режима в этой конфигурации, но не доказательство ошибки реализации или математической невозможности решения.
3. Ещё **24** случая завершили Console с `child_rc=0` при `Need=1`; им был задан `-t` в диапазоне 160–900 условных секунд симуляции. В сохранённых результатах нет явного C++-отказа, однако сами stdout/runtime logs не попали в Git, поэтому нельзя отличить естественное завершение по временному лимиту от другой причины нормального выхода. Три случая — `W02_CL100_N0_PSIoff`, `W02_CL100_N0_PSI25`, `W02_CL480_N0_PSI25` — завершились `child_rc=-15` без установленной причины остановки. Для этих 27 строк причина «алгоритм не может найти решение» не доказана.
4. Два Classic N0 @50 мс сошлись, но оценщик завершился с ошибкой, поэтому качество не измерено. Два Branch N1 PSI-off @25/50 мс сошлись, но получили 7/8 и оба не прошли качество: @25 цель найдена с одним false positive; @50 цель не найдена (`fires=00000000`).
5. Git содержит PHASE5/PHASE8 Train-снимки с `Need=0`. Сильнее этого — исторический отчёт SoftCold-повтора Branch25 от 2026-09-16: B1 soft и B2 strip завершились с `Need=0`, `L=13 11 7 1`; сводка отмечает `REPRO_OK_EXACT` и 8/8. Это свидетельство завершения C++-тренера по архивному runner-отчёту, а не вывод из одной только метрики качества. Сырые Train-логи, workdirs и SHA Console не сохранены, поэтому происхождение неполное. PulseLib pin указан как `780ffc7`; root-срез на 2026-09-15 также закреплял этот PulseLib, а сравнение с root PHASE8 `036006e2` не выявляет изменений исходников вне gitlink Bin. Для PHASE8 доступны точные Train-конфиги на исторических gitlinks; PHASE5 имеет сохранённые Done-снимки, но холодный старт подтверждён слабее.
6. Доказанной общей ошибки реализации, объясняющей массовую несходимость, пока нет. Поэтому исправление алгоритма не вносилось. Не делается вывод о математической невозможности ни одного случая.

## База и происхождение результатов

Исходная рабочая точка расследования: root `48f15a735073d1842db16d398423e8707dce8e94`, PulseLib `2bb72a3b6b28812c7b00382929f7461bc9faff30`, Bin `9acff00938ab247a00cc5e7db4bf4816c5d48e3c`. Чтобы включить уже зафиксированные W03 результаты, локальная ветка Bin `codex/historical_view` передвинута fast-forward до `716c426f382072d0dd28c4e49c4a2c30bbd3bd3d`; изменение root gitlink будет включено в отдельный root-коммит. Все изменения результатов W03 были уже в Git.

| Волна | Run ID | Root / Bin на запуске | PulseLib | Console SHA256 |
|---|---|---|---|---|
| W01 | `run-17-20261011T103939Z-445814` | root `75b4988095efde8ba862ae10f6e7c2f2f246e6a4`; Bin `2f19736dd8523a4ceea45fa999708f541f637b0f` | `2bb72a3b6b28812c7b00382929f7461bc9faff30` | `51da1f19a4414ba56547ece66faef1cbc336c7f1014bf972d8a559c82078f306` |
| W02 | `run-local-20261011T130254Z-1063887` | CL100 все + `CL480_N0_PSI25`: root `aef5b5875b8bd3d2c3b60335f5526972db9e8e27` / Bin `28eec7138f63d8c10801e971509f4d414afbac18`; `CL480_N0_PSIoff`, `CL480_N1_PSIoff`, `CL480_N1_PSI25`: root `d80dfb6d60361aa39a28cc77f28314a5909ee349` / Bin `1dc2e3f41d692aa3c8b9c2119f6dbfe504396edf` | `2bb72a3b6b28812c7b00382929f7461bc9faff30` | `e4df62fb9163d0506d8d7b76b84d2349f1c95314c8923d9c8b698c4fe4c54c5c` |
| W03 | `run-local-20261011T173443Z-1420654` | root `48f15a735073d1842db16d398423e8707dce8e94`; Bin `9acff00938ab247a00cc5e7db4bf4816c5d48e3c` | `2bb72a3b6b28812c7b00382929f7461bc9faff30` | `e4df62fb9163d0506d8d7b76b84d2349f1c95314c8923d9c8b698c4fe4c54c5c` |
| W04 | `run-17-20261011T130050Z-1058954` | root `d80dfb6d60361aa39a28cc77f28314a5909ee349`; Bin `1dc2e3f41d692aa3c8b9c2119f6dbfe504396edf` | `2bb72a3b6b28812c7b00382929f7461bc9faff30` | `51da1f19a4414ba56547ece66faef1cbc336c7f1014bf972d8a559c82078f306` |

Для W02 два набора root/Bin SHA отражают разветвлённое состояние рабочего каталога во время запуска. Сверка Bin `28eec713`→`1dc2e3f4` показывает изменение отчёта `EXPERIMENTS.md` и удаление старых результатов W04, но не изменение конфигураций, скриптов или кода; PulseLib и Console SHA одинаковы. Значит, в сохранённых данных нет признака различия алгоритма или входов между этими двумя ревизиями, однако provenance следует сохранять как per-case, а не сводить к одному SHA.

У всех 32 JSON результата имеются Console SHA, `input_manifest_sha256`, конфигурационный SHA до/после, а также SHA ключевых исходников до/после; кодовые хеши до/после совпадают во всех 32 случаях. Важно: каталог `TimeLearnerMatrix/Wxx/inputs` — это неизменяемый **источник/снимок**, а не точный XML, переданный Console. `worker()` вызывает `posttune_verify.run_case()`, который создаёт отдельную рабочую копию и до запуска выполняет `soft_cold_reset_train()`. В этом helper исходные Done-файлы переводятся в `Need=1`, `DendriteLength=1 1 1 1`, `TipR=86M×4`, нулевой `InitialSomaPotential`, `ResetToUntrainedState=1`, `StructureBuildMode=2` для всех вхождений; Model обрезается до сегмента 1, связи переназначаются на tip-1. Поэтому исходный W04 snapshot с `Need=0`/L=`22 18 11 1` не означает, что именно это состояние обучалось. Runtime config SHA зафиксирован в provenance как `config_sha256`; его содержимое и `cold_reset_contract.json` сохранены в run workdir, но сами workdirs не входят в Git. Трансформацию можно воспроизвести по pinned SHA `posttune_verify.py` / `repro_cold_lib.py`, однако полной пошаговой C++ трассы этих 32 запусков в репозитории нет. `inputs_mutated_during_run=true` обозначает штатное сохранение изменённых C++ параметров в Train-копию и не свидетельствует о мутации скрипта или исходного snapshot.

## Результаты W01–W04

Критерий сходимости здесь — штатное завершение C++ обучения с `Need=0`. `Need=1` в конечном снимке означает только, что к моменту остановки `Need=0` не зафиксирован.

| Случай | Trainer / режим | Need | Итоговая длина | Классификация наблюдения |
|---|---|---:|---|---|
| `W01_CL25_N0_PSIoff` | Classic, структурный, PSI off | 1 | `14 12 1 1` | Недостаточно данных о причине остановки |
| `W01_CL25_N0_PSI25` | Classic, структурный, PSI 2.5 | 1 | `14 11 8 1` | Недостаточно данных о причине остановки |
| `W01_CL25_N1_PSIoff` | Classic, структурно-параметрический, PSI off | 1 | `9 9 1 1` | Недостаточно данных о причине остановки |
| `W01_CL25_N1_PSI25` | Classic, структурно-параметрический, PSI 2.5 | 1 | `9 9 1 1` | Недостаточно данных о причине остановки |
| `W01_CL50_N0_PSIoff` | Classic, структурный, PSI off | 0 | `27 22 15 1` | Сошлось; оценщик завершился ошибкой, качество неизвестно |
| `W01_CL50_N0_PSI25` | Classic, структурный, PSI 2.5 | 0 | `27 22 15 1` | Сошлось; оценщик завершился ошибкой, качество неизвестно |
| `W01_CL50_N1_PSIoff` | Classic, структурно-параметрический, PSI off | 1 | `9 9 1 1` | Недостаточно данных о причине остановки |
| `W01_CL50_N1_PSI25` | Classic, структурно-параметрический, PSI 2.5 | 1 | `9 9 1 1` | Недостаточно данных о причине остановки |
| `W02_CL100_N0_PSIoff` | Classic, структурный, PSI off | 1 | `52 43 30 1` | `child_rc=-15`; причина остановки не установлена |
| `W02_CL100_N0_PSI25` | Classic, структурный, PSI 2.5 | 1 | `52 43 30 1` | `child_rc=-15`; причина остановки не установлена |
| `W02_CL100_N1_PSIoff` | Classic, структурно-параметрический, PSI off | 1 | `17 9 9 1` | Недостаточно данных о причине остановки |
| `W02_CL100_N1_PSI25` | Classic, структурно-параметрический, PSI 2.5 | 1 | `17 9 9 1` | Недостаточно данных о причине остановки |
| `W02_CL480_N0_PSIoff` | Classic, структурный, PSI off | 1 | `53 44 1 1` | Недостаточно данных о причине остановки |
| `W02_CL480_N0_PSI25` | Classic, структурный, PSI 2.5 | 1 | `53 45 28 1` | `child_rc=-15`; причина остановки не установлена |
| `W02_CL480_N1_PSIoff` | Classic, структурно-параметрический, PSI off | 1 | `54 44 1 1` | Явный `abort_tipr_rmax_stall`, TipR достиг `10^10`; ограничение проверенной конфигурации |
| `W02_CL480_N1_PSI25` | Classic, структурно-параметрический, PSI 2.5 | 1 | `33 41 29 1` | Недостаточно данных о причине остановки |
| `W03_BR25_N0_PSIoff` | Branch, структурный, PSI off | 1 | `1 1 4 1` | Недостаточно данных о причине остановки |
| `W03_BR25_N0_PSI25` | Branch, структурный, PSI 2.5 | 1 | `1 13 3 1` | Недостаточно данных о причине остановки |
| `W03_BR25_N1_PSIoff` | Branch, структурно-параметрический, PSI off | 0 | `7 6 4 1` | Сошлось; цель найдена; `fires=10100000`, 7/8, один FP — качество не прошло |
| `W03_BR25_N1_PSI25` | Branch, структурно-параметрический, PSI 2.5 | 1 | `1 13 3 1` | Недостаточно данных о причине остановки |
| `W03_BR50_N0_PSIoff` | Branch, структурный, PSI off | 1 | `1 9 6 1` | Недостаточно данных о причине остановки |
| `W03_BR50_N0_PSI25` | Branch, структурный, PSI 2.5 | 1 | `1 9 6 1` | Недостаточно данных о причине остановки |
| `W03_BR50_N1_PSIoff` | Branch, структурно-параметрический, PSI off | 0 | `15 12 6 1` | Сошлось; `fires=00000000`, 7/8 по совпадениям, цель не обнаружена; качество не прошло |
| `W03_BR50_N1_PSI25` | Branch, структурно-параметрический, PSI 2.5 | 1 | `15 12 6 1` | Недостаточно данных о причине остановки |
| `W04_BR100_N0_PSIoff` | Branch, структурный, PSI off | 1 | `25 21 11 1` | Недостаточно данных о причине остановки |
| `W04_BR100_N0_PSI25` | Branch, структурный, PSI 2.5 | 1 | `22 18 11 1` | Недостаточно данных о причине остановки |
| `W04_BR100_N1_PSIoff` | Branch, структурно-параметрический, PSI off | 1 | `25 21 11 1` | Недостаточно данных о причине остановки; длины совпали с PHASE8 gen snapshot, но Need не достиг нуля |
| `W04_BR100_N1_PSI25` | Branch, структурно-параметрический, PSI 2.5 | 1 | `22 18 11 1` | Недостаточно данных о причине остановки |
| `W04_BR480_N0_PSIoff` | Branch, структурный, PSI off | 1 | `1 41 88 1` | Недостаточно данных о причине остановки |
| `W04_BR480_N0_PSI25` | Branch, структурный, PSI 2.5 | 1 | `1 49 81 1` | Недостаточно данных о причине остановки |
| `W04_BR480_N1_PSIoff` | Branch, структурно-параметрический, PSI off | 1 | `1 1 41 1` | Недостаточно данных о причине остановки |
| `W04_BR480_N1_PSI25` | Branch, структурно-параметрический, PSI 2.5 | 1 | `1 1 41 1` | Недостаточно данных о причине остановки |

W02 long-span cases use canonical Phase6 inputs. W03/W04 use Branch and the mode/PSI variations shown in IDs. The exact matrix factors, `train_t`, input manifests, and per-case file hashes remain in the wave `results.json` files and `EXPERIMENTS.md`.

## Исторические обучающие результаты

### Branch: PHASE8

Root `036006e2a0906766e7c8f3896bd88f52ebca8980` pinned Bin `b93e32439d62ef7006fd3010ff14f99628a36a74` and PulseLib `780ffc7feec4c3561ec049598c896fdde56c8320`. The saved Train configuration for `EXP_br_span25_packA_gen_C1e9` has `IsNeedToTrain=0`, `DendriteLength=13 11 7 1`, `TipSynapseResistance=20M,20M,20M,86M`, `ResistanceMin=20M`, `ResistanceMax=100G`, `NormalizationMode=1`, `SyncTolerance=0.00104167`, `EnableNextSegmentInhibition=0`. Span50/100 were recorded later by root `f7ef51a19d6f66613eb3a8d71ecac4b0a8c0ddca`, pinned to Bin `9ba33d8faaf82a10912ce1b55865d418cb281460` and the same PulseLib `780ffc7feec4c3561ec049598c896fdde56c8320`. In `PHASE8_SHORTSPAN.md`, the 50/100-ms gen cases are recorded at `Need=0` with lengths `13 11 6 1` and `25 21 11 1` respectively; the later PHASE8 table also records preinh cases.

PHASE12 от 2026-09-16 добавляет отдельное свидетельство сходимости: `REPRO_COLD_RESULT.ru.md` фиксирует Branch B1 soft и B2 strip с `Need=0`, одинаковыми `L=13 11 7 1`, 8/8 и `REPRO_OK_EXACT`; `REPRO_COLD_INVESTIGATION.md` указывает, что перед успешным повтором были исправлены отсутствие `ResetToUntrainedState`, преждевременная остановка до `Need=0` и неполная подготовка Test. Поэтому исторический Done сообщён именно для C++ cold-обучения, а TipR@Rmin и ручной выбор тихого порога остаются последующей оценкой качества. Ограничения provenance сохраняются: в Git нет raw Train-лога, workdir и SHA Console. C++-исходники этого сентябрьского среза совпадают с root `036006e2` вне изменений Bin gitlink; PulseLib pin `780ffc7`.

Текущий W04 Branch100 N1 PSI-off начинает с состояния cold reset, растёт до `25 21 11 1`, но сохраняет `Need=1`. В сохранённом PHASE8 Done snapshot те же итоговые длины, но `Need=0`. Значит, различие наблюдается при завершении обучения после достижения того же вектора длин; текущий случай не унаследовал исторически обученные длины. Совпадение конечных длин всё же не доказывает совпадение промежуточного состояния. Это приоритетная пара для повторения: сравнить точные старый и текущий код/конфиг, cold reset, PSI, `EstDelayPerSeg`, TipR и поля EOL, затем сохранить C++-аудит итераций.

### Количественное сравнение Branch100 N1 PSI-off

W04 `BR100_N1_PSIoff` — особенно информативный случай: cold-reset старт (не Done seed), итог `L=25 21 11 1`, но `Need=1` при заданном `-t=640`; конечные TipR=`0.336M, 0.728M, 34.6M, 86M`. PHASE8 Branch100 gen Done snapshot имеет те же длины, `Need=0`, Rmin/Rmax в XML `20M/100G` и TipR=`73.99M, 88.93M, 133.36M, 512.48M`. Текущий runtime для мембранного R=10M использует ratio 1000, то есть эффективные пределы примерно `10k..10G`; старая пара границ была несимметричной относительно Rm и не совпадает с текущей формулой. Следовательно, условия не эквивалентны, а сильное снижение R в W04 может быть связано с изменённым диапазоном или ходом AmpNorm. Без итерационной трассы нельзя установить, стало ли это причиной Need1: сохранённый результат показывает выход процесса с `rc=0`, а не C++ EOL-отказ.

### Classic: PHASE5

Root `ac901c5b5008364341b7710ad1ae9d80fa711420` points to Bin `8aa29289…` and PulseLib `780ffc7feec4c3561ec049598c896fdde56c8320`. Saved Train snapshots for span50/span100 show `Need=0`; the report records lengths `25 23 15 1` and `52 48 27 1`. Exact cold reset provenance and iteration logs were not preserved. TipR@Rmin and quiet-probe threshold are post-training quality steps and must not be treated as the explanation for convergence.

### Other historical campaign summaries

`SOFTCOLD_CONVERGENCE_AUDIT.ru.md` сообщает 0/49 Need0 в full49. Это полезная сводка кампании, но архивные материалы не содержат полную трассу итераций каждого случая. Поэтому они не доказывают, что все 49 случаев алгоритмически неразрешимы, и не позволяют установить причину каждого отказа. Старые SoftCold-кампании также использовали разные критерии и ревизии; их итоговые PASS/FAIL нельзя напрямую сравнивать.

## Изменения C++-алгоритма, которые нужно учитывать в причинном анализе

The source timeline does not yet identify a causal regression, but it bounds plausible comparisons:

| Commit | Change and relevance |
|---|---|
| `f3763f3` (Sep 26) | `kAmpNormEps` changed to double; fixes epsilon truncation in Classic. |
| `17beea0`, `09d37e2`, `bb438c4`, `b29b595` (Sep 30–Oct 1) | TipR no-improve escape and slight `LastAbsDt` tolerance at Rmin; may affect the transition from midband/Rmin to Done. |
| `5308aa5` (Oct 3) | AmpNorm EOL changes in Classic and Branch: Rmin Done, NoImprove step, Rmax dwell. |
| `6e31124` (Oct 3) | Branch changed midband handling; keeps near/far no-improve distinctions. |
| `9b63613`, `b32d715`, `162e7c9`, `c3b0226`, `3cefd64` (Oct 4–7) | Rmax length-escape/W3 behavior and anti-bounce refinements. Relevant only to parametric training with Rmax escape enabled; not an explanation for structural N0 cases. |
| `1ff482c`, `dc2866a` (Oct 8) | Read-only training iteration audit and additional peak-validity gates for EOL. These change observability and gate decisions. |
| `a15f4eb`, `b5229e4` (Oct 8) | Rs/Rm-derived resistance bounds. |
| `2bb72a3` (Oct 9) | Restores configured cold-start Rs instead of forcibly initializing from Rm ratio. |

PHASE8 Train XML uses fixed `ResistanceMin=20M` and `ResistanceMax=100G`; current N1 runtime derives bounds from membrane resistance and default ratios (for Rm=10M: about 10k..10G). This differs historically and deserves a controlled comparison, but cannot explain W01/W02/W04 structural N0 cases where parametric bounds are inactive. Current cold-start restoration also affects N1, but the present W03 N1 Branch has two Need0 cases; thus it is not a universal convergence block.

## Локальные проверки и ограничения воспроизведения

- Current root/PulseLib source was built in Debug and Release with preset `win-vs2019-*-localqt`. Debug Console SHA256: `F16BFDD86B508BEA083692DF9568848BD578869A5298643D9EA60AF3B6C66FEC`; Release Console SHA256: `E24F6E7A52A8308A6D2801686B16D70A4FD77C98644596DB7B255072D2F95C0D`. The first incremental Release link mixed Debug static libraries and failed with CRT-link errors; cleaning only that ignored build preset's outputs and rebuilding all 403 steps succeeded.
- `ctest --test-dir build/win-vs2019-debug-localqt -R '^PulseLib_StorageComponents$' --output-on-failure` passed 1/1 (136.82 sec) after adding Branch cold-reset anchor and Classic/Branch SyncTolerance/PeakMeasureMargin boundary assertions. This validates those contracts; it does not establish a convergence defect.
- Existing C++ read-only training audit emits reset and iteration state including peak validity, lengths, dt, TipR, phase, EOL predicates, Branch active pulse, Need and failure. No new training logic was moved to scripts and no C++ algorithm change is supported by current evidence.
- Four Debug local runs (Classic50 N1, Branch100 N1/N0 and a PHASE8 Branch25 cold seed) produced only an initial iteration during roughly 16 minutes because Debug simulation throughput was too low. They were stopped and are **not results**. First reset/iteration entries show configured initial TipR `86M`; current derived bounds are about `10k..10G` at Rm=10M. No training conclusion can be drawn from those entries.
- A separate historical Release Console was built from root `036006e2a0906766e7c8f3896bd88f52ebca8980`, Bin `b93e32439d62ef7006fd3010ff14f99628a36a74`, and PulseLib `780ffc7feec4c3561ec049598c896fdde56c8320`; binary SHA256 `8A268AB44659FC111DE98D14C320F5E1544495B34B7143D9F87CCC4EBBEF8D79`. The root source at the PHASE8 100-ms record (`f7ef51a19d6f66613eb3a8d71ecac4b0a8c0ddca`) differs from this source pin only by the Bin gitlink. The PHASE8 Branch25 and Branch100 configs are extracted from Bin `b93e3243` and `9ba33d8f` respectively, then given the same scripted cold reset for both old and current code.
- The first historical launch attempt exited with Windows status `0xC0000135` because Qt runtime DLLs were not on PATH. It is not an algorithm result. The replay was restarted with Qt 5.15.2 runtime available; old Branch25 is running. Current Branch25 and Branch100 replays are also running from the same archived XMLs. The initial current audit records `Need=1`, `L=1 1 1 1`, `Rs=86M×4`, no TipR/length change, and no EOL; only the first training iteration has been observed so far. Startup logs say resistance bounds could not be derived before the model settles; the audit later reports the default/derived 10k..10G interval. This requires checking against the complete reset/build trace and is not yet classified as a defect.
- The Release replay is much faster than Debug, but the `-t=320/640` simulation limits remain costly on this workstation. These partial logs are retained only as diagnostics; no `Need=1` before a completed C++/time-limit exit is called a convergence failure. Temporary binaries, workdirs, logs, and runner script are ignored under `temp/` / `_repro` and are not committed.

## Классификация и следующие проверяемые действия

| Класс | Случаи/объём | Решение сейчас |
|---|---|---|
| Подтверждённая ошибка реализации | Нет доказанных случаев в W01–W04 | Не менять тренеры до трассы, показывающей нарушение C++ контракта. |
| Ограничение алгоритма/протокола в проверенных условиях | `W02_CL480_N1_PSIoff`: abort на Rmax; 2 Classic50 N0 и 2 Branch short N1 достигли Need0, но качество отдельно не прошло | Сохранить как конкретное ограничение/результат, без вывода о невозможности решения. |
| Недостаточно данных | Остальные 27 Need1; также причинный разбор разницы PHASE8 vs W04 | Повторить с полными C++ audit логами и точными cold входами; различать C++ отказ, timeout/остановку процесса и Need1 после лимита. |

Рекомендуемый приоритет дальнейшей проверки:

1. Повторить на Release-сборке точный PHASE8 Branch25 gen cold seed на исходном C++ `036006e2` и на текущем C++ `48f15a7`/Pulse `2bb72a3`, с одинаковыми входами и контрольными хешами; после этого повторить аналогичную пару для Branch100 gen, которая сопоставима с W04.
2. На текущем коде повторить `W02_CL480_N1_PSIoff`, сохранив полный C++ audit; проверить, что Rmax abort вызван именно условием в коде и что предшествующие изменения R/длины соответствуют направлению dt. Сверить отдельный тест Classic и Branch для аборт-предиката и Rmax escape.
3. Повторить контрольные случаи Classic50 N0 и Branch25/50 N1 PSI-off на Release, чтобы отделить медленную Debug-сборку от логики и зафиксировать качество отдельно от Need.
4. Добавлять C++-тесты только для контрактов, подтверждённых трассой: границы EOL и валидность пика, TipR направления на Rmin/Rmax, применение роста длины, Branch active pulse/reverse order и anchor после reset. Скрипты остаются только инструментами запуска и анализа.
5. Если исторический C++ Done подтвердится воспроизведением, сравнить первую различающуюся операцию/условие до появления Need0. Если нет — изучить PHASE5/8 рецепты как post-train качество отдельно; их TipR и порог переносить в C++ только после контролируемых абляций. Качество не подменяет критерий сходимости.

Полный запуск матрицы из 294/312 случаев не входит в эту работу. Все выводы ограничены сохранёнными историческими артефактами и текущими волнами W01–W04.
