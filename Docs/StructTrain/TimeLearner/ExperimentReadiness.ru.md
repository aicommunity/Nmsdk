# Готовность к научным экспериментам — 10.11.2026

Новая полная научная серия ещё не допущена. Исторические августовские4/8–6/8 остаются рабочими результатами исходного протокола; новые инженерные gates их не отменяют и не заменяют. Полностью принят этап0, этапы1–12 частичны.

Последние факты:

- SDKf39 на M40:12 audited PASS/5 unobserved в17-case gate. Load/XML и два свежих процесса waveform transfer проверены, Packages5 не принят из-за OOM. [Опубликованные primary и границы проверки](NativeArchiveRepair17Oom-20261110.ru.md).
- Isolated C0 старого SDKff42 также завершился kernel OOM при4GiB. SDK355/Pulse165 на M40:15 audited PASS, C0 incomplete/OOM4GiB, две warm проверки не запущены; полный18-case gate не принят. [Точные terminal records](https://github.com/aicommunity/Nmsdk/blob/0b1ea04e53c102a079b65319942fd699377f1b9d/Docs/StructTrain/TimeLearner/ValidationPlans/NativeArchiveMove18-20261110/terminal-readback.json). Move/copy ownership имеет отдельный PASS и не объявляется достаточным исправлением памяти.
- [Новый full119 на обоих workers завершён30completed/29PASS/1FAIL/89not-run](https://github.com/aicommunity/Nmsdk/blob/22e9714bb/Docs/StructTrain/TimeLearner/Native119DatasetReadiness-20261110.ru.md). Исправление foreign-reference прошло1/1 на каждом; dataset snapshot test пропустил штатный Build/Init после MatrixData и упал до импортера. Исправленный SDK22e9714 прошёл real complete TU syntax; свежие полные119/43leaf/310rules на Elder и M40 прошли canonical preparation, обе сборки фактически работают. Runtime119 ещё не принят. Full119 и полный compact primary новых попыток остаются открытыми.
- [Console cold7: два сквозных сценария подготовлены](https://github.com/aicommunity/Nmsdk/blob/829b67aca/Docs/StructTrain/TimeLearner/Cold7ConsolePipelineAcceptance-20261110.ru.md): preflight/новый Train/export/measured calibration/real confirmation/frozen evaluation/rollback. На M40 проверены только import и ровно2 collected IDs, физические фазы пока не выполнены;675 Scripts Git blobs и полный metadata archive независимо сверены. Actual reader16 диагностически прошёл; Console2 пока не выполнен.
- Windows: SDK8ec closed-build audit принят отдельно от original descendants_remaining. N=1 native8:6PASS/2FAIL на fresh-process log path; isolation обоих callers прошла full TU syntax на M40. Исправленный SDKe086 A2 compiler exit0, но original descendants_remaining/непринят. Отдельный closed-build audit прошёл13.530268s,4078source/17287dependency/62runtime files неизменны; original отказ сохранён. Подготовлены повторные native8 и два stopped-child cases. Native приёмка исправления впереди; Windows не заменяет Linux.
- [Reader/CLI11/11 и два просмотренных временных графика](NativeArchiveGatePairReports.ru.md) опубликованы. Actual package6 reader16 прошёл16/16 на407JSON+294CSV закрытой отрицательной119 серии; повторение на принятом subject, полная primary публикация, Console cold Train→Test и общая mode/physics matrix остаются открытыми.
- Elder: [тот же SDK355 в normal Release завершил18/18](ElderNormal18Preservation-20261110.ru.md), включая C0 и обе warm проверки; полный primary713 originals/2.30MB опубликован в Git и независимо проверен. Перед новым запуском около12.6GiB свободно; удалены только1010 старых .o/292562912bytes, runtime/primary/logs сохранены. Различие с M40 ASan ещё не объяснено контролируемым A/B. Cleanup inventory publication остаётся отдельным открытым пунктом.

[Прежние оперативные снимки](ExperimentReadinessHistory-through-20261110.ru.md) сохранены отдельно. Их исходные отрицательные результаты и промежуточные статусы не переоцениваются. [Состояние всех этапов и исторические receipts](ImplementationStatus.ru.md).

## Что требуется до первой новой научной серии

1. Принять полный native119 с точной выборкой и всеми310 artifact rules. Timeout/error/not-completed сохраняются отдельно; новые fresh SDK22e9714 сборки Elder/M40 начались; это ещё не119 runtime PASS.
2. Повторить на итоговом принятом subject уже прошедшие16 package6 Python checks: исходные индивидуальные targets/actual graph/C0, warm import, stopped/partial/zero-group states, certificate3/summary7, external primary и прежний package5. Metadata fixtures их не заменяют.
3. Проверить настоящий Console-путь нового cold7: preflight → cold Train → полный export → native Test import → calibration/confirmation → frozen evaluation. Inline publisher tests не подтверждают сам Console process. Сверить source execution binding, semantic model fingerprints и hash экспортированных bytes; при ошибке не подставлять шаблонный Test.
4. Зафиксировать конкретное N4 stock задание и его область применимости: профиль/все дочерние параметры/storage images, частоту, reset policy, обучение/калибровочные данные, порядок, ITI, все search/time budgets и методы измерения. Применение факторов подтвердить effective readback до дорогого Train.
5. Получить валидные полные наблюдения и отчёт задания. Honest unresolved/budget/nonseparable — допустимые результаты при достоверных данных. Invalid configuration/runtime/observation не выдаётся за научный отрицательный результат обученной модели.

Это допуск ограниченной серии, а не завершение общего плана. В нём допустимо оставить C-trim/PostTune Off и явно ограничить физические профили; вся обязательная матрица, оба сервера, N0/N1, N=1/2/4/>4, физика/торможение/частоты/режимы и все варианты PostTune всё равно остаются условиями общей рекомендации V2. Текущий candidate-window contract требует N≥2. [Source review N=1](SingleInputContractReview-20261110.ru.md) различает штатный scalar/single-impulse путь и multi-input omission метод; полное одновходовое cold Train→export/import остаётся открытым требованием плана. Существующие реальные probe/certificate tests не заменяют эту приёмку.

## Обязательные условия каждого научного задания

| Область | Обязательная проверка |
|---|---|
| Runtime/provenance | Изолированный неизменяемый runtime, exact source closure, compiler/flags, executable и фактически загруженные libraries; owned process identities, closure и resource lease |
| Физика/storage | Native construction и effective дочерний graph: классы, связи, частота, Cs/Rs/синапсы/LT. Immutable images и обнаружение name collisions; новые сегменты наследуют правильный профиль, индивидуальные обученные параметры сохраняются |
| Lifecycle | Штатный scheduler и единая частота дерева в проверенном контуре, без вложенного Calculate. Build/Calculate/Reset bool не используются как результат обучения; typed diagnostics и фактические состояния проверяются отдельно. Reset физической пробы не равен сбросу learner |
| Обучение | CapturedPerInput, anchorN−1, исходные bounds и tolerances: amplitude absolute1e-5, relative0, minimum1e-6, SyncTolerance из конфигурации/default0.02. Fresh all-input verification конкретной revision; stall не доказывает физическую невозможность |
| Train→Test | Полная обученная модель, реальные storage definitions/параметры/топология/связи/порог и происхождение преобразований; native import/readback и semantic fingerprint. Не требовать произвольного отличия от шаблона или всех L>1 |
| Калибровка | Явно Same-Matrix либо independent frozen; любой выбранный threshold подтверждается реальным spiking run. Silent target остаётся FN; NonSeparable — отдельный исход |
| Наблюдения/scorer | Trial/sample IDs и labels, hash фактически предъявленного паттерна, real stimulus times, полные окна/complete, spikes и arbitrary-N soma channels; expected set без дублей/пропусков/NaN/Inf. Версия scorer и причины отказа сохранены |
| Frozen evaluation | Модель/порог фиксированы до Test, learned-state hash неизменен. TP/FP/FN, timing, morphology и robustness не смешиваются с выполнением, validity и сертификатом сходимости |
| Визуальный отчёт | Все объявленные паттерны и записанные somas, actual input overlays, читаемые временные overview/zoom и local-Y, явные units/clipping/полные окна, выбранная visual QA. Рисунки не заменяют primary и scorer |
| Запуск/публикация | Capability/factor preflight, точный parser реального конфигурационного диалекта, ресурсы/диск, frozen manifests, проверенные child commits и root publication; error push не даёт published |

При Train выбирается максимум закреплённого импульса в штатной пачке. Отдельная ранняя вершина допустима при небольшом хвосте соседнего отклика; полное возвращение к baseline между импульсами не требуется. Неразличимую общую вершину нельзя повторно засчитывать двум входам. Время, предсказанное моделью задержки, не заменяет измеренный пик. Single-pulse characterization — отдельный диагностический режим. Test оценивает полную реакцию на паттерн, включая общий максимум и реальные spikes; критерий Train не подставляется вместо критерия классификации.

## Уже доступные научные результаты

| Результат | Доказанный объём |
|---|---|
| Августовские4/8–6/8 | [Saved-state replay](HistoricalAugustReplay.ru.md) и [historical cold Train→Test](HistoricalAugustColdStart.ru.md) сохраняют исходные рабочие наблюдения с плохой разделимостью. Это не сертификат Exact нового контроллера |
| Историческая Classic6/8 | [Матрица8 cyclic positions × Delay1.5/3.0s](HistoricalFrozenProtocolMatrixScientificReport-2026-11-07.ru.md): одна frozen модель,16условий,128предъявлений; в каждом TP1/FP2/FN0/TN5. Это не все8! перестановок и не16cold trains |
| Engineering N2 | [Measured calibration/frozen controls](ManagedNativeCalibrationAcceptance.ru.md): отдельный LT-профиль, один target/один foil, повторные предъявления и Same-Matrix calibration; TP2/FP0/FN0/TN2 в проверенных случаях. Не stock N4 задача и не независимые обучения по номерам ModelSpec |
| Stock N4 | [Восемь Train и diagnostic Test](FairDomainStockScientificReport-2026-11-07.ru.md): InvalidObservation; низкий threshold даёт FP7, высокий — молчание включая target. Это незавершённые Train; два порога не доказывают глобальную NonSeparable |
| Диагностика волн | [Каналы](NativeChannelDiagnostics.ru.md), [feedback profiles](FeedbackProfileScientificReport-2026-11-07.ru.md), [full/omit/single](HighThresholdSubsetScientificReport-2026-11-08.ru.md) и [single maximum Console](SingleMaximumConsoleReplay.ru.md) исследуют механизм измерения. Они не дают нового успешного классификатора |

Stock NSPNeuronGen не содержит дополнительной LTMembrane. Engineering LT результаты не доказывают причинный эффект её инерции: для этого нужен парный A/B при прочих одинаковых условиях. Изменение порога влияет на динамику через feedback; offline sweep одного spiking CSV не заменяет подтверждение выбранного порога.

После сквозного допуска выполнить cold retrain в исходных условиях и legacy/V2 A/B с одинаковой математической целью, затем frozen порядок/ITI/reset проверки. Target должен присутствовать в каждой позиции; reset-per-trial и continuous stream — отдельные протоколы. Seed считается независимым повтором только при реальном источнике случайности и сохранении через Reset. Идентичные детерминированные состояния не являются независимыми обучениями.

Сборки, численные проверки и render выполняются на user@10.245.1.11/user@10.245.1.17 через user@10.245.1.12; Windows .14 — дополнительный согласованный worker, его совместимость не подменяет обязательные проверки двух основных серверов. Исходники, конфиги и результаты синхронизируются через Git. Компактный Git хранит сжатые primary, модели, метрики и выбранные рисунки; полные воспроизводимые отчёты — кэш M40 Data. [Масштаб и visual QA](VisualTestReports.ru.md).

СерияD не возобновляется автоматически. Получение8/8 не является условием завершения рефакторинга. Все прежние gates остаются доказательствами своих версий, не суммируются в общий текущий PASS и не объявляются отсутствующими из-за смены критерия. Предыдущий накопительный текст этого документа доступен как54ea56fa8c2a684e0fdcb61771a81df248833186:Docs/StructTrain/TimeLearner/ExperimentReadiness.ru.md; исходные отчёты и измерения не удалялись.
