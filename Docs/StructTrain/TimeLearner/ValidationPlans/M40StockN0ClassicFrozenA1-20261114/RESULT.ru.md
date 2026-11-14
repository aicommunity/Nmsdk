# Classic N0: восемь frozen-проб фактического terminal state

M40 s11-stock-n0-classic-frozen-m40-a1: production1/1 PASS1804.423с; outer completed/closed1833.2312008631416с, heartbeat errors0. [Test log](completed/worker/validation/unittest.log), [whole-group closure](completed/process/whole-group-closure.json), [полный результат](completed/worker/tmp/stock-n0-stopped-matrix/result.json).

При фиксированном исходном пороге100 все8 паттернов молчат: TP0/FP0/FN1/TN7. Это валидная отрицательная диагностическая оценка остановленной модели, без сертификата обучения и без успешной детекции target. Значение accuracy7/8 здесь отражает преобладание foil и не является научным PASS.

Проверены полные окна2с,2000Гц, reset-per-trial,1 target/7 foils исходной PhaseA matrix1c1464e248f8744e858bd66df0be99e39969fd65. Применён настоящий terminal export Classic N0, а не шаблон или лучший промежуточный кандидат: package SHA256d8d545f9d0e9a038e7dc232ad86de94213496ac94481a1c32a822b3b98c3f070, model revision35d849faa2aaea5d2620f0fd59d9934c77760b7fde0dd49d3284539f69f68263. Source graph identity и вся модель до/после frozen-проб сохранены; training_completed=false. Низкоуровневый scorer сам по себе не аттестует запуск; native process/manifest и fixture проверяют его отдельно.

Source actorf33948eb1515c6a20b9901fd335185a569238529, controleaca1065ed5a429b45ea2710459ef86d8f0fe1d3, runtime105ccc46bf2d23aa093ee6ec5fb088d9f33faa8e572f8191869f8cc279377a8a. Это старый SDK root74e5d206d4b619fcf81f77f11b54ebec7b8f0f6e/Pulse7c6c94785af0c83104d348bb3b733ed1f149c8a8; кандидат нового N0 поиска здесь не используется.

Producer3367f095a68820e3225d17471ff32d9cfde93756; Git pack161559B, SHA25628210bc44a3dd18174c0e2afbcb32519fce728bc32e4dbfa98d4edccc59a6720. Исходные receipts импортированы без переписывания JSON. Полный сжатый primary frozen-проб и собственные временные графики всех8 паттернов ещё ожидают публикации; Same-Matrix подбор и настоящий прогон выбранного порога — отдельный последующий эксперимент.
