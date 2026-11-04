# Исторические theory/sim: удаление из текущего дерева

Этап9/12:14 файлов (13 Python и segsim.c) удалены без wrappers/копий.
Retrieval snapshot8b231dae9c9be8405c561ace76a0d2730c49c076 опубликован до
удаления. Каждый полный исходник прочитан; blob/SHA256, last-change commit и
команда git show записаны в script_migration.json. Все JSON/NPY, таблицы и
исторические рисунки результатов сохранены.

model/evalset/klib — standalone binary driver и summation kernels;
run_base/collapse/ei/fast/hp/iti/tau — фиксированные exploratory sweeps;
theory1/theory2 — Gaussian/biexponential/coincidence hypotheses;
figs — фиксированные ../data и ../fig*.png;
segsim.c — отдельная C-модель без Rdk storage/Environment/scheduler.

Часть скриптов выполняет расчёт и пишет результаты при import. Есть зависимость
от рабочего каталога; subprocess не проверяет exit status и полноту stdout;
margin использует target0. Это исторические ограничения, не новая native
проверка или исправление физики. Не переносим этот код в новый pipeline с
вымышленной native equivalence. Аналитическая ценность, данные и код истории
сохранены. Достижимость подтверждают измеренные остатки, а не ожидаемые L.

Буквальные callers/imports проверены в root8b231dae9, Bin99f58da92 и Pulse9ec4566d7.
Найдены внутренние imports и исторические отчёты. E05 comparator принимает
внешний бинарник аргументом и ссылается на другое fastmodels/sim; он остаётся
отдельным pending review, не объявляется современным CLI. Корневой production
пакет не вызывает это семейство. Scan не исключает внешние dynamic paths.

SIGNAL_SHAPE_THEORY и NORMALIZATION_SYNC получают historical/Git оговорки.
Числа, исходные критерии, данные и августовские4/8–6/8 не переписываются.
Standalone совпадение в частных условиях не считается общей native equivalence.
Modern analytical replacement этому пакету не приписывается.

Manifest121 records (119 retired,2 moved), complete=false. Предыдущий path-based
остаток231 уменьшается на14:29 root+188 Bin=217 candidates, нижняя граница review.
До merge требуются production history verify-migration на двух workers:
все121 records, exact changed-tree scope и restored-path negative Git fixture.
Исторический код не исполняется/не материализуется; numerical runtime не меняется.
