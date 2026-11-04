# Текущая карта выполнения исходного плана,04.11.2026

Основание — [утверждённый план0–12](RefactoringPlan.ru.md). Нумерация и критерии
не сокращены до реализованных API. Это актуализация состояния после принятых
04.11 объединений; подробный прежний перечень требований сохранён в
[аудите01.11](PlanCompletionAudit-2026-11-01.ru.md). Старые «ещё не реализовано»
или «worker жив» в исторических дополнениях не заменяют текущие receipts.

Полностью принят только этап0. Все этапы1–12 остаются **частичными**. Exact
для нескольких fixtures, завершённый процесс и научный PASS различаются.
Ни итоговая карта всех моделей, ни весь рефакторинг пока не завершены.

## Согласованный develop

| Репозиторий | Принятая исходная точка |
|---|---|
| Root | `e218753e49b12f05708a60a4f22266882f810430` |
| PulseLib | `9ec4566d71bf56d4eeb5c8a920bbc683fcd85299` |
| Rdk | `10e9d05aa658dd2203c89bc84ba9166595b50014` |
| Bin | `99f58da9296a794374cef679bbb878cb62af979a` |

Root develop последовательно принял resource budgets, construction threshold/
calibration и native probe/report acceptance. Merge commits сохранены; rebase,
squash, cherry-pick не использовались. Pulse child опубликован прежде root.
[Threshold integration receipt](InitialThresholdIntegrationVerification.json) и
[native probe integration receipt](NativeProbeIntegrationVerification.json)
сравнивают реальные trees с ранее проверенными источниками, вместо присвоения
merge commit вымышленного нового runtime pass. Нового численного запуска под
этими merge commits не было. Исходные normal/ASan primary и отрицательные
предшествующие verdicts сохраняются.

## Что принято и что ещё требуется

| Этап | Проверенные подэтапы / текущее состояние | Требования до полного закрытия |
|---|---|---|
|0 — начальное объединение|Принят ранее; дальнейшие адресно принятые изменения идут children-first через `--no-ff`.|Не считать каждую feature выполненной по одному merge. Текущий Git checkout проверяется отдельно ниже.|
|1 — доказательства и параметры|Есть source/property/evidence registries и адресные runtime receipts. Даты и версии критериев сохраняются.|Закончить полный semantic/property/evidence review обоих learner; разрешить remaining unknowns и отличать code fix от runtime-verified fix для каждого режима.|
|2 — сборки и runtime|Изолированные deploy roots, runtime/source manifests и process identities используются в принятых gates. Новые большие отчёты — на Data M40.|Закончить весь build/resource matrix, quantitative worker policies и проверку воспроизводимости общего runtime; не обновлять работающие SDK.|
|3 — измерения и scorer|Строгие native observations/scorer, explicit incomplete/invalid statuses и реальные временные отчёты работают в проверенных путях.|Покрыть все legacy adapters и оставшиеся modes/physical profiles; вся оценка должна зависеть от полных реальных окон и единственного versioned verdict.|
|4 — lifecycle/storage|Нативные fixtures и explicit model boundaries проверены;18 threshold/archive cases на каждом worker, включая реальные ответы2000/20000Hz.|Полная fresh/reuse/Copy/Load/growth/heterogeneous physics матрица и все legacy/V2 paths, единая семантика Default/Build/Init/Reset/Calculate без learner-specific обходов.|
|5 — model export/Train→Test|Исправленные8 calibration cases и7 readers на каждом worker:4 реальные Exact sources,4 исходных stopped controls,2 ModelSpec2 distinct-owner transfers.|Распространить полную semantic/response identity на остальные modes/topologies/dimensions/profiles. Не подменять полный export overlays и не обещать mid-probe checkpoint.|
|6 — общий контроллер|Native V2 service, adapters и scoped controllers реализованы; native probe теперь объединён. Граф, history и source references сохраняются в адресных import/probe случаях.|Полное legacy/V2 A/B и рефакторинг remaining duplicated controls; вся configured/multirate/compatibility матрица.|
|7 — алгоритмы|Честные bounded search/measurement/final certificate пути реализованы и адресно проверялись. C-search normal262/119 принят своей веткой; ASan K1 ещё работает.|Принять pending algorithm branches и их общий срез, завершить N0/N1/C-trim/quantization/bounds/nonmonotonicity/reset/physics matrix. Отрицательный stock Train не доказывает PhysicalInfeasible.|
|8 — conversion/PostTune/calibration|Есть versioned final states, transactional candidates и реальные calibration/frozen controls. Проверены новые threshold construction/transfer semantics.|Все реализованные PostTune/mute/inhibition/calibration/reset modes, commit/rollback/interruption, idempotent conversion и frozen independent evaluation для всей матрицы.|
|9 — единый пакет и миграция|Активные root CLI/анализ/отчёты реализованы; migration manifest и часть retirements приняты.|Удалить оставшиеся исторические executables из Bin/PulseLib/Docs после переноса нужного функционала, без wrappers; указать repository/full commit/path/blob. Завершить prepare/preflight всех supported factors.|
|10 — очередь/provenance/publish|Приняты path reservations15/15 и path+slot+RAM+disk budgets30/30 на обоих workers; диск привязан к реальному filesystem.|Связать public JobSpec/ConditionSpec с production Train→Test, весь owned process graph, cancel/recovery, actual resource policies и все publication/fault cases. Учёт заявленных ресурсов не является OS quota или полным scheduler.|
|11 — контрольные эксперименты|Августовские saved-state replay и cold controls сохраняют исходные4/8,5/8,6/8. Новый stock stopped A4:32 trials,80 trial-soma pairs,6+3 report checks,20 selected PNG просмотрены.|Legacy/V2, target в каждой позиции, order/ITI/reset, independent frozen и вся научная физическая матрица. Stock stopped diagnostic не заменяет Test обученной модели и не отменяет август.|
|12 — документация|Актуальные receipts/отчёты обновляются при каждом принятом срезе; новый A4 доступен для чтения.|Сквозное согласование root/submodule/config/ClDesc/defaults, оставшиеся migration links и снятие конкурирующих актуальных спецификаций.|

## Завершённые04.11 адресные проверки

- [Threshold/archive](InitialThresholdConstruction.ru.md):18 native cases на
  Elder и M40 ASan; четыре физических roundtrip Classic/Branch×2000/20000Hz
  сохраняют construction100 и поздний effective0.005, без LTMembrane.
- [Calibration preconditions](CalibrationFixturePreconditions.ru.md):8 native
  и7 data checks на worker; нет изготовленного certificate или ослабления
  CapturedPerInput/sync0.02/abs amp1e-5/relative0. Engineering LT fixture
  не обозначается как научный stock четырёхвходовый нейрон.
- [Native probe phases](NativeProbePhases.ru.md):12 imported jobs,7 readers
  и2 cold regressions на worker; прерывание warm baseline не меняет Rs и не
  запускает main probe. Все7362 primary files восстанавливаются побайтно.
- [Reservations](ResourceReservations.ru.md): schema2 атомарно учитывает
  каталоги/slots/RAM/disk;30 tests на каждом worker, включая настоящие два
  конкурирующих процесса и два filesystem. Recovery и production wiring
  остаются открытыми; живой K1 ledger не мигрировал.
- [Читаемый stock temporal report](../../../Reports/StructTrain/TimeLearner/s11-stock-stopped-phasea-visual-a4/REPORT.ru.md):
  полный кэш14728 файлов на M40,4450 trial-soma views,20 выбранных PNG в Git.
  Проверены40 metadata members и414 source hashes. Визуальная приёмка
  относится только к этим20 изображениям, не ко всему кэшу.

## Работающие проверки и следующие действия

C-search K1 root69789b8cb/Pulse84e456d на M40 имеет собственный неизменяемый
SDK/runtime. Supervisor3649813/start_ticks284056538, targeted native3660392
подтверждены живыми04.11. Предусмотрены34 адресных native cases, затем262
полных и119 readers. Успех не присваивается до фактического завершения и
независимой проверки. Этот снимок не включает новые initial-threshold/Rdk
и не является проверкой их будущего общего среза.

Отдельно запущен настоящий fresh recursive checkout root develope218753e4
только из origin, без object donors/alternates: M40 owner3667868,
`readbacks/s00-current-develop-checkout-m40-a1`. Он не собирает SDK и не
запускает модель. Проверяются exact gitlinks, чистота, tracked blobs и Git
connectivity. На момент записи checkout ещё работает; результата PASS нет.

Дальнейший порядок: принять эти результаты по факту; завершить общий
algorithm slice и его regression/probe checks; затем расширять контрольную
матрицу по уровням этапа11. Series D автоматически не возобновлять. Параллельно
продолжать незакрытые property/migration/scheduler требования; ожидание ASan
не является причиной объявлять план завершённым или останавливать всю работу.


## Последующее уточнение04.11

Fresh checkout owner3667868 закрыт успешно: origin-only roote218753e4 и все
семь gitlinks чисты,100534 tracked files сверены на worker и независимо с
локальными Git objects. [Доказательства и границы](FreshDevelopCheckout.ru.md).
Это не новый SDK build и не приёмка будущего C-search/containment code.

[Contained process primitive](ContainedProcess.ru.md) прошёл12/12 controls
на каждом worker;11 групп на сервер закрыты с kernel membership receipts.
OS limits и учёт потомков после потери frontend работают в этом API. Однако
lease recovery/journal/ConditionSpec/Train→Test wiring ещё не подключены;
старый runner и работающий K1 не переведены. Этап10 остаётся частичным.
