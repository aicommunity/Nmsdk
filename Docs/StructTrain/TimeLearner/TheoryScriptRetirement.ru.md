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


## Проверено на двух workers

Source8154242fe2ee282f7659d29fe7609e7b0f22e1fc: обе production CLI проверки
подтвердили121 record и отклонили negative Git tree с восстановленным evalset.py
(exit2/migration_old_path_still_present, положительный receipt не создан).
На каждом worker сверены20 изменённых путей; Scripts/Tests/App/CMake и все
child gitlinks остались равны принятому root8b231dae9. Отдельные metadata-only
child object handles не являются SDK. Ни исторический script, ни C-модель не
исполнялись; active runtime не менялись.

Elder proof eb78ed1a3f95641b94f562439439dabb9d042a76,
M40 proof18a75a073ebcac5fec64d2512521e8633a8839a6. Все14 members каждого
passing archive и277 Python source blobs независимо проверены локально.
Сохранены также failed A1 archives: production positive121 там уже прошёл,
но scope check пытался делать rename detection и читать непереданные report
blobs. A2 явно использует --no-renames для проверки набора путей. Исходники,
manifest и assertions absence/hash/native-source preservation не менялись.
Worker cgroups закрыты; оперативные leases освобождены после kernel readback.

[Точные контрольные суммы](TheoryScriptRetirementVerification.json).
Это принятый пакет удаления14 исторических источников; общий этап9/12 открыт.
