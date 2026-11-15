# N0 before A1: отказ подготовки до native execution

Owned job s11-n0-geometry-before-train-m40-a1 закрыт с process_error; unit1/1 FAILED. Production prepare-N0 вернул stock_n0_source_runtime_changed: исходный N1 plan привязан к runtime105ccc, а запрос объявил новый runtime. [CLI transcript](completed/worker/native-n0-geometry-before-train/public-cli.log), [unit log](completed/worker/validation/unittest.log), [closure](completed/process/whole-group-closure.json). Ни native preflight, ни Train не запускались.

Guard сохранён. В A2 штатный prepare_recovery(full_observation=True) сначала создаёт новую N1 постановку для выбранного runtime; точное равенство прежних configuration и initial identity проверяется до prepare-N0. Частота/физика/target/tolerances и все научные budgets прежние. Это исправление запуска, не отрицательный результат алгоритма.

Producer852ca75ed434c04456ab4e4e19773c3f4246c3a5; pack82602B SHA2569ae7fbd49cfea894bdb633edd1d6948d741b935e62ec8c9ef213103f0be68d79. Исходные receipts импортированы без JSON rewrite.
