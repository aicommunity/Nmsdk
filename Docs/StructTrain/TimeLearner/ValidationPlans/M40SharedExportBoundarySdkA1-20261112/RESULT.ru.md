# SDK102 M40: 50 PASS, первая finalization-проверка пропущена

Fresh build завершён,50/50 реально выполненных C++ cases прошли: прежние36 и14 recovery-package cases нового объединённого API. Следующий NativeFinalizationBoundary/ClassicSnapshot был skipped: отсутствует TIMELEARNER_POSTTUNE_FIXED_SOURCE. Всего102 expected:50 completed PASS,1 skipped,51 not run. Общий job_validation_passed=false; это не102/102 и не функциональный допуск нового Train.

[14 исходных подтверждений](failed-finalization-readback/readback-integrity.json) сохраняют JUnit, exception, terminal, progress, runtime/source snapshots, outer/51 child closures и released reservation. Внешний worker завершился exit1; ошибки heartbeat/final captures отсутствуют. Whole outer и все51 child groups закрыты; cleanup не превращает отказ в PASS.

Ошибка моей подготовки набора: выбраны исторические fixture-dependent cases, но runner передаёт только явные разрешённые output/ASan env и потому не получает legacy fixture roots. Незадекларированный глобальный env не следует добавлять как обход. [Исправление](../../FinalizationStagedDataInputs-20261112.ru.md) использует существующие native_gate schema5 DATA roles и native_data_checks; сохраняет все52 исходные проверки и все202 assertions.

Passed50 сохраняются со своим code subject Root c73575fe545b00cc7c9bf170c81c185c30b7026a/Pulse dfb9a98244f91b4f4029d8470465fd40116436ca. Оставшиеся52 нужны на том же production core с исправленным test-only loader и явными8 DATA inputs; незавершённый новый scope не принимается по этим50. Полная публикация первичного корпуса остаётся отдельной задачей; исходники/артефакты на M40 сохраняются.
