# N0 after A1: отказ подготовки до native execution

Owned job s11-n0-geometry-after-train-m40-a1 закрыт с process_error; unit1/1 FAILED. Production prepare-N0 вернул stock_n0_source_runtime_changed: исходный N1 plan привязан к runtime105ccc, а запрос объявил новый runtime. [CLI transcript](completed/worker/native-n0-geometry-after-train/public-cli.log), [unit log](completed/worker/validation/unittest.log), [closure](completed/process/whole-group-closure.json). Ни native preflight, ни Train не запускались.

Guard сохранён. В A2 штатный prepare_recovery(full_observation=True) сначала создаёт новую N1 постановку для выбранного runtime; точное равенство прежних configuration и initial identity проверяется до prepare-N0. Частота/физика/target/tolerances и все научные budgets прежние. Это исправление запуска, не отрицательный результат алгоритма.

Producer89cda6a92f722db06efeafe312629ca857369077; pack82624B SHA256dccc3dfe50f68775ec167e981798bd0a7a9a66333b5c867e1c7953d6eb9f50ae. Исходные receipts импортированы без JSON rewrite.
