# Общие preflight-проверки входов metadata collector

> Последующая [приёмка65 и actual integration](CollectorInputCapabilities65Acceptance-20261109.ru.md) завершена. Ниже сохранена исходная постановка source preparation; её слова «ещё не запускались» относятся к исходному снимку. Maintained production collector CLI остаётся открытым.

Статус: source preparation. Локально выполнялись только Git/text/JSON/AST
проверки. Unit tests и новый server gate ещё не запускались. Изменение не
затрагивает SDK/cache/runtime, learner, алгоритмы, old53/73 source или primary.

Основа Root: `93c582b2b86f55cf05826b446eddcbb003bfc4c5`.

## Исправляемый разрыв общего pipeline

При сохранении уже закрытого reader53 отдельный temporary collector трижды
отказал по своим ошибкам, не перезапуская tests:

1. Suite selectors содержали `module.Class`, collector искал `Class.py`.
2. Metadata-only plan repository ошибочно использовался как ODB исторического
   primary archive; нужные blob objects находились в другом явном donor.
3. После переноса history в protected old input один read остался привязан к
   новому input root. Это произошло до публикационной lease/создания directory.

Все отрицательные исходники/ошибки сохранены в artifact
`8d05058a244c88096f9b41dba3ff4dd2f4aa008c`, prefix
`Reports/StructTrain/TimeLearner/s10-candidate-window-reader53-m40-a1`.
Финальная A4 публикация прошла explicit role preflight. Исправления ниже
переносят эту обязанность в maintained `collector_provenance.py`.

## API и ограничения

### RequiredFileRole и capture_required_file_roles

Каждый вход содержит явные `role`, canonical absolute `root`, безопасный
`relative_path`, exact `expected_bytes/expected_sha256`, `maximum_bytes` и
отдельный `staged_name`. Имя роли/файла не угадывается по basename. Роли,
staging names и physical paths должны быть уникальны; staging имена проверяются
также без учёта регистра. `descriptor.json` зарезервирован.

ВЕСЬ typed manifest и суммарный budget проверяются до чтения первого входа.
Далее проверяются canonical roots, отсутствие symlink в path/ancestors,
regular file, точный размер до body read, frozen stat/descriptor identity, bytes и hash. Отсутствующий
обязательный вход не становится пустым placeholder. Default aggregate budget
64 MiB, конкретный publisher может задать свой explicit предел.

Возвращается `CapturedFileRoles` с уже захваченными immutable bytes.
`materialize(owned_root, fresh_staging)` заново валидирует имена/bytes и пишет
ТОЛЬКО захваченные копии в новый direct-child staging. Используются прежние
directory-FD/no-follow/exclusive-create guards. Исходники после capture не
перечитываются как будто это тот же snapshot. Public construction объекта не
даёт полномочий: некорректные имена/дубликаты/bytes отклоняются до mkdir/open.

Общий `_frozen` читает `observed_file_size+1`, сохраняя budget и before/open/
after checks; большой разрешённый budget не служит размером allocation.

### GitInputRole и verify_git_input_roles

Для каждого Git входа обязательны canonical repository root, exact repository
HEAD40, object commit40, path, blob40, exact bytes/SHA256 и maximum bytes.
Совпадение hash соседнего файла не делает соседний repository источником роли.

Все manifests валидируются до Git read. Затем проверяются HEAD, binding
`commit:path→blob`, regular tree entry, `cat-file -t`, `cat-file -s`, предел
и точное объявленное число bytes ДО чтения body. Body проверяется по размеру/hash, HEAD проверяется
повторно. `GIT_NO_LAZY_FETCH=1` и `GIT_OPTIONAL_LOCKS=0`; отсутствующие objects
не догружаются и не заменяются данными из другого repo. Git errors становятся
structured evidence errors с исходным exception cause.

Default aggregate budget 128 MiB. Результат содержит reference descriptors,
`payload_retained:false`; primary archive не дублируется в metadata bundle.
Оригинальный compressed primary должен оставаться достижимым в указанном Git.

### capture_python_selection_inventory

Аргументы: canonical `source_root`, commit40, explicit `selectors`, frozen
`expected_test_ids` и aggregate source budget (default 8 MiB).

Поддерживаются только literal module и module/class selections. Доступный
source module определяется по exact Git tree paths; `module.Class.method`,
неизвестные/неоднозначные selections, duplicate/overlapping IDs отклоняются.
Source bytes читаются bounded из Git и сверяются с frozen physical module.
Работающий HEAD должен совпадать с source commit до и после capture.

AST dialect: прямые `unittest.TestCase` (включая обычные import aliases),
literal test methods, стандартные unittest skip decorators. Для class selector
прочие классы явно помечаются outside declared scope. Custom/inherited bases,
conditional/dynamic members (включая вложенные tuple/list/starred assignment
targets), `load_tests`, class rebinding/aliasing и method
selectors не подменяются эвристическим whole-file count. Local variables и
closures внутри методов не являются class test members.

Модуль НЕ импортируется, unittest loader НЕ вызывается, test bodies не
выполняются. Это ограниченный literal inventory, а не универсальный анализ
Python программы: actual production loader/result/log IDs всё равно обязательны.
`runtime_inventory_verified`, `tests_executed`, `SDK_source_verified`,
`kernel_closure_attested` и `test_success_attested` остаются false.

## Порядок использования publisher

```text
capture_owned_supervisor(exact owned container + explicit supervisor/stdout roles)
capture_required_file_roles(full required manifest)
verify_git_input_roles(explicit original/code/plan/reference ODB roles)
capture_python_selection_inventory(actual pinned source + suite selectors + IDs)
check actual result/log/closure/released reservation against their exact bindings
ONLY AFTER ALL CHECKS: reserve publication outputs; materialize frozen copies;
create compact bundle and Git commit
```

API сам не inspect/release kernel units/leases, не строит и не запускает tests.
Проверка closure остаётся у штатного containment owner. Raw observations не
нормализуются: например, inspection-derived `heartbeat_expired` может отличаться
по времени даже для released lease. Обе исходные JSON копии сохраняются с
разными hashes; сравнение immutable lease identity/resources/state/release
fields не является сравнением всех observation bytes или свежей kernel proof.

## Приёмка и дальнейшая работа

1. Source review API/schema и exact AST inventory новых 26 tests.
2. SERVER ONLY: новые 26 metadata tests и прежние 39 collector regressions
   (65 literal methods, zero skips/failures/errors), owned request/closure,
   source before/after и компактный Git evidence. Git repos в новых tests —
   отдельные synthetic text fixtures, не models/native observations.
3. После принятия helper gate — metadata reanalysis EXISTING reader53 через
   maintained API без повторного исполнения 53 tests, primary или C++.
4. Только затем negative reader73 publication через те же helpers. Его
   исторический outcome `72 passed / 1 failed` сохраняется, не превращается
   в PASS после успешного metadata preflight.

Ни source preparation, ни эти metadata gates не принимают archive2 wholeCLI,
runtime2 actual exporter, Train/package/certificate или scientific matrix.
