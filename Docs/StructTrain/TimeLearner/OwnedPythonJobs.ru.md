# Штатный запуск проверок Python и удаления подтверждённых дубликатов AR

`Scripts.StructTrain.TimeLearner.owned_python_job` заменяет подготовку новых
исполняемых TEMP-программ для этих двух узких операций. Он принимает JSON,
а запуск, ограничения и завершение всей группы выполняет существующий
`contained_runner.execute`. Старые результаты и их производители не меняются.

Адаптер Root `edaaa836e27b0ecef1c2f9203fb04ee82d62bd93` прошёл18/18 metadata tests на M40 без пропусков. Evidence `e993215c9d8517222f74928e4e590394f4e8bcb6`, [независимая квитанция](OwnedPythonJobsMetadata18Verification.json): проверены actual log/derived JUnit IDs,625 Scripts files по Git до/после, физическое закрытие owned group и освобождение lease. Контур проверяет две заявленные узкие операции; native runner с detached leaf groups остаётся отдельной работой.

## Границы

Команда `python3 -B -m Scripts.StructTrain.TimeLearner.owned_python_job run REQUEST`
поддерживается только в двух явно указанных Linux execution roots. Требуются
точное имя хоста, новый `job_id`, полный SHA инструмента, лимиты памяти/задач/времени,
физический порог свободного места и предел выделенных блоков каталога результата.
Пути входных файлов абсолютные, находятся внутри execution root и связаны SHA-256.
Повторное использование каталога или неявное продолжение запрещено.

Проверка Python требует отдельный `source.path/source.commit`, SHA файла production
validation-suite и явные fixture bindings. Источники инструмента и проверяемого
пакета могут иметь разные коммиты; оба сохраняются отдельно. Снимок проверяет все
материализованные файлы Scripts против Git blobs, включая бинарные fixtures.
Он не подтверждает материализацию SDK, gitlinks или сборку. Указанный suite должен
отдельно пройти review: адаптер не объявляет произвольные выбранные тесты
безопасными или научно достаточными. Production validation выполняется новым
интерпретатором из каталога проверяемого source; package fingerprint, полный список
ID, отсутствие skip/error/failure и fixture/source bytes до/после обязательны.

Операция `duplicate-static-archives` намеренно ограничена текущим форматом
`Elder_extra13_duplicate_AR_focused_readonly_review`. Она не ищет новые кандидаты.
Хеши plan/review и неизменность production `static_archive_cleanup.py` проверяются;
сам `apply_plan` не меняется. Worker получает write reservation всего execution
root, поддерживает heartbeat и до каждого unlink повторяет старые kernel/owner,
lease/process, canonical/identity/full-SHA target/keeper и retained-link проверки.
Нечитаемые контексты допустимы только при точном совпадении с двумя явно
перечисленными историческими OS-helper identities; universal process absence
не утверждается. Из сканирования исключаются только точные PID/start ticks
собственной launch ancestry и worker ancestry текущего запуска.

Retained aliases читаются через lstat/readlink с проверкой parent canonical path,
без следования ссылке. Только production apply_plan удаляет файлы из плана,
с fsync journal и каталогов. Снимок всех остальных regular files/aliases и всех
keepers должен совпасть после удаления. Следующее выполнение требует нового
review/attempt, даже если прежнее завершилось частичным отказом.

## Владение и результаты

Контроллер сохраняет frozen request и launch ancestry. Внутренний worker допускается
только при совпадении собственной PID/start ticks/cgroup с bound main process.
Единственная строка `STARTED` в явном `supervisor.log` содержит полный actual binding;
ошибка отображения stdout не становится ошибкой управления процессом.
Никаких новых `Popen` или генерации Python-программ адаптер не использует.

`contained_runner` получил только два необязательных callback: `on_started` после
фиксации binding и `monitor` после каждого штатного inspect. Их ошибки проходят
существующий stop/whole-group-closure путь. Старые callers без callbacks сохраняют
прежний интерфейс и поведение. Контроллер следит за физическим свободным местом и
выделенными блоками результата; original guard reason сохраняется отдельно.
Если наблюдающий SSH-канал потерян, попытку сначала исследуют по сохранённым
binding/terminal/kernel, не запускают заново.

Lease освобождает контроллер только через `recover_closed_worker` после доказанного
закрытия всей cgroup. Ни `operation_passed`, ни descriptor не являются научной
аттестацией, proof kernel closure другого запуска или общим утверждением о SDK.
Если запись metadata после execute не удалась, lease может остаться held даже при
закрытой группе; это требует явного fresh inspect/recovery и не считается успехом.
Публикация Git и независимая проверка остаются отдельными действиями после closure.

## Подготовленные проверки

Новый metadata-only inventory: 12 `OwnedPythonJobTest` и существующие 6
`StaticArchiveCleanupTest` (точный class name читается из actual pinned source при
составлении suite). Проверяются strict schema/limits/digests, отказ native action
и traversal, callbacks до side effects, закрытый observer pipe, symlink parent,
dangling retained alias, Git blob bytes, source epoch/drift и закрытие ровно своей
bound group при исключении каждого callable observer hook. Эти тесты не запускают
новые systemd units и не используют модели.

Отдельный адресованный suite143 проверяет неизменённый port source
`76ffc4c566a7c6113eb5131de398467103e320fa`: 67 wire +39 collector +30 declared time
scales +7 lossless ConfigDocument. Для последнего передаются как fixture реальные
Project.ini из pinned Bin, с отдельным immutable manifest. CLI проверяется из этого
же source и должен сохранять conditional/unknown semantics. Успех адаптера18 не
подменяет успех143, удаление13 AR или перенос старых Bin entrypoints.

На момент подготовки документа все эти новые inventories только сформированы
по исходникам; серверный PASS, удаление AR и retirement Bin2 не утверждаются.
Эта строка описывает исходный source-only снимок. Текущий принятый результат18 указан выше; остальные задания принимаются по своим независимым квитанциям.

Первый bootstrap17 @204ec3c завершился отказом до тестов: suite file был передан
как reservation resource, хотя штатный registry принимает directory trees.
Отрицательная попытка сохранена; новая версия резервирует родительский каталог
suite и проверяет этот контракт настоящим Reservations fixture (inventory18).
Evidence отрицательной попытки `b7fd31aa4b8d01559f55431fc2651a088e1d4f75`, [квитанция](OwnedPythonJobsMetadata17NegativeVerification.json): исполнено0 тестов, worker закрыт, leases отсутствуют. В первом collector файл suite был нормализован CRLF→LF; исходный bound suite отдельно проверен по сохранённым raw bytes. Это ограничение явно записано в квитанции, а не выдано за наличие original raw внутри архива. Positive18 сохраняет исходный suite в архиве.

## Подготовка изоляции кэшей графиков — 09.11.2026

Новая source-only версия worker задаёт `MPLCONFIGDIR=worker/tmp/matplotlib`
и `XDG_CACHE_HOME=worker/tmp/xdg-cache` вместе с прежним `TMPDIR=worker/tmp`.
Все три каталога создаёт сам worker; фактические пути сохраняются в
`worker/temporary-environment.json`. Дочерняя production validation получает
эти переменные через прежний `environment`. Новых request fields, действий
или runner API нет. Это исключает зависимость writable Matplotlib/XDG caches
от домашнего каталога user-systemd; исторические jobs и их metadata не меняются.

Новый адресный metadata test вызывает production `_worker`, подменяя только
проверки outer-unit/source и registry для временного fixture. Он запускает
настоящий metadata child с переданным worker окружением; child пишет маркеры
в полученные cache paths. Проверяются пути внутри owned TMPDIR и отсутствие
записей в прежних caller cache directories. Затем тест намеренно прерывает
validation boundary: положительный результат validation или модели не создаётся.
Inventory этого модуля теперь13: прежние12 и один новый test. Прежний PASS18
не подтверждает новую проекцию среды автоматически; шесть неизменённых AR tests
не добавлены в этот адресный scope без отдельной причины. Серверные проверки
нового source ещё не выполнялись. [Точные IDs и Git blob bindings](OwnedPlotCacheIsolationPreparation-20261109.json).

Для будущих14 renderer tests отдельно подготовлен интерпретатор
`/media/user/Data/TimeLearnerRefactor/plot-venv-channel-lt-overview-a1/bin/python`:
это настоящий скопированный executable внутри новой venv, не ссылка на
`/usr/bin/python3.12`. Поэтому штатная canonicalization `file_record` сохраняет
нужный prefix. Site-packages побайтно совпадают с прежней plot venv; imports
Matplotlib3.9.4, NumPy2.5.4 и Pillow13.0.0 проверены на сервере без создания
графиков или запуска tests. Прежняя среда,60 Git-restored native files и source7930
проверены до/после подготовки. Эта operational preparation не является PASS14.
Будущий source с исправлением кэшей получит другой каталог и fingerprint;
подготовленный source7930 остаётся отдельным неизменяемым снимком.
