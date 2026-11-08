# Штатный запуск проверок Python и удаления подтверждённых дубликатов AR

`Scripts.StructTrain.TimeLearner.owned_python_job` заменяет подготовку новых
исполняемых TEMP-программ для этих двух узких операций. Он принимает JSON,
а запуск, ограничения и завершение всей группы выполняет существующий
`contained_runner.execute`. Старые результаты и их производители не меняются.

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
Публикация Git и независимая проверка остаются отдельными действиями после closure.

## Подготовленные проверки

Новый metadata-only inventory: 10 `OwnedPythonJobTest` и существующие 6
`StaticArchiveCleanupTest` (точный class name читается из actual pinned source при
составлении suite). Проверяются strict schema/limits/digests, отказ native action
и traversal, callbacks до side effects, закрытый observer pipe, symlink parent,
dangling retained alias, Git blob bytes и source epoch/drift. Эти тесты не запускают
новые systemd units и не используют модели.

Отдельный адресованный suite143 проверяет неизменённый port source
`76ffc4c566a7c6113eb5131de398467103e320fa`: 67 wire +39 collector +30 declared time
scales +7 lossless ConfigDocument. Для последнего передаются как fixture реальные
Project.ini из pinned Bin, с отдельным immutable manifest. CLI проверяется из этого
же source и должен сохранять conditional/unknown semantics. Успех адаптера16 не
подменяет успех143, удаление13 AR или перенос старых Bin entrypoints.

На момент подготовки документа все эти новые inventories только сформированы
по исходникам; серверный PASS, удаление AR и retirement Bin2 не утверждаются.
