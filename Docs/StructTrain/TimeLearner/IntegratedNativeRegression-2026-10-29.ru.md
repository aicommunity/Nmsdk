# Полная native регрессия: 29 октября 2026

На обоих workers завершён полный normal Release проход из одного исходного
снимка: root `912ef71b36fbc040c6177a82070a796ee5eb99de`, PulseLib
`c7266dcb93ec51a765125bc30647cf1b59129c91`, Rdk
`1812624ff75c60f03ad57c10b379d3e3848590bc`. Все семь gitlinks совпадают с
фактическими HEAD, исходные деревья чистые. Native и независимый Python audit
завершились с exit code 0 на каждом worker.

| Проверка | Elder-1 | M40 |
|---|---:|---:|
| Native cases | 491 | 491 |
| Passed / helper skips / failures | 480 / 11 / 0 | 480 / 11 / 0 |
| Отдельные Rdk CTest groups | 3 / 3 | 3 / 3 |
| Независимые Python tests | 114 / 114 | 114 / 114 |
| Python skips / failures / errors | 0 / 0 / 0 | 0 / 0 / 0 |
| Stored / raw hashes, проверенные локально | 3268 / 3266 | 3268 / 3266 |
| Runtime path/hash records повторно проверены перед публикацией | 28 | 30 |

Одиннадцать skips — роли дочерних процессов для import и compatibility tests,
которые запускаются родительскими controls. Это не пропущенные parent tests.
Сохранены parent/child XML, журналы, model exports, первичные JSON/CSV и runtime
manifest. Native XML задавался аргументом отдельного процесса, дочерние XML
не перезаписывали родительский. Model clock не подменялся test-only seed.

Python source `54b3d56073ebbe9e2cc3ef9edacb5085bf817293` записан отдельно:
13 модулей production-data regression с явными evidence directories. Изменения
между native и Python source в Tests, Libraries, CMakeLists, Rdk/Bin gitlinks
отсутствуют. Fresh-process cross-worker replay остаётся отдельным ранее
опубликованным контролем. Counts этого полного прохода не подменяются counts
предыдущих адресных экспериментов.

Во время M40 full run другая сборка столкнулась с нехваткой места; событие
сохранено в s09-config-m40. Для публикации полного результата потребовался
отдельный успешный аудит первичных данных, а не только нулевой exit code.

## Опубликованные исходные данные

- [Elder-1](../../../Reports/StructTrain/TimeLearner/s08-integrated-elder1/README.md),
  evidence commit `bc37077f18adce02c9d90b2aecdc2b75fc8e6b4f`.
- [M40](../../../Reports/StructTrain/TimeLearner/s08-integrated-m40/README.md),
  evidence commit `182191b9534f62257687b97b24f9f7fc936dd71e`.

SHA256SUMS покрывает сохранённые файлы; validation.json содержит SHA256 и размеры
исходных байтов gzip-артефактов. Все перечисленные hashes повторно проверены на
локальном Git checkout. Исполняемые файлы в отчёты не включены.

## Граница вывода

Это проверка интеграции перечисленного source scope, а не завершение исходных
этапов 4–8 или всего плана. Полный production PostTune candidate loop, frozen
recognition/calibration, исторический replay, order/ITI и научная матрица ещё
открыты. Позднейшие connected-owner guards, lossless config adapter и Rdk BOM
исправление не входят в native source этого прогона. Их адресные проверки
документируются отдельно; старый full PASS на них не переносится.

PulseLib принят через merge commit develop
`4db59424125dda426a29bc74faac565db871511f`; отличие от native c7266dcb —
только документация. Root develop merge `9e06c339a8186e3330303f6cd4fa829d09b74510` записывает
этот точный gitlink. Свежий checkout на M40 подтверждает все семь gitlinks
и чистое дерево. [Git closure](../../../Reports/StructTrain/TimeLearner/s08-accepted-closure-m40/README.md),
evidence `7f21442575db614df55c781bb4c9b242c5fbea6e`: 5 stored / 2 raw hashes.
Первоначально отдельные clones не были зарегистрированы через submodule init;
эта setup error исправлена, recursive status повторно проверен. Первый HTTPS
push отчёта не прошёл из-за отсутствия credentials; origin возвращён на
штатный SSH transport, опубликованный commit проверен через ls-remote.
