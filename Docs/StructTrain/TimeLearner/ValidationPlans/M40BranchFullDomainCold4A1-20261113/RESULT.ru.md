# Branch N4/N1: полный Train и DATA audit завершены

Принят1/1 actual production Train test за2793.485s; outer completed2815.022s, processes closed, operation_passed=true, heartbeat_errors=[]. Это валидный отрицательный исход обучения, не Exact: budget_exhausted/native_training_time_budget_exhausted, certificate=null. Исходные receipts, index, execution и summary сохранены без пересериализации. Полный первичный corpus ещё требует компактной публикации; до неё не объявлять Git closure научных данных завершённой.

104 search probes/51 edits,51 измеренный кандидат input2,0 rejected observations. Четыре кандидата попали во временной допуск20ms, ни один одновременно в амплитудный1e-5. Начальный L1: timing−240ms, amp0. L25: timing−15ms/amp−0.0118549032499361; L26: timing−6ms/amp−0.011918946239878103. Все эти Rs86МОм. Терминальный графL=[27,27,27,1], Ns1, Rs86МОм; revisionfea609e0651ccf779b58a9321e8d4008e984db768ce1167cdcc1406d1a03280d, state198897970bytes. Терминальная структура не подменяет завершённое измерение кандидата и не имеет final verification groups.

Существенный следующий разбор: physical domain evidence наL26 даёт channel minimumRs2880071.5552629367, но control для общего банка inputs0/1/2 имеет locked_by_shared_bank=true и возвращает допустимый интервал86M..86M. Поэтому здесь достигнута временная готовность, а N1 не изменяет сопротивление для восстановления амплитуды. Нужно проверить групповую правку владельцев одного физического банка, не ослаблять правила unique assignment и не менять общий storage prototype. Это ограничение текущей реализации, не доказательство физической невозможности.

Read-only научный отчёт с полной source проверкой и заранее заданным выбором графиков запущен отдельным job s03-branch-full-domain-report-m40-a1; результат/visual acceptance пока pending. Научная классификация этой модели не проверялась.

Уточнение: read-only A1 имел ошибки выбора ролей/перечня отказов. Принят исправленный A3; см. ../M40BranchFullDomainReportA3-20261113/RESULT.ru.md и ../../BranchSharedBankScientificReport-20261113.ru.md. Группа108 полна, selection valid, но не потреблена контроллером.

Уточнение по полному inventory: из52 domains 27 shared-lock и25 unlocked. У unlocked [27,27,26,1] также timing-ready, но измерено только Rs86M. Первый проход broad geometry-first N1 откладывает остальные Rs; shared-bank lock не является единственной причиной отсутствия нормализации. Приоритет — bounded local Rs exploration на измеренной timing-ready геометрии с сохранением fairness и fresh verification.
