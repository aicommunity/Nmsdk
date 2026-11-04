# Pending: production coordinator и все отчёты changed-threshold rollback

Source2cc27b9f3192ccd5a11d5dcc8189f68205205b15 содержит candidate coordinator CLI и расширенную проверку четырёхфазных отчётов. Это feature-код, не принятая реализация develop.

Elder worker2076977/start337169840 ожидает exact closure/release corrected-baseline build. Далее8 actual public coordinator checks:4 новых cold N1 Train→остановка на завершённой границе→continue→export→native measured grid/confirmation→frozen Test и4 остановленных источника без export/Test. Ожидаются20 native units на неизменяемом SDKf679, полный managed ledger/unit binding и отсутствие повторного Train при continue. До фактического gate этот путь не считается принятым. Общие fault/cancel/reconciliation, ConditionSpec, queue/publish wiring и mode matrix остаются открытыми.

На M40 worker3904533/start287701184 реально строит новые временные отчёты по опубликованному primary bfa6be48a8732892fa75c3207eb8c45b3bd8c6b3, без повторного расчёта моделей. Все1955 archive members проверены;1900 native run/result files восстановлены. Старый render test перечислял только3 фазы и не охватывал новый rollback-frozen. Теперь требуется совпадение exact phase sets; число trial–soma pairs берётся из ModelSpec/declared trials, а не постоянного24. Планируется32 matrices/192 pairs, фактический PASS и visual QA ещё не получены.

Полный кэш остаётся на M40 Data, в Git попадут выбранные рисунки/metadata. jobs.json и сжатые orchestration сохраняют точную постановку без учётных данных. Группы ограничены по RAM/tasks/wall time; native ASan K1 и его runtime не изменяются.

Для последующего A/B Root1eab24decb6432947afc928e7f049f3a07de2709/Pulse8644 объединяет mechanical dispatcher и исправленные cold fixtures. Git trees Tests/App/CMake равны corrected baseline33fc; нового candidate SDK пока нет. Оба source snapshots опубликованы в отдельных ветках, в develop не объединены.
