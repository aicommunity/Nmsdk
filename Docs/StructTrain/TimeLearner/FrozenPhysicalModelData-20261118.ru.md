# Замороженное выполнение полной physical DATA-модели

Статус: реализация и native fixtures подготовлены; серверная проверка ещё
не выполнена. Это продолжение этапов5/6, не закрытие этапа и не научный
результат. Работающие задания на Root445/Pulsec54 и Windows Root03d/Pulsec54
не обновляются. При потере VPN их исходы остаются неизвестными до readback.

## Задача

Полный source/proof import повторно разбирает историю поиска и первичные
измерения перед каждой оценкой. В текущем диагностическом запуске подготовка
до native Console заняла около13 минут. Новый physical DATA export отделяет
полный граф/storage/Dataset от истории, сохраняя ссылку на исходную границу.
Теперь добавлен native путь установки такого графа для замороженных проб.
Измеренное ускорение или снижение RSS пока не заявляется.

## Контракт компонентов

Оба learner предоставляют ImportNativePhysicalModelData,
ExportNativePhysicalModelData, HasNativePhysicalModelData. Для проб применяется
прежний QueueNativeRecognitionTrial, штатный scheduler, его reset policy,
полные окна и существующие наблюдения Soma/LT/input/spikes. Нового Calculate
или вложенного расчёта нет; Build/Calculate/Reset bool не используются для
передачи ошибок. Результат импорта — NativeModelBuildResult и диагностика.

```text
validated source recognition boundary
    -> full physical model DATA export
    -> native Dataset + neuron + storage images import
    -> verify effective graph, banks, threshold and model revision
    -> existing shared frozen owner commit boundary
    -> native initialization/reset
    -> existing full-pattern recognition trial executor
    -> complete observations and unchanged frozen model
```

PrepareNativeFrozenPhysicalModelData требует recognition boundary: обычную,
diagnostic, threshold candidate либо calibrated. Solo DATA не преобразуется
автоматически; прежде требуется явный Solo→Recognition Convert. Все input banks
должны быть подключены. Порог в metadata должен совпадать с Threshold реального
LTZone. Родительские overlays и восстановление по defaults не применяются.

InstallNativeFrozenState выделен из существующего recognition owner helper.
Для прежнего API его factory вызывает прежний proof importer; DATA factory
вызывает новый physical importer. Условия idle boundary, native commit,
owner mirrors, order, readback и обработка ошибок после commit сохранены.
Целые физические дети импортируются сразу с индивидуальными параметрами;
cold reconstruction/InitializeNativeOwnedModel к обученному графу не применяется.

## Границы статусов и владения

- Native training service после DATA import — Idle, без certificate и search
  authority. CalibrationConfirmed всегда false, даже для calibrated source.
- Экспорт через прежний recognition proof API отвергается. DATA возвращается
  своим API после полной проверки frozen hold.
- BeginNativeTraining не запускается поверх frozen hold. Нельзя заменить
  модель при queued/running trial или войти через DATA в owned finalization.
- Старые solo C-control/finalization records не переходят на новый hold;
  физические индивидуальные C остаются частью импортируемого графа.
- Legacy TrainingPhase не объявляет Done. Данные исходного сертификата в
  metadata остаются provenance DATA и не становятся сертификатом Test-модели.
- Выбор порога и другие изменения физики требуют отдельного явного пути;
  импорт не преобразует модель и не применяет conversion повторно.

## Подготовленная проверка

В Test_PulseLib_PhysicalModelData.cpp добавлены три native случая:

1. Classic: два независимых owner — прежний full-source diagnostic import
   и новый DATA import. Один target и один foil, полные окна0.4с/2000Hz,
   native reset-per-trial. Сверяются полные observation JSON, кроме run_id:
   все отсчёты Soma/LT/input, события, completeness, validity и revisions.
2. Та же проверка Branch с реально включёнными входами recognition-графа.
3. Solo DATA и противоречивая заново подписанная threshold metadata
   отвергаются; исходная модель не меняется.

В первых двух случаях отдельно проверяются запрет training/proof export,
сохранность DATA hash и отказ от замены во время queued trial. При заданном
TIMELEARNER_EXECUTION_OUTPUT пишутся полные JSON/CSV для читаемых временных
графиков. Это cold N2/asymmetric fixture, не обучение или классификация N4.

К исходным228 Linux/227 Windows cases добавляются3 новых и16 прежних
регрессий изменённого общего пути: NativeThresholdPotential (4),
NativeCalibrationPersistence (2), NativeDiagnosticThreshold (2),
NativeCalibrationOwnership (8). Ожидается247 Linux/246 Windows cases.
Состав должен быть сверён production inventory и compiled gtest list;
статический перечень не считается выполнением.

[Точные IDs и Git blob hashes](ValidationPlans/FrozenPhysicalModelData-20261118/INVENTORY.json):
Root `543c77e2027e19d425045be8039a8b07baa81bd2`, Pulse
`5f8b281fc1d679ae7927f7ad7410d3ff675a522a`.14 CPP source files,
247/246 IDs, source hashes8 изменённых Pulse files. Worker job ещё не создан.

## Оставшаяся приёмка этапа5

Нужны сборка и actual native gate, реальная обученная/converted/calibrated
модель из опытов, неоднородная физика/C-trim, новый процесс и все8 паттернов.
Console DATA-evaluation entry point и корневой runner добавлены в следующей
подготовленной реализации ниже. Source-boundary resolver опубликованного
исходного корпуса ещё необходим. Публикация сохраняет оригинальные
данные и экспорт отдельно во внешнем M40 archive с компактными Git refs.
Считать выполненным полный Train→Test до этого нельзя.

## Console, runner и анализ DATA: подготовлено, не проверено

Новая операция Console — `--timelearner-physical-model-evaluate`. Её schema1
job имеет kind `timelearner_native_physical_model_evaluation_job` и отдельное
поле `source_model_data`. Checked-file-source-v1 поддерживает этот же явный
role; подстановка DATA в прежний `source_recognition` запрещена. В Console
сохранены общие цикл native scheduler, полный declared design при прерывании,
проверки hash до/после проб, записи фактических input/Soma/LT/spikes.

Корневой пакет предоставляет `physical-model-evaluate JOB --source-model-data
MODEL --runtime-manifest RUNTIME --wall-seconds SECONDS --process-policy POLICY
--output NEW_DIRECTORY`. Требуется существующий contained process policy.
Используются прежние runner, runtime capture, artifact closure и повторный аудит
run manifest. Snapshot содержит полный MODEL; история обучения не копируется
повторно. Это не удаление исходной истории: она хранится отдельно в архиве.

Команды `analyze ... --format physical-model-data` и `analyze EVALUATION
--format physical-model-evaluation --model MODEL` используют новый явный
DATA-аудит. Он сверяет JSON/XML/identity digests, storage closure, реальный
Dataset/target, частоту, индивидуальные input banks и effective Threshold.
Нативная реконструкция XML по-прежнему проверяется только native importer.

Проверки сетки времени, событий, count/timestamps, полноты, меток/ID, порядка,
окон и FP/FN общие с прежним scorer. Полная наблюдённая реакция Test не требует
однозначного назначения каждого пика входному импульсу; это отдельное условие
Train. Неполный declared set не получает pooled counts. DATA-результат сохраняет
`training_completed=null`, `declared_training_outcome=null`,
`source_training_evidence_checked=false`, `calibration_confirmed=false`,
`evaluation_verdict=null`. Метаданные исходной модели не превращаются в proof.

Native fixtures теперь дополнительно сохраняют standalone MODEL и оригинальный
recognition source. Подготовлены8 Python проверок на этих реальных native
артефактах: обе топологии, счётчики, перестановка/перенос строк, пропуски/дубли,
NaN, frozen hash, censoring, заново подписанные противоречия, разделение старого
proof role, source snapshot и публичный analyze CLI. Добавлена транспортная
регрессия native source role; будущая native selection —248 Linux/247 Windows.
Это список будущих проверок, не PASS. Старые247/246 и текущая Windows227
относятся к другим снимкам кода.

До применения к научному корпусу нужны новая сборка Console/интеграционных
тестов, compiled inventory, actual fixtures/Python gate и запуск операции в
новом процессе. Ускорение, меньший RSS и полная приёмка этапа5 не заявляются.
