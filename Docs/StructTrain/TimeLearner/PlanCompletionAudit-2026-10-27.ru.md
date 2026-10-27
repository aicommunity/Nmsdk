# Текущее выполнение полного плана TimeLearner — 27.10.2026

Это актуальная поэтапная сводка на дату проверки (Europe/Moscow).
Она заменяет прежние накопительные формулировки статуса, но не нормативный
[план](RefactoringPlan.ru.md) и не исторические измерения.
Исходный [аудит 25.10](PlanCompletionAudit-2026-10-25.ru.md) сохраняется как
исторический снимок с последующими дополнениями.

**Полностью принят этап 0. Этапы 1–7, 9, 10 и 12 выполнены частично.
Этапы 8 и 11 в требуемом новым планом сквозном виде ещё не выполнены.**
Это классификация по условиям приёмки целых этапов, а не процент объёма работы:
этапы существенно различаются по сложности и зависимости друг от друга.

## Дополнение: финальная адресная проверка native-model-builder

После A2 завершён A3 на root `c1f90650bf7e5e01b848fbb5a278950ae927e641`,
с тем же PulseLib `37e8cc47a50712daf98186dae933836b7218a974`:
на каждом сервере **29/29 новых и 68/68 регрессионных**, M40 ASan **21/21**
(detect_leaks=0). Добавлены cold Ns=3/individual Rs, тормозные offsets,
фактическая Branch solo routing, growth и scaling тормозных сопротивлений.
Независимый Python-аудит на каждом сервере: 18/18 tests без skips, 112 service
CSV/packets, восемь отрицательных сертификатов и 42 valid/complete builder probes.

Все A1/A2/A3 артефакты, включая неуспешную A1, опубликованы через Git в
`Reports/StructTrain/TimeLearner/s06-native-builder-elder1` и
`s06-native-builder-m40`. Финальная сводка и ограничения:
[NativeModelBuilder](NativeModelBuilder.ru.md). Это проверенный C++ API-подэтап
этапов 4/6; configured V2, portable trained-state codec и полная matrix остаются
открыты. Классификация целых этапов 0–12 **не изменилась**.

Локальная перепроверка полученных Git-пакетов: 3754 stored hashes и 3750 raw
gzip payloads без ошибок. [Машинная сводка](NativeModelBuilder.validation.json).
PulseLib объединён и опубликован в develop merge commit
`5f1a6076edfe2e306e507013a82dc7574ec735d7`; root сохраняет этот точный gitlink.
Root merge: `feb18e9b5d1cf7d0459bc8fedd8649f73fde6daf`, опубликован в develop.
На обоих серверах отдельный recursive checkout восстановил его с чистыми
деревьями и точными gitlinks. Это приёмка builder API-подэтапа, а не всех
требований этапов 4/6 или всего плана.

### Исторический промежуточный статус A2 (до финальной проверки)

После исходного снимка ниже появились изменения в root
`51f8579e81909f00170508e99028825230bfd5b9` и PulseLib
`37e8cc47a50712daf98186dae933836b7218a974`. Оба локальных дерева чистые;
gitlinks согласованы. Работа находится в `stage06/native-model-builder`,
ещё **не объединена в develop**. Bin/Rdk не изменились относительно снимка ниже.

Реализованы явные C++ `ConstructNativeModel`/`AdoptNativeModel`, storage-owned
cold construction и отдельный native-owned путь повторного Build, сохраняющий
текущий граф. Это уточняет прежние слова «builder отсутствует»: они описывают
принятый develop-снимок, а не новую рабочую ветку. Configured
`ControllerVersion=2` по-прежнему отсутствует; обычная загрузка конфигураций
не переведена на новый путь.

Завершение A2 подтверждено exit code 0 обоих серверных заданий и независимым
повторным чтением XML: **на каждом сервере 25/25 новых проверок и 68/68
регрессионных, failures/errors/disabled = 0**. Source HEAD на обоих серверах
совпадает с указанным root, source status чистый. Проверены Classic/Branch,
2000/20000 Гц, neuron modes 0/1/2, learner modes 0/1, N=6, forced Build,
Reset/UnInit/Init, heterogeneous C/individual Rs, отказ cold replacement при
внешнем listener и cold N0/N1 service. Это адресный набор, не полный декартов
продукт режимов и не научный эксперимент распознавания. Четыре cold searches
подтверждают честный SearchUnresolved, а не успешную сходимость.

Первая попытка A1 дала 18 fixture failures и пять Branch regression failures
на каждом сервере; причины и исправления записаны в
[NativeModelBuilder](NativeModelBuilder.ru.md). Их нельзя скрывать итогом A2.
Сырые A1/A2 артефакты пока находятся на серверах, не опубликованы комплектом
в Git. Хеши повторно прочитанных A2 XML и границы проверки сохранены в
[машинном дополнении](PlanCompletionAudit-2026-10-27.builder-a2.json).

**Подэтап builder ещё не принят полностью:** нужны дополнительные cold Ns>1
и inhibition/routing проверки, ASan, независимый аудит новых первичных данных,
Git-публикация всех попыток и merge child → root. Классификация целых этапов
0–12 в таблице не изменилась; этапы 4 и 6 получили проверенную адресными
тестами реализацию в рабочей ветке, но не полную приёмку.

## Принятый снимок до рабочей ветки

Новый ограниченный контур уже работает через явный C++ API `BeginNativeTraining`
обоих learner: capture → bounded search → реальные structural edits → fresh
all-input verification. Однако `ControllerVersion=2` и новый начальный builder
пока отсутствуют. Обычная загрузка старых конфигураций продолжает legacy-путь.
Наличие принятого API-подэтапа не означает, что все пользовательские эксперименты
уже автоматически перешли на новый алгоритм.

## Проверенный Git-снимок

| Репозиторий | HEAD на момент проверки |
|---|---|
| Root | `c2aa03e7dfdb3a24ddc42276015d9f3e5cfcf450` |
| PulseLib | `38e977c674f999675d469198269c8937c83cce5e` |
| Bin | `e78596e9639a841cd1989d73df7fe614419770ce` |
| Rdk | `8846c1423ab13a24e3ebfdce786ce85b6a9fc0d6` |

До записи этого отчёта деревья чистые, child HEAD совпадают с root gitlinks.
Изменённые дочерние ветки объединялись `--no-ff` и публиковались до корня.
PulseLib/Bin branch hints в `.gitmodules` — develop; version задаётся gitlink.
На обоих серверах заново прочитаны независимые recursive checkouts этого root:
HEAD совпадает, status чистый, все gitlinks согласованы.

Основные server source checkouts остаются на test snapshot
`87e444b67ef471d79cb8277630472ee1a090226c`; это ожидаемая отдельная immutable
сборочная версия. Она не подменяется merge SHA в runtime manifests.
Активных build/test процессов именно в `/home/user/timelearner-refactor/`
при этой проверке нет. Состояние чужих экспериментов этим утверждением не описывается.

Машинные результаты read-only проверки:
[PlanCompletionAudit-2026-10-27.evidence.json](PlanCompletionAudit-2026-10-27.evidence.json).
Новых сборок, численных тестов или научных экспериментов этот аудит не запускал.

## Состояние этапов 0–12

| Этап | Статус | Что есть и что ещё требуется |
|---|---|---|
| **0. Начальное объединение веток** | **Выполнен** | Исходная работа объединена в develop, gitlinks и branch hints согласованы; child commits опубликованы до root. Последующие подэтапы также приняты merge commits. Recursive checkout проверен на обоих серверах. |
| **1. Реестр доказательств, режимов, дефектов** | Частично | Есть исходные SHA/gitlinks, августовские опорные commits, журнал исправлений и уровней доказательности. Нет полного поэкспериментного ledger с августа и завершённого semantic review всех параметров/аудитов. В сохранённом inventory все 211 записей параметров — `semantic_review=pending`, все 324 script candidates — `review_required`. Это исходный inventory, не текущая завершённая экспертиза. |
| **2. Изолированные сборки/runtime** | Частично | Настраиваемый deploy root, отдельные ресурсы/ini, code/build/runtime manifests, tracked Reports и Git-передача проверены на двух серверах и Qt5/Qt6. Осталось автоматически собирать полный production run bundle перед/после настоящего Train: данные, модель, события, фактически загруженные библиотеки и все стадии одного run. Самостоятельный runtime recorder не заменяет runner. |
| **3. Наблюдения/scorer** | Частично, основная измерительная реализация проверена | Recognition schema 4, strict scorer, labels/IDs/completeness/nonfinite, arbitrary soma dimension; отдельные native training schemas и auditor. Есть реальные CSV и corruption tests, whole-burst assignment, explicit assigned-wave selection. Нет единого production-пути Train→calibration→frozen Test→единственный verdict для всех старых и новых анализаторов. Историческая метрика остаётся отдельной. |
| **4. Lifecycle/storage/эффективная модель** | Частично, большая проверенная основа | Исправлены подтверждённые общие Copy/XML/frequency/lifetime дефекты; есть native profiles, checked image registry, graph/cache/link readback, rest/reset, growth и individual physics controls. Native editor сохраняет чужие банки/наблюдателей и learned Rs/C в проверенных случаях. Не завершены вся profile/mode/load/reuse матрица и новый builder/repeated Build contract. Legacy parent overrides/wake passes остаются. Новые production profiles не распространены на всю экспериментальную матрицу. |
| **5. Полный экспорт модели и Train→Test** | Частично, physical archive реализован | Полный native physical graph, определения зависимых storage images, external stimulus ports, semantic fingerprint, fresh-process и cross-host Git roundtrips проверены. Нет законченного producer/consumer полного обученного состояния двух learner: references/certificate/controller boundary/conversion/calibration вместе с моделью. `EncodeNativeTrainingState` — diagnostics, не checkpoint/import. Реальный сквозной Train→Test ещё не принят. |
| **6. Общий контроллер** | Частично, рабочий explicit API | Общий `NativeTrainingService`, topology adapters, scheduler Before/After, budgets, external stop, Reset/warm/retarget и native edits работают; локальные действия не исполняются вручную тестовым циклом. Общие legacy helpers имеют отдельные compatibility A/B. Нет configured `ControllerVersion=2`, нового исходного builder и всей production mode matrix. |
| **7. Алгоритмы обучения** | Частично, bounded native контур проверен | CapturedPerInput raw references, signed measured residuals, missing/ambiguous/clipped handling, model revision invalidation, Classic round-robin/Branch reverse, bounded L/Ns/Rs, physical bank/alias rules, actual integration assessment и независимый final sweep реализованы. Не готовы динамические Rs domains по каждому L, production длительности окон/recovery, весь N0 repeatability/spread и quantized/best-effort контракт, optional C-trim и полная физическая/inhibition матрица. Четыре native поиска пока проверены на ограниченной области L=2..3 и возвращают честный SearchUnresolved. |
| **8. Conversion/PostTune/calibration** | **Не выполнен по новой спецификации** | Старые реализации существуют, но нет нового immutable Solo→Recognition conversion с idempotent load/save, полного transactional PostTune commit/rollback и законченного Same-Matrix/frozen calibration pipeline с реальным threshold confirmation. Текущий новый training API явно отклоняет C-trim/PostTune/calibration. Поддержка не отменена — остаётся обязательной. |
| **9. Пакет экспериментов и миграция** | Частично, основа | Root package содержит inventory, runtime, native evidence auditor и tests. Главный CLI пока поддерживает только `inventory`; runtime/auditor имеют отдельные module CLI. Нет остальных production-команд, полного lossless config adapter и законченного deletion/migration manifest. Старые активные/исторические scripts остаются в Bin/Docs. |
| **10. Очереди/provenance/publisher** | Частично только provenance и ручная публикация evidence | Runtime identities и checked Git-публикации конкретных тестовых пакетов работают. Нет production ConditionSpec/serializer, job runner с owned PID/hash, leases/locks/crash recovery и fail-closed publisher для полного run. Старый Bin publisher по-прежнему содержит rsync и push с `check=False`. Ручной evidence harness не считается реализацией production pipeline. |
| **11. Контрольные научные эксперименты** | **Не выполнен** | Выполнены implementation/characterization controls и короткие compatibility A/B. Не приняты исторический replay августа, исходный cold retrain, scientific legacy/V2 comparison, настоящий order/ITI sweep и вся mode/physics матрица. Native waveform A/B и перестановка строк CSV не являются robustness экспериментом распознавания. |
| **12. Вся документация и завершение** | Частично | Поддерживаемый root комплект, профильные PulseLib/Rdk/Bin изменения и historical marking есть; каждый новый подэтап документирован. Нужны завершение обновления всех learner/config/analysis/ClDesc материалов, удаление устаревших CLI ссылок после миграции и итоговая проверка единой актуальной спецификации. Сам этот статусный отчёт не закрывает этап 12. |

## Что уже принято полностью в пределах конкретных подэтапов

Эти пункты имеют код, scoped server checks, опубликованные артефакты и merge,
но не подменяют условия приёмки целого этапа:

1. Изоляция runtime/deploy и строгая фиксация source/build/binary provenance;
   исправление CRLF-повреждения рабочих копий Reports.
2. Strict recognition collector/scorer и отдельный native evidence auditor;
   проверка IDs, чисел, окон, completeness и фактических timestamps.
3. Lifecycle/storage исправления, immutable image recipes, graph/binding/cache
   inspection, native physical archive и cross-host/fresh-process roundtrip.
4. Native probe executor обоих learner с единственным штатным scheduler,
   Branch solo routing, защитой от lifecycle/структурного вмешательства.
5. Whole-burst assignment и явный `AssignedBurstWave`, сохранивший прежний
   `IsolatedWindow` default. Прогноз задержки не подтверждает отсутствующий пик.
6. Bounded decision controller и native structural editor: preview перед live edit,
   effective readback, shared-bank legality, сохранность внешних наблюдателей.
7. Общая служба `BeginNativeTraining`, fresh all-input certificate, сохранение
   references при Reset/warm и их инвалидирование при retarget.
8. Typed revision observer с полными boundary captures и доказанной native A/B
   эквивалентностью. На исследованных двухвходовых пробах — ускорение 6.36–8.35;
   83.52–100.01 относится только к стоимости чтения ревизии 169-node графа.

Подробности: [NativeTrainingService](NativeTrainingService.ru.md),
[NativeModelEdits](NativeModelEdits.ru.md), [BoundedTraining](BoundedTraining.ru.md),
[AssignedWaveSelection](AssignedWaveSelection.ru.md),
[ModelRevisionObserver](ModelRevisionObserver.ru.md), [ModelArchive](ModelArchive.ru.md).

## Актуальные проверки и границы доказательности

| Снимок/проверка | Фактический результат | Область |
|---|---|---|
| Root `4a27a579b5fff61e025ed200f627aa0482f06e1a` | На каждом сервере четыре maintained CTest suites; PulseLib 293 pass + 9 skip из 302, три Rdk suites — 18 pass | Последняя описанная полная CTest-серия этого хода работ. Skips не считаются прохождением. Последующие изменения имеют отдельную адресную приёмку. |
| Root `1e980f9103920c6012afe810d1e4be23929c80dc` | 43/43 addressed на каждом сервере, 4 M40 ASan | Финальные bank readback/Rs изменения native editor; не повтор всей CTest matrix. |
| Root `90d11d1990221753e6b494dbf40d83964b7d0fa3` | 39/39 на каждом сервере; реальные traces/state summaries | Общий service API и diagnostics. Четыре ограниченных поиска имеют negative final certificates; Exact/warm control использует отдельный sync 0.2 с и не подтверждает default 0.02 с. |
| Root `f2fe81f96d68859690ae56e4ef29f5c32c549bc7` | 56/56 C++, 18/18 Python на каждом; 56 M40 ASan | Explicit assigned-wave policy и её evidence/protocol binding. |
| Root `1f1e0352bce24bc538d888e20f4e20ebc4906339` | 85/85 C++ на каждом сервере | Observer/full identity equivalence, native Classic/Branch A/B 2000/20000 Гц, service/search/final gates. |
| Root `87e444b67ef471d79cb8277630472ee1a090226c` | На каждом: 12/12 replacement/lifetime, 20/20 old-provider regressions, 18/18 Python; M40 ASan 59/59 | Final observer tests; ASan native A/B subset — 2000 Гц. Полная CTest после этого снимка заново не заявляется. |

Последние пакеты дополнительно содержат независимую проверку 56 service CSV и
четырёх negative certificate summaries на каждом сервере, CSV всех четырёх A/B
пар и full/cache counters. Нельзя суммировать эти числа как количество независимых
научных обучений: наборы перекрываются и проверяют разные snapshots/контракты.
ASan выполнялся с `detect_leaks=0`; отсутствие всех утечек не доказано.

В этом аудите повторно проверены **7809 записей файлов в 56 SHA256 manifests**;
отсутствующих файлов или hash mismatches нет. Также проверены **4571 raw gzip
payloads** в десяти поддерживаемых `validation.json/raw_files` manifests:
размеры и распакованные hashes совпали, необработанных layouts нет. Это доказывает
целостность перечисленных опубликованных bytes, но не полноту всех требований
плана и не правильность научных выводов автоматически.

## Конкретные открытые стыки, проверенные по коду

- `ControllerVersion` отсутствует в production learner properties/dispatch.
  Новый API сам по себе не переключает существующие XML-конфигурации на V2.
- Оба legacy `BuildStructure` пересоздают `Neuron`; native training ownership
  ещё не заменяет `ABuild` новым read-only/reuse builder. При `Ready=false`
  повторный Build требует отдельного исправления и runtime-проверки сохранности
  learned/heterogeneous state. Простой no-op Build готового объекта — другой случай.
- Legacy Branch `AllSynapsesNormalized` продолжает проверять только active input.
  В новом API отдельный final verifier уже обходит все входы, но старый путь этим
  не переписан и не объявляется исправленным.
- Legacy `ParallelResistanceScaled` и `RebuildCableForPostTuneProbes` остаются;
  последний использует parent MembraneCapacity либо fallback `1e-9`.
- `ModelArchive::ValidateMetadata` пока требует положительный raw
  `captured_per_input`. Новый FinalVerification корректно допускает raw 0 и
  отрицательный raw при ненулевом rest baseline. Полный trained-state codec
  должен устранить эту несовместимость; сквозной runtime transfer с таким случаем
  ещё не выполнен. Это code-level finding, не результат нового эксперимента.
- Главный `Scripts/StructTrain/TimeLearner/__main__.py` имеет только команду
  `inventory`. `commit_timelearner_matrix_wave.py` в Bin всё ещё использует rsync
  и непроверяемый push; production replacement отсутствует.

Сохранённый inventory относится к прежним SHA, указанным внутри JSON. Текущий
повтор той же **эвристики по именам tracked paths** даёт 325 кандидатов вне нового
root package: root 99 (98 в Docs), Bin 226, PulseLib 0. Ноль по этой эвристике
не доказывает отсутствия scripts под общими именами: semantic/content review
всех участвующих trees ещё обязателен. Удаление старых путей и законченный
migration manifest не выполнены; исходные 324 записи нельзя выдавать за готовую
классификацию текущих 325 кандидатов.

## Приоритет дальнейшей реализации

1. Закончить production-путь модели: native initial builder/adopt/repeated Build,
   storage-owned physics, configured `ControllerVersion=2`, строгий readback.
   Параллельно закрывать semantic property/evidence review, а не переносить pending
   в PASS автоматически.
2. Закончить алгоритмы: geometry-dependent Rs domains, production окна/recovery,
   весь N0 quantization/repeatability и optional heterogeneous C-trim; проверить
   исходные tolerances и честные отрицательные исходы.
3. Собрать полный versioned learned-state export/import и Train→Test, затем
   conversion/PostTune/calibration/frozen evaluation на конкретной финальной модели.
4. Закончить root experiment package, lossless config adapter, scheduler и publisher;
   удалить прежние scripts, сохранив их repository/SHA/path/blob в migration manifest.
5. Выполнить исторические replay/cold и scientific legacy/V2, order/ITI и полную
   mode/physics матрицу; затем провести итоговую сквозную проверку документации.

Августовские визуально подтверждённые **4/8–6/8 остаются рабочими наблюдениями
своего исходного протокола**. Новые implementation tests их не отменяют и не
доказывают robustness при другом порядке/ITI. В рамках рефакторинга серия D
автоматически не возобновлялась.
Научные 8/8 не являются условием завершения рефакторинга; условия исходного плана
остаются неизменными, цель не достигнута и не отмечена complete.

Отдельно от технической готовности плана: при чтении `get_goal` во время этого
аудита механизм автоматической цели вернул `usageLimited`. Это состояние
ограничения использования, а не завершение плана или приёмка этапов. Аудит
не менял статус цели и не сокращал её исходный объём.
