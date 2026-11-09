# Сохранение первичной причины остановки native gate

Native119 A1 успешно собрал оба targets и подтвердил 19 cases. Следующий `NativeCandidateWindowBanks/ClassicN6EachActualInputRoutesNPlus2` остановлен внешним лимитом 2400 s. GTest не успел записать итоговый XML. Worker сохранил typed gate result `execution=timeout`, но затем безусловное чтение XML заменило верхнюю причину на FileNotFoundError.

Исправление касается `native_acceptance_worker.Worker.gate`: результат процесса сохраняется до разбора XML; отсутствие, повреждение или дубли XML фиксируются отдельной ошибкой наблюдения. Число выполненных cases берётся только из реально завершённых записей XML; ожидаемые, но ненаблюдённые IDs записываются отдельно. Сначала проверяется исходный typed gate outcome, затем полнота/согласованность JUnit и runtime route. Ни timeout, ни пустой/повреждённый отчёт не могут дать положительную приёмку.

Девять адресных metadata tests вызывают production `Worker.gate` с контролируемым native-gate adapter: timeout без XML/с partial XML/с truncated XML, process error, ложный success без/с повреждённым XML, нормальное завершение, failed case и duplicate ID. Они не заменяют повторную проверку реального N6 расчёта и не являются новым scientific result. До серверного запуска статус — source-only.

Не изменены лимит 2400 s, входные интервалы, число входов/проб, математические критерии, модель и проверки model revision. Исходный отрицательный запуск не перезапускается и не исправляется задним числом. SIGTERM stack попал в `IdentifyModel/ModelRevisionObserver::Read`; одиночная выборка стека не доказывает, что весь расход времени приходится на этот путь. Оптимизация требует отдельного измерения с сохранением обнаружения изменений модели.
