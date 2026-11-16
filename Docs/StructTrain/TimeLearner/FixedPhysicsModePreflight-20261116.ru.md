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

[Адресная приёмка M40 получена:6/6](FixedPhysicsModePreflightAcceptance-20261116.json), без failures/errors/skips. Tested source c8480262231bfaace0c009edc806176a0e263a32, controls ae28eca764c54ca173264ced9e69e7fe5de955cb; owned PID91339 закрыт. Fingerprint шести input fixtures f10f715cab7847d8bee823c5b1131946c2bb32a26ec3921c8ee7288250a979b7. Обычные generated jobs точно совпали с production baseline; включённый C-search отклонён до дорогой подготовки/Train, history-only и общий C-search declaration API сохранены.

Elder A1 отказал до тестов: reservation_capacity_exhausted,0 executed. В его ledger slots=1 и этот слот занимает s11-frozen-order-native-elder-a2. Отказ и исходная декларация сохранены, это не отрицательный исход тестов и не новый научный результат. Повтор на втором worker отложен до закрытия работающей серии; ограничение ресурсов не менялось.

M40 proof7eb02d510fc8c5c428688e4129453e575e624a5dec94c69f1ecec7b178c2b075/403090bytes/54members и Elder refusal9cf87bc1902f6f9e573c85fb9b28fc11bf30aaa1a55d39909ea5545f14103561/107006bytes/40members хранятся во внешнем M40 архиве. На Elder независимо проверены каждый member, исходные counts/IDs и source root. Code Git bundle d9014ba1d8d06b118e8d5f6fc0c2a2fd62ecd67b2359122ae1cbd6dc96937818 и fixture Git bundle24fd8e60fac42a9c4cc4d21b410e350d912b9f336ab454607643756741adbd71 сохранены там же.

После закрытия и архивации отказа удалён только новый чистый standalone source cache Elder:989867302 logical bytes. Полный Git commit опубликован и воспроизводится; controls, fixtures, модели и observations сохранены, live leases не пересекались с каталогом. Квитанция0b8f0a75610498a9ad4a7daf19f856c2f2ec6bbae99b53cc94e3ae1d95a35949. Source cache потребуется восстановить в отдельном каталоге для отложенного A2.

Работающие cold600 и frozen-order64 используют прежние immutable source/runtime; их исходы проверяются отдельно. Приёмка6/6 относится к подготовке деклараций, не к native C-search physics или всей матрице. Полный исходный план остаётся активным.
