# Исторические исходники заданий внутри Reports: внешний индекс извлечения

Адресный подэтап 9, 109 файлов, исходный корневой снимок
`7a46c3a9068f6c50abd87c9616c81c76479efcc5`.
Это commit извлечения исходников, а не доказательство версии кода, которой
выполнялся каждый исторический опыт. Полные пути, blob SHA1, SHA256, размеры,
last-change commits и команды `git show` — в [script_migration.json](script_migration.json).
[Машиночитаемая классификация и consumer review](RootReportSnapshotRetirement-20261108.json)
содержит все 109 записей; прежний FourTreeScriptInventory остаётся снимком своей версии.

Удалены 46 producer.py, 40 publisher-source.py, 8 launcher.py, 2 recovery-collector-source.py,
4 worker.py и 9 фиксированных ASan build/owner-reader queue исходников. Это
снимки исполнения конкретных старых заданий с прежними путями, commits и
предшественниками. Математические анализаторы, reader implementations и
управление процессами остаются в поддерживаемом Scripts/StructTrain/TimeLearner.
В текущем дереве не остаются wrappers или исполняемые копии этих 109 файлов.

Для каждого файла прочитан полный Git blob, проверены AST imports, execution
calls, строковые пути и фиксированные runtime/readback bindings. Полные пути
в остальных root tracked blobs обнаружены только в прежнем inventory (109 записей);
в согласованных Bin/PulseLib/Rdk tracked trees — ни одного. Проверка basename
и динамических imports/runpy/subprocess в maintained Scripts/Tests обнаружила
только штатное создание собственного launcher.py в contained_process и
строку producer.py в отрицательном policy fixture. Их функциональность сохранена.
Девять queue sources составляют один исторический dependency group; запускать
их как современные job specs нельзя. Наличие внешнего неучтённого consumer
произвольной исторической копии не исключается этим анализом.

## Неизменность исторических пакетов

Ни один исторический README, report narrative, bundle, SHA256SUMS, manifest,
source-hash inventory, request/runtime receipt не переписан. Все модели,
численные первичные данные, архивы, рисунки и остальные Reports blobs сохранены.
Ссылки и хэши удалённых loose sources в старых квитанциях относятся к полному
историческому Git tree выше. Для извлечения следует использовать commit/path
из migration manifest. Текущее разреженное после удаления loose sources
содержимое каталога не выдаётся за заново полный исторический пакет.
Этот внешний индекс намеренно не изменяет hash-bound прежние доказательства.

Новый publisher уже запрещает loose scripts в новых artifact sets: источник
следует упаковать в primary archive либо выразить декларативным job spec.
Существующие архивы остаются первичными историческими артефактами.

## Приёмка и ограничения

Manifest содержит 354 записи: 352 retired и 2 moved, complete=false.
Перед merge: production history verify-migration всех 354 записей на обоих
Linux workers; отрицательный Git fixture с восстановленным source path обязан
дать exit2/migration_old_path_still_present без положительной квитанции;
Git diff обязан содержать ровно 109 Reports удалений и новые/обновлённые
maintained Docs, без изменений остальных Report blobs и production sources.
Старые скрипты не материализуются и не запускаются; модели не рассчитываются.
Серверная приёмка на момент этого source commit ещё pending.
Полный этап9, научный результат и весь план этим подэтапом не завершаются.
