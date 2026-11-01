# План повторного SoftCold full49 после восстановления cold-start Rs

Дата фиксации: 2026-10-10. Прогоны выполняются на `Elder-1`, непосредственно в `/home/user/Nmsdk`, внутри отдельной `tmux`-сессии. Цель — повторить все 49 SoftCold case ID из `Bin/Configs/SpikeSamples/StructTrain/_repro/SOFTCOLD_QUEUE_manifest.txt` и отдельно зафиксировать ход обучения, качество разделения и детекцию цели.

## Зафиксированная база

- Root на старте: `0469e198904135209b7d56b1d15b5d95d1655048`.
- PulseLib: `2bb72a3b6b28812c7b00382929f7461bc9faff30`.
- Bin harness: `b59a4b2ec55991dc384db6591e1ff2e896d7aae5` (`posttune_verify.py` streaming fix).
- Linux Console SHA-256: `63c348252618ba0d05ed29bdf422c60f58cda5be5a83087f2d8c1367ff83e4ff`.
- Manifest: 49 case ID; SHA-256 `bd6719097279aed04d9fd0ba6ab156833f5f4cf2c2e1cd01cec1c35f8de5bcdf`.
- Метаданные и лог: `evidence/metrics/SOFTCOLD_full_matrix_after_rs_20261010T064000Z.{meta.txt,log}`.
- RCS и shards создаются с новым суффиксом `after_rs_20261010T064000Z` в `_repro/runs`; старые `rcs.d`, RCS, workdir и архивы не переиспользуются.

## Что выявила проверка инфраструктуры

Старый `br100_search` оставил в workdir файл `EventsLog` размером 14,172,336,670 байт и завершился с `rc=137`. В `posttune_verify.py` обнаружено чтение каждого такого файла целиком через `Path.read_text()` в `count_events_mode4()`. Это создавало риск OOM уже при постобработке и могло оставить временный workdir; считать такой исход отказом C++-обучения нельзя. Подсчёт переведён на потоковое чтение строк, изменение проверено `py_compile` и fixture с сохранением прежней семантики счётчика. Тренеры и алгоритмы C++ не менялись.

## Протокол запуска

1. В существующем build-каталоге выполнены configure/build Linux Console и `Test_PulseLib_StorageComponents`; целевой фильтр `TimeLearnerResistanceTest.*` прошёл 6/6.
2. Matrix launcher использует `PARALLEL=6` (4 физических ядра; ранее Branch-прогон получил `rc=137`), `autosave_model_s=10`, `snap_every=20`, `stall_autosave_n=0`. Последний параметр отключает только эвристическую остановку по неизменным длинам/TipR, чтобы доводить случай до терминального C++-исхода или лимита протокола. Штатные отказы тренера и пределы StatisticLog остаются включены.
3. Registry apply отключён до полной сверки (`SKIP_REGISTRY_APPLY=1`); launcher и монитор живут в `tmux`. Потеря SSH-клиента не завершает прогоны.
4. Начальное свободное место — 235 GiB; launcher требует не менее 140 GiB для шести worker. Временные данные не удаляются; размер диска и активных `EventsLog` периодически записывается отдельным монитором.
5. Обучающая логика остаётся в C++; shell/Python применяются только для сборки, запуска, сохранения метаданных, контроля ресурсов и постобработки.

## Классификация итогов

Для каждого case записывать три независимые оси:

- **Сходимость обучения:** `converged_need0` / `converged_posttune_finalized`; `cpp_training_refusal` с C++ phase/reason; `not_converged_at_stop` с указанием timeout/протокольной остановки; либо `insufficient_data`.
- **Качество PostTune:** `separable`, `nonseparable`, setup/timeout/invalid metrics или `not_reached_or_unknown`.
- **Детекция цели:** PASS, `target_not_detected`, другой gate failure, `not_evaluated_training_incomplete` или `insufficient_data`.

`Need=1`, ненулевой launcher RC и gate FAIL сами по себе не считаются объяснением. `rc=137` без C++ training-failure trace относится к аварийному/недостаточному исходу harness/ресурсов до разбора подтверждённой причины. Конечный набор запусков не доказывает математическую невозможность алгоритма.

## После завершения

1. Проверить shards и RCS: 49/49, нет дубликатов/пропусков, сопоставить каждую строку с уникальным run bundle и `provenance.json`.
2. Сверить для всех 49 convergence, C++ refusal phase/reason, `Need`, PostTune result, detection gate, fires/metrics, TipR class, snapshot/reset audit, stdout RC и input hashes. Любые `insufficient_data` выделить явно.
3. Обновить `EXPERIMENTS.md`, `SUCCESSFUL_EXPERIMENTS.md`, `SOFTCOLD_FULL49_SNAP.md`, `SOFTCOLD_CONVERGENCE_AUDIT.ru.md`, `SOFTCOLD_FINAL_MATRIX.ru.md`, `STATUS.ru.md` и связанные указатели/классификации. Registry применять только после этой сверки.
4. Коммитить только streaming fix, plan/report, проверенные docs и нужный root gitlink. Не добавлять `runs/`, `EventsLog`, `StatisticLog`, `rcs.d`, бинарники, metrics logs и старые артефакты. Push не выполнять без отдельной просьбы.
