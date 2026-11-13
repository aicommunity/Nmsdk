# Оба настоящих холодных N0 preflight приняты

M40 s11-stock-n0-preflight-m40-a1: production public CLI1/1 PASS6.119с, outer completed/closed27.49807453714311с, operation_passed=true, heartbeat errors0. [Test log](completed/worker/validation/unittest.log), [closure](completed/process/whole-group-closure.json). Source69e985df6654ac64cc34571e6862119cf26b90c5.

Новый prepare-N0 schema4 создал отдельно fingerprinted Classic/Branch N0 jobs из исходного immutable N1 schema3 плана. Оба native preflight completed/valid; холодные effective identities совпали с соответствующими N1 initial graphs. Все native groups закрыты, fixtures/source неизменны. Штатный runtime105ccc46bf2d23aa093ee6ec5fb088d9f33faa8e572f8191869f8cc279377a8a, C++ SDK Pulse7c6c94785af0c83104d348bb3b733ed1f149c8a8/root74e5d206d4b619fcf81f77f11b54ebec7b8f0f6e.

[Classic index](completed/worker/native-stock-n0-preflight/Classic-stock-cold8-N0/index.json), [Branch index](completed/worker/native-stock-n0-preflight/Branch-stock-cold8-N0/index.json), [новый prepared index](completed/worker/native-stock-n0-preflight/prepared/index.json), [source-plan bindings](completed/worker/native-stock-n0-preflight/prepared/source-plan.json). Ns bounds1..128 только неопорным, Rs фиксированы индивидуально, anchorNs1/L1, cold inputs Ns1/Rs86M. Частота2000Гц, stock без LTMembrane и начальный threshold100 сохранены.

Это проверка создания и native codec/readback/идентичности, не доказательство сходимости или применения Ns>1 в обучении. Train/Test здесь не выполнялись. [Научная постановка](../../StockNormalizationControl.ru.md).

Producer22b88a7e43f2705f0a9a52fe1dca4185b386444f, pack134224B SHA25633ae2d9bfbf6b200de74e4242ecb0f62fdb2821114cd59bdeeeab22e5a6f591e;92 исходных Git blobs импортированы без перезаписи JSON, включая jobs/conditions/initial identities/process closures.
