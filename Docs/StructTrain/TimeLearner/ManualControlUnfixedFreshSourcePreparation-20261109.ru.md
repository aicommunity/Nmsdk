# Парная исходная SDK-копия на M40 — 09.11.2026

В отдельный путь
`/media/user/Data/TimeLearnerRefactor/source-manual-control-unfixed-m40-a1`
доставлены Root `bb1d24ea950ff068c25f7db7186517b55eef3dbd` / Pulse
`800f92ae1f9e0133cefc0ccfe36abc3d8c99727f`, Bin918/Rdkd6 и четыре остальных
точных gitlinks. Все восемь независимых checkout созданы Git packs без alternates.
Работающие source/build/runtime A3 и corrected E11 SDK не менялись.

[Независимая metadata/Git-проверка](../../../Reports/StructTrain/TimeLearner/s10-manual-control-unfixed-source-preparation-m40-a1/independent-verification.json)
сверила4020 материализованных файлов по точным Git blobs и восемь HEAD/gitlinks,
равенство снимков до/после чтения и29 same-SDK imports. Package fingerprint
`d3dd9564a993abc98ee17d7edb793d71a6b09d0e188dcb2c3e8a77e9a5a8ab5f` и весь
Scripts tree совпадают с corrected E11 и проверенным db2; unit13/30 не повторялись.

Production source inventory четырёх TU содержит422 cases; после двух pure
declarations/proposal TU полный шестифайловый inventory —476. Два diagnostic-only
случая явно отделены. Для исходной версии выбраны **только четыре** witness
controls: POS2, NEG-Classic1 и NEG-Branch1. Эти IDs проверены по actual Git source;
ни476, ни474, ни4 не являются числом выполненных/принятых тестов.

[Сравнение реальных материализованных копий](../../../Reports/StructTrain/TimeLearner/s10-manual-control-unfixed-source-preparation-m40-a1/paired-materialized-differences.json)
связано с опубликованной corrected metadata revision
`85b1d24ab7e216285e90f5c65117b44cc35fb2c7`. Множества4020 путей одинаковы;
отличаются **ровно пять** файлов:

- `Core/TimeLearner/NativeCompositeTrainingAttempt.cpp` в PulseLib;
- `Core/TimeLearner/NativeTrainingService.cpp` в PulseLib;
- `Core/TimeLearner/NativeTrainingService.h` в PulseLib;
- `Core/TimeLearner/NativeTrainingServiceComposite.cpp` в PulseLib;
- `Tests/Integration/Libraries/Test_PulseLib_CompositeTraining.cpp` в корне.

Все прочие материализованные Git bytes совпадают, включая исходники физики,
Rdk, App, CMake и Python package. Это source isolation, **не** доказательство
одинаковых физических waveform или воспроизведённой runtime-ошибки. Для него
остаются нужны настоящие U/R native controls с одинаковым заявленным профилем.

[Evidence](../../../Reports/StructTrain/TimeLearner/s10-manual-control-unfixed-source-preparation-m40-a1/summary.json)
содержит10 файлов, около1,60MB: lossless gzip snapshots/inventory, receipts,
pair differences, metadata-tool sources как сжатые данные и checksums. В этой
подготовке вывод сжимался с первого наблюдения; transport failure отсутствует.
Голые исполняемые wrappers в Reports/Docs не добавлены.

Ограничения sparse checkout те же: Docs/Reports не материализованы, Bin содержит
ClDesc/Watch; omitted paths сохранены. Это не полный архив исторических данных.
CMake, compiler profile, runtime, модель и тесты здесь **не запускались**;
canonical execution spec не создавался. Следующие шаги — независимо завершить
текущий baseline248, подготовить фактический build/resource/canonical профиль и
выполнить POS2/NEG1/NEG1, corrected20 и остальные regression partitions. Source
подготовка не закрывает этапы исходного плана и не создаёт научный PASS.
