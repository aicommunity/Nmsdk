# Native133 и сохранённый анализ,05.11.2026

На Elder прошли все133 независимых native C++ tests:0 failed/skip,4142105ms. Фактический root `4f3db1160cda9bad59974af2bff01c023832248d`, Pulse `f6a917d395b21610f6bf6cbb0ed945e6cdee31dd`. [Архив2056 members](../../../Reports/StructTrain/TimeLearner/s06-shared-recognition-ab-a1/bundle.json):9668904 bytes, SHA256 `23b8ffbfdda712470dc50b9726040167af8a4fb5990a5ac77d9f2a71568f18b5`. Evidence `1ed9bb55c7e56fda8e117391943b07b66372dca1`.

Отдельные8 NativeRecognitionOwner controls на исходном1eab и новом4f одинаково не достигли завершённого предварительного обучения. Ни один не подтвердил положительный Owner contract. Все112 пар CSV независимо сверены побайтно из архива. Это не доказанная регрессия и не положительная приёмка переноса. Source2cb с явно заданной initial ISI[.01,.03] строится для новых Owner8/full133; допуски и алгоритм не менялись. Группы сравнения закрыты, lease освобождён.

## Recovery/declaration

| Попытка | Источник и данные | Фактический итог |
|---|---|---|
| A2 | package8c, его corpus2776 | Whole-worker timeout1800s;6 завершённых ok log records, седьмой started; следующие13 не начались |
| A3 | integrated d936 | Ошибка обвязки до tests/reservation: outer-label replacement изменил predecessor path внутри worker literal |
| A4 | integrated d936, прежний corpus8c | Все20 выполнены за5.238s:0 failures,8 errors,0 skips; suite не принят |

[Независимая сверка](RecognitionAndRecoveryVerification-2026-11-05.json) включает архивы/checksums,294 старых и317 объединённых source blobs. A2 evidence `c9bf294e88fd524aa99fa06159679c52acfd03da`:12 members,70992 bytes. A4 evidence `8ccc763af665883cc9637d90cd8d202ef2164bff`:13 members,57492 bytes, плюс диагностика A3. Все завершённые группы закрыты, leases освобождены. Нейронные модели этими проверками не пересчитывались.

A4 отвергает прежний manifest.analysis с pipeline_run_analysis_changed. Повторный анализ двух Train примеров показал единственное отличие: training_audit.auditor_version,3→5 для completed Classic-v1,3→4 для stopped Classic-N0. Остальные поля этих двух примеров совпадают; эквивалентность всех этапов/случаев этим не доказана. Старые manifests не изменены. Свежие native coordinator runs на объединённой сборке нужны для полноценного положительного gate.

Исторические данные требуют отдельного явно выбранного versioned adapter с известными схемами и полями. Нынешний explicit learned-v2-no-capacitance рассчитан на current auditor3 и должен быть пересмотрен/проверен для current5. Автоматически удалять все version поля нельзя. Изменённые certificate/residuals/trial counts/model/runtime и неизвестные поля должны по-прежнему отвергаться. Это открытая задача этапов3/9/10, не scientific PASS.

После свежего подтверждения закрытия A2 удалены607 временных regular files: каждый hash/size совпал с сохранённым исходным файлом, оригиналы дополнительно прочитаны. Удалены4 временные alias symlinks; уникальных изменённых test files не было. Освобождено140161024 bytes. Первичные файлы не удалялись.

При первой private Git-упаковке A4 loop variable затенил destination prefix; commit9cb44bee не публиковался в origin. Новая evidence8ccc исправляет только размещение, без изменения primary archive или переписывания старого commit; диагностика сохранена в previous-private-publication-path-error.json. Старые временные скрипты не возвращались в проект.

## Следующая приёмка

1. Завершить current SDK2cb Owner8/full133, не обновляя активную source/runtime среду.
2. Завершить full ASan304802/Pulsecc, затем fresh-process owner8 и readers128 с тем же runtime; focused44 их не заменяет.
3. Отдельно собрать integrated d936 с точными gitlinks и выполнить coordinator8/live6/recovery20 на свежих primaries; закончить targeted readers/role/resource checks.
4. Проверить explicit historical adapters без изменения старых manifests.
5. После runtime приёмки — настоящие merge commits Pulse/develop, затем root с точными gitlinks. Данная приёмка данных не продвигает candidate code.

[Галерея42 временных графиков и полный кэш](IntegratedMetadataAndTemporalReports.ru.md) уже опубликованы отдельно. SI единицы и причинное влияние LTMembrane не проверены. Только этап0 полного плана принят полностью;1–12 частичны.
