# Фиксированная физика и явный C-search: ранняя проверка режима

Воспроизведён дефект подготовки uniform Fast и Stock/PSI опытов: конфигурация schema8/base4 с действующей capacitance_search проходила через оба генератора, хотя протокол и последующий physical audit требуют неизменных C. Legacy optional_modes.sync_capacitance_trim=0 этому не мешал: он не управляет новым поиском C.

Это риск неверно поставленного дорогого Train и позднего отказа physics audit. Данная проверка не утверждает, что в опубликованных Fast/PSI результатах поиск C был включён.

## Воспроизведение

На M40 вызваны настоящие production declare_case и make_cases из source6e72f24b408d8a45dc31798769c123bbdf071b7d. Их blobs совпадают с принятым rootc3e9e25fc4336d96d41df65d933f6648842da65e: uniform79d56c26cfdb32b31606aa5848f2a8ac92e5d38e, PSI4cc9c9ba7a21f9ebeecf4b08000e4a4d926ef4ad.

В реальные исходные cold templates добавлены versioned C0-history и валидная конечная политика C/C0=[0.9,1.1], subdivision_depth2, maximum_contexts5. Общий production validate_job и policy validator принимают декларацию; legacy SyncCapacitanceTrim остаётся0. До исправления получены1 uniform и2 PSI jobs с сохранённым активным поиском C. Реального Train в воспроизведении нет.

## Изменение

Общий require_fixed_capacitance_policy запрещает явную capacitance_search именно в опытах с фиксированной C. Проверка вызывается в uniform declare/prepare/run и в Stock/PSI make_cases. Prepare отказывает до разбора тяжёлой reference primary; run — до проверки runtime и запуска native preflight/Train.

Запись capacitance_history без поиска допустима: владение и сохранение C0 не являются её оптимизацией. Общий native pipeline продолжает принимать явный versioned C-search; legacy bool не переинтерпретируется. Математика, CapturedPerInput, amp/sync tolerances и физические компоненты не меняются. Финальный effective-physics audit сохраняется.

## Проверка кандидата

Подготовлены6 server checks: exact equality обычных деклараций с исходным production output; отказ uniform и PSI на явном C-search при legacy0; разрешённая C0-history без поиска; сохранение общего C-search API; отказ prepare/run до reference/runtime/controller work и без output artifacts.

Серверная приёмка ещё не получена. Работающие cold600 и frozen-order64 используют прежние immutable source/runtime; их исходы проверяются отдельно. Полный исходный план и обязательная matrix остаются открытыми.
