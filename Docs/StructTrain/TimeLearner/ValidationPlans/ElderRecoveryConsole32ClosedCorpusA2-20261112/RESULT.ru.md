# Полный Elder native32 primary corpus — 12.11.2026

Актуализация12.11: [независимый DATA replay обоих полных корпусов принят16/16](../M40Native32IndependentA2-20261112/RESULT.ru.md). Ниже сохранён исходный collection/Git transport результат; его замечание о ещё требуемом semantic restore относится к моменту публикации.

Production collector завершён:operation_passed=true, whole group closed, lease released, heartbeat_errors пуст. [Terminal](completed/worker/terminal.json), [controller result](completed/controller-result.json), [closure](completed/closure-and-reservation.json), [состав/контрольные суммы readbacks](completed/readback-integrity.json).

Сохранены весь job и его controller:2703regular files/834627225bytes, плюс links; проверены33исходные закрытые units. Исходный native32 результат32/32 и исходные данные не изменены. [Collector proof](completed/worker/primary-bundle-proof.json). Архив не переоценивает старые неуспешные попытки.

Компактный Git corpus:[bundle](../../../../../Reports/StructTrain/TimeLearner/RecoveryConsole32NativeClosedCorpus-Elder-20261112/bundle.json), [primary.tar.xz](../../../../../Reports/StructTrain/TimeLearner/RecoveryConsole32NativeClosedCorpus-Elder-20261112/primary.tar.xz), [origin](../../../../../Reports/StructTrain/TimeLearner/RecoveryConsole32NativeClosedCorpus-Elder-20261112/ORIGIN.json). XZ6041800bytes; expanded834638873bytes; SHA256ecd6a2570e4cdbac1aaac6c1f0d6e604cfc13f38032188732434fbbe46b8e42a. В Git добавляются четыре bundle-файла, без build/runtime binaries и полного rendered cache. Исходный readback на Elder не удалён.

Транспорт выполнен только через Git:[точные commits/объекты/хеши](git-transport.json). Standalone commit9b4ac27075c43f80b2ed4c2e44ddfc2796db115d; Git pack6097413bytes, SHA2566b4e793065aa6f607d21d7697a58aa2aa6acd891f23649726cd4e7f674823be0. Локально выполнены Git fsck и проверка SHA256/размеров каждого извлечённого файла. Это проверка транспортной целостности, **не независимый semantic replay**; он остаётся следующим отдельным требованием для этого полного32corpus.

Native subject8362d58f4d6576a0c8b0cc7633270976dff1df7b/Pulse1110808f4ad1f67538dadc6fe1d3f097e00c0630:4active-Build guards,7Console publication controls,11legacy wire cases и10public recognition cases с20полными target/foil trials. Scope технический N2/Sync0.2 и stopped/completed states; это не научная N4 матрица. Коллектор не запускал модели повторно.

A1 был отклонён до создания job из-за имени worker:Elder вместо фактического Elder-1. A2 фиксирует правильный host; manifest и пределы исходных данных не менялись. Disk floor2GiB/output cap256MiB соблюдены.
