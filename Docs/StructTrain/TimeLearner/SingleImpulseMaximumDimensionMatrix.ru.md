# Размерная матрица SingleImpulseMaximum

Добавлены четыре native test groups: Classic/Branch ×2000/20000Гц. Каждый
проверяет N=1,4,6; прежние четыре N=2 cases сохранены отдельно. Это16
положительных физических условий и16 A/B пар, а не16 новых gtest IDs.
Пятая прежняя fault-группа проверяет три границы отказа для обеих топологий.
Адресный gate содержит9 gtest IDs и10 Python reader tests (прежние6+новые4).

C++ вызывает production native executor на настоящем storage/Environment
графе. Сравниваются все stimulus/soma samples между схемами4/5, часы с
прежним roundoff1e-12, физическая размерность, выбранный input, raw maximum
и запрет выдачи training certificate. Для Classic записываются все N сом,
для Branch — одна физическая сома с сохранением physical_input_count=N.
Выбран input0 при N=1 и input2 при N=4/6. Фиксированный training threshold100
объявлен до построения. Нормализация fixture — N1; N0 и другие профили этим
расширением не проверяются. CapturedPerInput и остальные defaults не меняются.

Четыре новых independent readers проверяют фактическое множество12 новых
условий, raw argmax, сохранность всех каналов/revisions в A/B и отказ при
потере физического канала. Прежний reader явно оставляет новые четыре
именных группы отдельному reader, сохраняя собственный ожидаемый набор
четырёх полных N2 captures и шести fault captures. Лишние неизвестные схемы
и неполный состав не считаются PASS.

Постановка серверной приёмки: normal9/readers10 на Elder, затем ASan9/readers10
на M40 после завершения и свежей closure/release прежнего ASan38. Нельзя менять
source/build активного задания. До фактических receipts это только новый
проверяемый код, не принятое расширение матрицы. Локально выполнен только AST
и source review; численные проверки выполняются на серверах.

Предыдущий ASan38 относится к Root038/Pulse217 и исходному N2 helper. Его
результат не переносится на новые N1/4/6 assertions автоматически. Полная
mandatory physics/mode matrix, full-burst assignment, convergence и научная
классификация остаются открытыми.
