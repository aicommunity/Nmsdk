# Запрет новых loose scripts в TimeLearner Reports

`publisher.py` проверяет новые явно объявленные artifact sets до staging и
перед первым/каждым push. Область — `Reports/StructTrain/TimeLearner`, включая
вложенные пути и регистр имени каталога. Известные script/build suffixes,
`CMakeLists.txt`, Git100755 или начальный `#!` (также после UTF8 BOM) запрещены.
Остальные artifact types проходят прежнюю hash/regular-file/Git closure проверку.
Это не миграция Rdk CMake/product sources за пределами Reports.

Отказ: `loose_report_script_forbidden:<reason>:<path>`. При обычном preflight
отказе не добавляются новые пути в index и не публикуется ни один child/root ref.
Caller должен отдельно подготовить compact primary archive или declarative job
spec; publisher не переписывает bytes/имена/manifest. Существующие staged
изменения caller сохраняются. Прежний post-add filter-mismatch контракт
остаётся прежним: index reviewable, commit/push после отказа запрещён.

Для записанных файлов проверяется Git index/tree mode. POSIX executable bits
учитываются до add только при действующем core.fileMode; Windows X_OK не
используется как признак исполняемого source. Shebang/hash вычисляются из одного
потокового чтения artifact bytes. При публикации проверяются immutable Git blobs,
а не рабочие копии и не ожидаемые файлы producer.

Чтение старых artifact sets через `verify_artifact_set` и `publication_plan`
без enforcement flag сохраняет прежнюю evidence-интерпретацию. Новый
`publish_closure` включает policy, поэтому read-only integrity не превращается
в право повторной публикации loose script. Schema1 inventory не содержит и
его аттестацией не является. Сам архив может содержать точные provenance source
bytes; блокируется loose executable, а не первичная историческая информация.

Новые12 tests в `tests/test_report_artifact_policy.py` используют реальные Git
indexes/commits/children/local bare remotes. Проверяются compact archive/models/
metrics/figures, mixed-case suffixes и scope, nested paths, BOM/shebang,
script-named inventory, Git755 binary, историческое read-only чтение,
неизменность staged caller data и отказ до pending child/root pushes.
Все прежние `test_publisher.py` выполняются как regression gate. Локально —
только AST и Git/source review; серверная приёмка на обоих workers ожидается.

Исторические109 loose Reports scripts, найденные four-tree snapshot27d6e4b,
остаются отдельной конечной группой удаления с Git retrieval manifest и review
их consumers. Этот guard сам по себе не завершает этапы9/10 или весь план.
