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

## Приёмка завершена на обоих workers

Проверенный source root: `0153d505861403ec3dc2b721a6b0321b270e2e69`.
Elder evidence: `3f3aa18a67cc69fe2ad1912bec06300a2e49ca88`;
M40 evidence: `f342e24c5f614551541fea48cf77bb1be7898a16`.
Оба production CLI реально извлекли все 354 старых blobs из отдельных Git
object stores, сверили размер/SHA и отсутствие старых путей. Restored-path
negative fixture на обоих отклонён (exit2, migration_old_path_still_present,
положительный output отсутствует). Это 354 retrieval records, а не 354
научных теста. Все 109 старых исходников дополнительно прочитаны и AST-parsed;
они не материализованы как исполняемые файлы и не запускались.

Git scope на проверенном source commit — ровно 109 удалений и четыре
maintained Docs изменения. Остальные 86126 Reports blobs совпадают; production
Scripts/Tests/native sources и gitlinks не менялись. Все 412 production Python
source hashes на обоих workers независимо сопоставлены с Git, before/after
совпадают. Worker reserve/release находится внутри его собственного bounded
unit: PID/start_ticks lease owner совпадает с kernel binding. Оба unit закрыты,
lease released с обязательным пояснением; managed child graph этим не
объявляется зарегистрированным. Выполнялись только синхронные Git/production
history CLI subprocesses; C++ builds и расчётов моделей не было.

Каждый compact archive содержит 43 members, dictionary 32 MiB. Elder archive
197068 bytes/SHA256 `72b1155b88970bf04a88bc4341b93bd8cf74e07f82d79ef6dad075415163c23d`;
M40 archive 197444 bytes/SHA256 `e5049a24e684241265f1218bcecea4d3731747ea7245ccfef9bcc7a6c3b7b273`.
Outer/member hashes, exact source hashes, identity/closure и negative receipts
проверены отдельно; [машиночитаемая сверка](RootReportSnapshotRetirementVerification-20261108.json).
Первый collector отказал до упаковки из-за неподдерживаемого dictionary16MiB.
Его исходные bytes и отказ сохранены в архивах; новая p2 упаковка использует
штатный32MiB. Успешные CLI-проверки не перезапускались и не переоценивались.

На Elder после приёмки отдельный source занимает37146624 bytes, job913408,
evidence object store5521408; измеренное свободное место488349696 bytes.
Это не разрешение больших сборок при почти полном диске. Capacity/schema и
чужие задания не менялись; удалений серверных данных в этом подэтапе нет.
Полный этап9 и вся итоговая научная приёмка остаются незавершёнными.
