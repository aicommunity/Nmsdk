# Привязка коллектора к фактической попытке

08.11.2026. Реализация `Scripts/StructTrain/TimeLearner/collector_provenance.py`.
На этапе исходной подготовки серверные регрессии ещё не выполнялись. Этот
документ не добавляет приёмку обучения, сборки или всего плана рефакторинга.

Причина изменения — два конкретных отказа сборщика доказательств Elder A3.
Первый запуск коллектора через stdin не мог прочитать свой `__file__`. Затем
collector-a2 сохранил в `90af73022c3c0955eaafa368ef5a7e00702147b1` журнал A2
под меткой A3. Независимая проверка обнаружила это до приёмки. Исправленный
collector-a3 опубликован как `ec2935e8511f89da6457e896dba21099037b796c`.
Worker/controller bytes исходного численного A3 в двух архивах идентичны;
12 passed / 1 failed / 193 not run и отсутствие шести экспортов сохранены.
Старые артефакты не исправляются и не переоцениваются.

## Контракт входов

`capture_owned_supervisor(container, supervisor_log=..., worker_stdout=...)`
требует явных абсолютных путей. Имя supervisor-файла ничего не доказывает.
Worker stream должен быть `stdout.log` именно переданного contained-каталога:
это штатный output route `contained_process`, а не поиск по похожим именам.
Supervisor STARTED и worker GATE — разные роли и разные потоки.

Сначала читаются request, binding и оба лога. Каждый файл должен быть обычным,
не проходить через symlink и помещаться в явный лимит (по умолчанию 16 МиБ
на вход). Открытый inode, размер, mtime и ctime проверяются до/после чтения и
против пути. Изменение или замена приводит к отказу; JSON с повторными ключами
и нечисловыми JSON-константами не допускается. При необходимости большего
лимита вызывающий код должен явно объявить новый бюджет.

Проверяются существующие content-digests request и binding, связь
request SHA → binding, unit, invocation, cgroup, PID и start ticks. Во всём
supervisor-файле должна быть ровно одна STARTED JSON-строка; весь её объект,
включая digest, должен совпадать с `owned-unit.json`. Отсутствующая, повторная,
неоднозначная, повреждённая или чужая STARTED-строка запрещает упаковку.
Это проверки целостности и согласованности, не криптографическая аутентификация.

`CapturedCollectorInputs.materialize(owned_root, staging)` пишет уже прочитанные
bytes и descriptor в новый непосредственный дочерний каталог `owned_root`.
Поскольку value object можно создать вручную, до первого mkdir/open повторно
проверяются ровно четыре допустимых уникальных basename, неизменяемые bytes,
размеры/хэши, request/binding/STARTED и совпадение полного descriptor. Произвольные
имена, повторные роли или несогласованные bytes не приводят к созданию каталога.
Пути проверяются; каталог и файлы создаются без overwrite через directory fd.
Исходные журналы повторно не открываются. Результат — явный словарь logical
member → staged Path для существующего `create_native_bundle`; его формат и
повторная проверка хэшей остаются прежними. Materialize требует Linux directory
fd; поддержка Windows Job Object этим модулем не заявляется.

## Источник и область проверок

`capture_git_case_inventory(source_root, selections=..., inventory_documents=...)`
использует чистый фактический `runtime.source_closure`, HEAD и Git blob bytes.
Для выбранных C++ файлов проверяются также реальные worktree bytes; в конце
HEAD и source closure проверяются повторно. Все вызовы Git используют
`GIT_NO_LAZY_FETCH=1`: недостающий объект означает отказ, а не сетевую загрузку.

Каждый selection содержит ровно `path`, `suites`, `dialect`.
`suites=null` выбирает распознанные случаи файла; непустой список выбирает
явно названные suites. Поддерживается только
`literal-TEST-and-attempt-invalid-budget-v1`: строковые literal `TEST(Suite,Name)`
и существующий `ATTEMPT_INVALID_BUDGET_TEST`. Тело `#define` не считается
случаем; четыре фактических вызова macro разворачиваются в четыре ID.
В самой единственной definition этого macro допускается ровно одно gtest
объявление `TEST(TrainingInvalidBudget,name)`. Добавленное второе TEST или другая
семья не могут молча уменьшить счётчик: dialect отказывает. Неверный UTF-8
supervisor-журнала также даёт структурированный EvidenceError до упаковки.
Это не общий интерпретатор C++/gtest: TEST_F/TEST_P/TYPED_TEST не поддерживаются,
и compiled `--gtest_list_tests` с фактическим JUnit всё ещё обязательны. При
`suites=null` любой такой macro отклоняет весь файл; при явном списке отклоняется
его присутствие в выбранной suite. Такие объявления в других suites сохраняются
как `outside_declared_scope` с `coverage_attested=false`, не входят в IDunion и
не являются заявлением покрытия.
Число 206 не зашито в helper; оно получается из зафиксированного набора
74 + 23 + 105 + 4 в регрессионном source pin.

Для опциональных inventory documents задаются `path`, `source_path` и при
необходимости `claimed`. Документ читается из Git того же фактического commit;
`source_sha256` сравнивается с вычисленным TU hash. Переданная копия `claimed`
только проверяется и никогда не становится источником authoritative полей.
Cases/count сверяются с literal source inventory. Для sparse Git-доноров
нужные маленькие Docs blobs следует доставлять явно, не материализуя кампании.

## Descriptor и интеграция

`describe_collection` выпускает schema 1 с отдельными полями:

- `collector_tool_source`: Git commit и фактические bytes самого Python helper.
  Для Scripts projection это не проверка gitlinks всего SDK.
- `planned_source`: явно заданный план; он не заменяет фактические источники.
- `actual_sdk_source_closure`: наблюдаемый текущий SDK, либо null.
- `actual_compiled_runtime`: предоставленный runtime manifest после проверки
  source association и fingerprint, либо null. Это само по себе не аттестация
  успешной компиляции или загрузки файла процессом.
- Обязательный `compilation_state` принимает только `not_started`, `not_observed`
  или `built`. Первые два требуют null runtime; `built` требует manifest.
  Фаза объявляется по реальным producer records и не выводится из имён/плана.
- `declared_source_inventory`: набор, полученный из Git; `observed_test_inventory`
  остаётся null. Успех сборки, compiled inventory, kernel closure и успех тестов
  модуль не подтверждает; `scientific_verdict` всегда null.

На M40 preflight c19 Python tool/planned root540 и фактический старый SDKd920
должны оставаться разными. Поскольку новая сборка не началась,
`actual_compiled_runtime=null`; 206 плановых случаев нельзя объявить выполненными.

Будущий collector перед `create_native_bundle` обязан:

1. Внешним штатным backend доказать закрытие точной группы и освобождение lease.
2. Передать точные пути журналов и сравнить полученный binding с этим closure.
3. Получить Git inventory и отдельный provenance descriptor; при preflight-отказе
   сохранить null для новой компиляции и фактически не выполненных проверок.
4. Упаковать staged copies `materialize`, provenance descriptor и неизменённые
   первичные данные; после упаковки выполнить независимую проверку.

Helper не запускает backend, не снимает блокировки, не переименовывает входы,
не исправляет старые артефакты, не строит модели и не синтезирует primary.

## Регрессии

`tests/test_collector_provenance.py` использует только сохранённые metadata
из ec293 / 90af / 153751 / c19 и выбранные настоящие Git blobs root540/root6dac.
Fixture manifest содержит полный источник каждого member, размер и SHA256.
Thin Git pack содержит оба настоящих commit, все tree objects и только нужные
source/document blobs; он не содержит runtime ELF или научные CSV.
В unit tests источник SDK подставляется из сохранённых source-closure записей;
Git bytes и файловые изменения проверяются в отдельном временном Git fixture.
Это не повторная проверка SDK gitlinks на сервере и не моделирование физики.

Обязательные отрицательные контроли включают чужой A2 log при binding A3,
неоднозначный STARTED, tamper, гонку чтения, чужой stdout route, выход staging
за owned root, исходный stale nested fc9 против Git05f из A2 и подмену статуса
preflight новой компиляцией. Тесты запускаются отдельным ограниченным серверным
metadata job после review исходного pin; локально разрешены только source/AST/Git
проверки. SDK/cache Elder6dac и текущий M40 numerical job не используются.

Исходный список 33 metadata-проверок из be710 superseded новым списком 38:
добавлены пять конкретных границ — ручной path escape, повторная роль,
несовпадение bytes/descriptor, второе TEST в macro и неверный UTF-8. Это изменение
source/test inventory; прежний запуск тестов не заявлялся и не переоценивается.

Первый metadata gate38 на M40 с исходниками2919 выполнил 38 случаев:
37 passed / 1 error / 0 skipped. Отказ full206 source inventory возник из-за
TEST_P в другой, не выбранной suite того же файла. Исходный отказ и kernel
closure сохранены в `0c2f50da9641f6dc9d31867a617eb5766ff5996d`; helper под
проверкой не использовался как источник приёмки собственного неуспешного gate.
Следующий источник исправляет только границу явно выбранной области и добавляет
39-й контроль: выбор настоящей параметризованной NativeLearnerExecution всё ещё
отклоняется. Прежние исходники, fixtures, результаты и критерии не переписываются.
