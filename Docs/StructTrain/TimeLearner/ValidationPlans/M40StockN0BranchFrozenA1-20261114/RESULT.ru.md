# Branch N0: восемь frozen-проб фактического terminal state

M40 s11-stock-n0-branch-frozen-m40-a1: production1/1 PASS; outer completed/closed1785.6560876602307с, heartbeat errors0. [Unit log](completed/worker/validation/unittest.log), [whole-group closure](completed/process/whole-group-closure.json), [полный диагностический результат](completed/worker/tmp/stock-n0-stopped-matrix/result.json).

Использован actual stopped export после budget_exhausted, L=[38,38,38,1], Ns1/Rs86M: package SHA25628fa5dd184a7b1d45d2c2a62f2200406d346c91d65067e7b080686d137355a8a, model revision87be6dbf500ff125fec276415e8f140b3c6e13d13fc83c5f6eeb5b99287b26b7. Лучший промежуточный Ns4/L25 и шаблон не подставлялись. Полные восемь окон2с,2000Гц, reset-per-trial,1 target/7foils исходной PhaseA matrix1c1464e248f8744e858bd66df0be99e39969fd65; исходный порог100.

Frozen/import pipeline подтвердил неизменность модели и source graph. training_completed=false, certificate отсутствует, evaluation_verdict=null. TP0/FP0/FN1/TN7: при100 все паттерны молчат, target пропущен. Валидность исполнения не создаёт свидетельства сходимости или успешной классификации. Числа ответов будут включены в научный отчёт вместе с собственными временными графиками; полная сжатая primary публикация frozen-проб ещё открыта.

Actorf33948eb1515c6a20b9901fd335185a569238529, controleba92dd6fa3271fadaec2ccf3d7bfa0d63fe8404. Старый SDK root74e5d206d4b619fcf81f77f11b54ebec7b8f0f6e/Pulse7c6c94785af0c83104d348bb3b733ed1f149c8a8, runtime105ccc46bf2d23aa093ee6ec5fb088d9f33faa8e572f8191869f8cc279377a8a. Новый N0 search здесь не используется.

Producer32a3bc20313cadeef271f277d66105dedcdacdfc, pack224252B SHA2567bc19eec9dacac886241f98ee53f11d93e421d990e32fcab3c17c56810a28b03;27 исходных Git blobs импортированы без JSON rewrite.
