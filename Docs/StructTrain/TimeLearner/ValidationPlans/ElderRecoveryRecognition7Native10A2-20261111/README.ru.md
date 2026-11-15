# Последовательная попытка A2 после занятости рабочего слота

A1 завершился до компиляции с reservation_capacity_exhausted: на Elder
установлен slots=1, и одновременно работал короткий primary-bundle collector.
Whole group закрыта,0 C++ cases выполнены; старый исход A1 сохраняется.
Это не недостаток памяти или диска и не ошибка модели. Ограничения не меняются.

Перед A2 registry inspect подтвердил reserved slots/memory/disk=0, available
slots=1. Collector завершён; следующие owned numerical jobs не запускаются
параллельно с native A2. Sourceca8be945/Pulse1110808 и4128файлов A1 повторно
проверяются, без изменения source. Build/runtime/output создаются в новых
каталогах A2. Cohort10, budgets, physical free floor2GiB и disk reservation2GiB
сохранены. Canonical preparation и native outcome A2 ещё не приняты.
