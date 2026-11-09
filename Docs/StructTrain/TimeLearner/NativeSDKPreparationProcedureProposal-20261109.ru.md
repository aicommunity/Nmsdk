# SDK source-update и native48 canonical: предложение реализации

Статус: конкретный план/данные, не реализация. Existing SDK f015/Pulsef7,438objects/184flags/cache1281 ещё не менялись. Target code956 и все7gitlinks неизменны. Root отдельно доставил и проверил isolateddonor; это не actual4030SDK readiness.

## Что уже существует

`timelearner_deliver_empty_private_source_v2.py` параметризован, но работает только с пустым новым каталогом. Production `native_preparation.prepare_native_module_checks/serialize_preparation`, `capture_git_case_inventory`, `runtime.source_closure`, `_git_blob/_frozen` и `validate_job/configure_arguments` пригодны для повторного использования. Maintained существующего SDK checkout updater нет. Старый embedded source-updateworker не переносится и не копируется.

Предлагается один Tool-only `Scripts/StructTrain/TimeLearner/native_sdk_preparation.py` и узкий dispatch в existing `owned_python_job`: закрытая операция native-sdk-preparation с plan binding и двумя действиями source-update/canonical. У операции нет собственного supervisor, lease, scheduler или произвольных команд. Stock owner сохраняет контекст/heartbeat/disk/whole-cgroup/closure/recovery. Нужен общий SQL-RO `Reservations.read_snapshot` из382 после приёмкиgate66; частный SQL в каждом job не добавляется. SDK956/nativeworker35/nativeprep/ownednative bytes не меняются. Решение по коду оставлено Root review.

## Источники и изменения

Sourceupdate использует только местный Gitdonor и фиксированные Gitargv: проверкаpacket870f, index-pack, unique preservedref, сохранение всех предыдущих refs/rawshallow entries и detachedcheckout956 с выключенным submodule.recurse. Никакого fetch/remote/submoduleupdate/reset/clean/rebase/авторестарта. Все4030 codebytes,8cleanheads,29actualSDKimports и неизменность438/184/1281 проверяются независимо после операции. Частичное обновление сохраняется как отрицательная диагностика, а не автоматически откатывается или выдаётся за готовую SDK.

Ожидаемые4030 и Root1014 ledgers уже закреплены вV3. Runtime/output/controller/canonical nativeA4 остаются свежими и не создаются sourceupdate action. Diagnostic context и pinnedrequest/temporaryenvironment existingowner могут создаваться в его штатном порядке; это не запись вSDK/canonical/native outputs. Запись SDK начинается лишь после schema/input/path checks, рабочей lease и fresh source/cache guards. Эта постановка не меняет lifecycle existingowner ради обещания полного отсутствия filesystem side effects.

## Canonical и namespace

Подготовка canonical идёт отдельным явным действием после сохранённого sourceupdate результата. Независимый процесс запускает maintained Toolfile как `__main__` с `-I/-B`, stdlib-only bootstrap и явным SDKsys.path до любых Scripts imports. Сам actorfile принадлежит Tool и учитывается отдельно; все реально загруженные29Scripts должны принадлежатьSDK и совпасть сGit. Никакой смены sys.path внутри уже импортировавшего ToolScripts процесса, inlinebody или TEMPкопии.

Child вызывает существующие SDK APIs prepare/serialize/validate/configure. Parent получает проверенные документы и только затем пишет внешние raw canonical/job bytes. Аргументы и job.preparation заранее указывают на futurecontroller/inputs; externalPREP отдельный. Controller не создаётся на этой фазе, JSON не переписывается послеSHA, hashcycle не возникает. Typed stock owned-native request создаётся как данные; dispatch native48 требует отдельного Rootreview. Флаги compiled/test/kernel/science producer не повышаются из-за успеха metadataunit.

## Конкретные данные и проверки

В компактном архиве JSON proposal0240eb... содержит точные поля/пути, ownership, пошаговые проверки и14предлагаемых областей тестирования, а не14уже выполненных тестов. Job draft103aa0... задаёт48cases из102source scope/37leaves/185rules/28protected и прежний profile15. Производственные code paths и regression files названы; реализации пока нет.

Тесты после source review — только на сервере: настоящие маленькие Gitrepos/shallowrefs/donorobjects, path/dirty/missingcontrol/childlink/cache/protected guards, fault injection на реальной Gitгранице с честным partialstate, общий SQL-RO owner API, отдельный реальный namespace process, canonical byte roundtrip и существующие owner regressions. Plaincache testfiles проверяют hash guards и не изображают скомпилированные бинарники. Фактический4030SDK source-update станет отдельной интеграционной проверкой без CMake/native/model; source/canonical/native48 остаются разными этапами приёмки.
