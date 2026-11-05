# Joint304: актуализация первичных readers

Исходный source802 native304/304 не означает успешного анализа. Reader attempt
A3 выполнил95/119:18 CLI subtest failures из-за UnboundLocalError analyze,
два setUpClass errors из-за прибавления объявленных ModelSpec2 cohorts.
A1 не создал unit из-за неправильного launcher API, A2 завершён kernel OOM
при256MiB; эти попытки не считаются PASS. C++/научные данные не пересчитывались.

Отдельный root7a98295005762c11a9937e5c8f63e6628564d6d6 исправляет CLI name shadowing.
Этот branch объединяет его через merge; Tests C++, App, CMake, Pulse/Rdk/Bin
gitlinks побайтно совпадают с source802. Новая native сборка не приписывается.

Прежние schema3 boundary readers требовали ровно6 completed/6 stopped;
совместный gate объявляет ещё4 C-Off ModelSpec2 completed. Schema4 readers
требовали4 completed и4 codecs; совместный gate добавляет4 C-On completed и
8 ModelSpec2 codecs (две топологии/нормализации/частоты). Теперь ожидаемые cohorts
берутся из explicit native specification, проверяется полная матрица и отсутствие
дубликатов. Baseline counts остаются прежними. Все новые случаи проходят те же
primary/transfer/certificate/corruption проверки; они не фильтруются из анализа.

Не допускается len>=N, автоматически вывести успех из найденного набора или
считать отсутствие целой объявленной группы нормальным. Initial threshold100
проверяется как условие конкретного engineering fixture, не общий default.
Ни одного scientific tolerance/threshold/probe window не изменено.

Подготовлены прежние119 checks и5 существующих actual-domain CLI controls.
До выполнения на worker нет runtime приёмки этого reader source. Joint ASan и
вся научная/режимная матрица остаются открытыми.
