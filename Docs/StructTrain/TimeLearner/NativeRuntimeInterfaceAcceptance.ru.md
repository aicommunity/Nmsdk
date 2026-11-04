# Проверка назначения runtime и места на диске,04.11.2026

Ошибка постановки live-routing A3: вместо NeuroModelerConsole был передан корректный по hash manifest тестового Test_PulseLib_StorageComponents. Фактический stdout показывает Google Test suites, а не объявленный Train. Задание остановлено по сохранённым kernel handles; закрытие controller/native group и освобождение глобальной lease проверены заново. Этот запуск не дал Train/Test результата и не проверил шесть live cases. Все первичные данные и operator stop records сохранены.

В candidate package `8c9ee9f6b319a06224d6ebdcdd537b88e993fc4a` добавлен ранний контроль интерфейса executable: настоящий `--help` должен объявлять Console options и требуемые операции. Runtime проверяется до и после; gtest ограничен help/list без выполнения test bodies. Вызов ограничен временем/объёмом вывода и закрывает собственную группу. Guard вызывается до output в managed pipeline, standalone native/calibration worker. Help подтверждает назначение программы, но не выполнение научного задания или соответствие всех схем данных.

На Elder прошли7/7 actual checks без mocks/failures/errors/skips: Console, gtest, переименованный Console.rs2, canonicalization операций, неизвестные операции, отказ неправильного runtime до standalone/managed output. Console snapshot33fc сохранён отдельно от test-runtime SDK. Production code остаётся feature до полного coordinator/live regression; child gitlinks и принятые алгоритмы не менялись.

[Полный compact primary](../../../Reports/StructTrain/TimeLearner/s02-runtime-role-and-disk-maintenance-a1/bundle.json):118 файлов,91 760 bytes compressed,SHA256 `ad6f9faa34a8800b75453535c1093e925ab45679a76300ce25858a7536c27b1b`. [Независимая проверка](NativeRuntimeInterfaceAcceptanceVerification.json) подтверждает каждый member,294 Python source blobs,9 published checksums, разные executable hashes и свежие closure/release. Evidence commit `bdf598dd4f2e8649c6a354161d8824c6e7f77471` доставлен через Git. Локально выполнены только Git/hash/archive проверки.

## Обслуживание диска

Object-cleanup A1 остановился до удаления: старые build directories содержат Git repositories FetchContent. Другая операция нашла две побайтно одинаковые read-only копии immutable Git pack в build-test-switch-off-b3/build-test-switch-on-b3. Проверены SHA256/размер/filesystem, чистые HEAD/status/stash и отсутствие пересечения с active process/held production resources. Только эти копии заменены hardlinks; содержимое файлов, refs, stash, SDK/runtime и primaries сохранены.

Освобождено408 945 883 bytes: свободное место6 036 226 048→6 445 170 688 bytes. Началась queued recognition-helper build. После размещения её isolated source на Elder осталось около3GiB. Capacity production registry не менялась. Cleanup refusal и полный dedup plan/producer/terminal/lease входят в primary. Эти действия не запускают нейронную модель.

## Следующие gates

Coordinator A4 ждёт recognition whole-worker closure/release до создания bounded unit, затем8 tests/20 native phases с Console33fc/package8c. Live-routing A5 ждёт8 PASS и closure/release coordinator A4, затем6 tests/10 phases. Обе pre-unit queues подтверждены живыми; модели ими ещё не запускались. Предыдущие launcher A3/A4 отказали до worker из-за старого служебного label; проверки не выполнены.

На M40 joint ASan44 работает; full304 ждёт PASS/closure/release. Capability7, очереди и обслуживание диска не завершают этапы1–12 и не дают научного результата классификации.
