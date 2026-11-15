# N1 Classic: исправленная половина физического A/B

Подготовлено; не запускать до закрытия [before Train](../ElderN1ClassicBeforeTrainA1-20261112/PLAN.ru.md) и проверки свободного места/lease. Предыдущая M40 after попытка не заменяет эту пару на одном Elder.

SDK Root `fcfd8bdff149c14cbe67149e996945d122bf954d` / Pulse `5f1a4ac6f9aff208ada7f8bcf62645c9d79a6615`; общий Python controller `fd55a9936ba6018ca86e583c0e844b10fb582d56`. Применяется существующий послеисправленный executable, без новой сборки и изменений runtime. Фактор — только production условие N1 geometry interleave; остальные Core-файлы между subjects совпадают.

[Побайтное сравнение подготовленных jobs](comparison/matched-jobs.json) выполнено на Elder штатным prepare: весь Classic job до и после совпал, SHA256 `c2f4bfa17157fbb1edef2990d176356ea69826f6387e7f65b7c84f59c0e61c99`. Также совпал Branch job для будущей отдельной пары. Различия source/runtime provenance сохраняются отдельно в condition manifests. Initial graph и8 actual waveforms уже совпали; after characterization не подставляется под before runtime identity.

Все условия и критерии совпадают с before: CapturedPerInput, N4/N1,2000Гц, исходная пачка, assigned impulse, declared windows, amplitude absolute1e-5/relative0/min1e-6/Sync0.02, anchor3, прежние bounds,128 search probes/1280 edits/1800s, finalization300s/process2100s/outer3600s. Окна и физика не исправляются только для одной половины. Learning outcome принимается честно; Exact не является условием технического PASS. Никакого Test/calibration после незавершённого обучения.

Результат пары должен сравнивать фактический порядок geometry/Rs, свежие signed residuals, probes/edits и причину остановки. Отрицательные/ограниченные результаты сохраняются. Одного совпадения или различия конечных L недостаточно. После обоих результатов публикуются compact primary и читаемый алгоритмический отчёт с временными реакциями. Branch и остальные режимы обязательной матрицы остаются открыты.
