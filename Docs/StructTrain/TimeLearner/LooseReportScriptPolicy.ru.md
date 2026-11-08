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
только AST, Git/source и metadata review. Приёмка завершена на обоих workers:
32/32 methods на каждом (20 прежних publisher regressions и12 новых).

Исторические109 loose Reports scripts, найденные four-tree snapshot27d6e4b,
остаются отдельной конечной группой удаления с Git retrieval manifest и review
их consumers. Этот guard сам по себе не завершает этапы9/10 или весь план.


## Приёмка и сохранённые неуспешные попытки

Root `91323406ce458186baa1fa19e19f7b2249b617e6` принят на M40 A2 и Elder A3.
[Независимая квитанция](LooseReportScriptPolicyVerification.json) проверяет
32 exact IDs на каждом,412 source hashes по Git, точные worker byte hashes,
реальные runtime mappings и kernel closure. Primary: M40
`cf8d8cda5ddd634c45a27c9fe1fd3fe94efe32dd` (86 members,38 480 bytes),
Elder `9e92627785004703ac133602bb138777beb3342a` (103 members,39 568 bytes).
Оба XZ используют32MiB dictionary. Scientific verdict остаётся null; модели
и C++ не рассчитывались/не собирались для этой software-проверки.

[Журнал попыток](LooseReportScriptPolicyAttempts.json) разделяет assertions,
execution, cleanup и publication. A1 прошли31/32: Git755 fixture имел index755
при filesystem644 и потому правильно сработал более ранний dirty-source gate.
Исправлен только fixture POSIXchmod; production policy между A1 и принятым
снимком не менялась. В A1 операционный wrapper дополнительно пропустил
обязательный release note и оставил две legacy controller reservations.
Их не переоценивали в успешные тесты или зарегистрированный managed graph.

После отдельного source/request/controller/kernel аудита выполнена одноразовая
административная reconciliation ровно этих двух собственных tokens. Raw SQL
preimages, точный driver source, source audit, до-commit proof и committed event
сохранены в primary. Проверены controller PID/start/boot/uid, все412 исходных
source hashes, закрытие известного child cgroup и отсутствие живого owner.
В одной atomic transaction изменены только state/updated/release_note нужной
строки; schema/capacity/metadata/остальные rows неизменны. API guards не ослаблены,
процессы и данные не изменены; `registered_child_graph_attested=false` сохранён.
Это конкретный операторский known-source case, а не универсальное правило
автоматического освобождения по произвольному списку units.

Elder A2 отказал до запуска тестов, пока единственный slot занимала старая
reservation. Отказ сохранён; после reconciliation выполнен новый A3. M40 A2
не повторяли. До вычислений A2 также был bootstrap type error в чтении
/proc/stat; подтверждённые неизменные supervisor bytes и отсутствие job/lease
проверены перед первым compute. При сборе отчёта исправлена лишь ошибочная
догадка collector о filename binding: используется supported inspect API.

На Elder один Git tree/index command возвратил0 со stderr invalid-object для
не материализованного старого Docs blob. Этот diagnostic не скрыт и не назван
чистым publisher PASS. Независимый Git diff подтвердил ровно три новые artifact
записи, все прежние tree entries сохранены; source/tests/первичные данные не
пересчитывали. Полная производственная интеграция публикации остаётся отдельной
приёмкой. Operational status тестовых stderr needs_review также не переименован.

Следующий обязательный инфраструктурный шаг — единый maintained Python
verification worker по declarative specification, использующий существующие
contained_process/runner/runtime/reservations APIs и UTF8/byte SHA. Повторять
adhoc launcher-body генерацию для новых gates не следует.
