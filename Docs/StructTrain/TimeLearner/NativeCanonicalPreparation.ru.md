# Штатная canonical-only подготовка native acceptance

Это Tool-only модуль `native_canonical_preparation.py` и один закрытый kind `native-canonical-preparation` в existing `owned_python_job`. Source updater не реализован. Existingowner сохраняет единственную lease, heartbeat, disk limits, whole-cgroup execution/closure и recovery. Новый модуль не создаёт supervisor, не запускает модели и не меняет SDK/source/cache.

## Данные

Owner operation: ровно `{kind,plan:{path,sha256}}`. Plan schema1 содержит kind=timelearner_native_canonical_preparation, schema_version, workspace, source, cohort, native_job, prior_bindings, external_output, native_tool, require_fresh_build=true. Source содержит path/fullcommit/namespacebinding; cohort/job/namespace/priors связываются exact rawSHA. Unknown keys, alias paths, duplicate/nonfinite JSON и неверные типы запрещены. Firstrelease namespace поддерживает regular Git modes100644/100755; symlink code явно не поддержан.

Источник — новая SDK956, а не обновление старой. Fresh build/runtime/nativeoutput/controller остаются отсутствующими. Job.preparation заранее указывает на controller/inputs/preparation.json, а execution argv — на controller/inputs/job.json. ExternalPREP отдельный, атомарно свежий. Никакой перезаписи исходного jobJSON послеSHA, hashcycle или преждевременного controller mkdir.

## Namespace

Parent работает только в Tool namespace. Он запускает отдельный `python -I -B <maintained Toolfile> _child ...`. У file-mode child до SDK sys.path допустимы только stdlib imports; __main__ actorfile и егоSHA учитываются отдельно какTool. После явногоSDKpath загружаются восемь стандартных SDKmodules и реальные29transitive Scripts files: каждый path/blob/bytes/hash должен принадлежать SDK и совпасть с4030namespace. Частичная проекция, trackedbyte drift, extra files и смешение Tool/SDK запрещены. Полный codeledger проверяется по реальному Git и filesystem без fakeWorker/копий функций.

Child вызывает действующие SDK prepare_native_module_checks/serialize_preparation/validate_job/configure_arguments. Parent независимо проверяет schema2/rawroundtrip/sourceclosure/namespace/actor/configureargv, затем пишет неизменные canonical/jobbytes и data-only stock owned-native request. Ни один флаг compiled/test/kernel/science не повышается успехом этой metadataunit. Publicnative48 dispatch остаётся отдельным действием после Rootreview.

## Владение и ошибки

Readonly owner observations используют общий Reservations.read_snapshot из382; собственный SQL не добавляется. Standardexistingowner резервирует только directorytrees, readonlySDK/tool/input/dependency/protected paths и writeowncontext/externalPREP. Lease передаётся функцииproduce; она проверяет точного владельца и покрытие путей, включая отдельный каталог исходного plan. До child и непосредственно перед публикацией все original plan/cohort/job/namespace/prior bytes повторно проверяются по исходным SHA; обе карты сохраняются. Все childGit/Python команды синхронные внутри того же ownercgroup. Partialoutput, timeout, nonzero иcapture errors сохраняются; авторестарт/автоочистка отсутствуют. Старые A3source/cache остаются защищёнными; свежая сборка48 не заявляет reuse438objects.

## Приёмка

Текущий исходный patch не запускался локально; выполнены только AST/Git проверки.12новых metadata methods используют настоящие Git SDK fixtures (целые productionScripts,7реальных childrepos, literalTEST metadata) и действительный изолированный Pythonchild. C++ не компилируется, математические модели не извлекаются и не симулируются. Проверки охватывают closed schema, rawdigest/pathalias, separateexternal/internal layout, freshbuild, fullGit namespace/dirty/extra file, isolatedSDK29maps/rawproducer, staleHEAD, hotnamespace refusal и ownerdispatch resources. Existingowner regressions обязательны.

Полная фактическая4030canonical48 наM40 — отдельная интеграционная приёмка после RootfreshSDKproof и metadata tests; только затем возможен native48. Зависимость commonROAPI382 не объявляется принятой до завершения её отдельного66gate. SDK956, nativeworker35, native_preparation и owned_native_job исходники этим patch не меняются.

## Metadata25 A1 и исправление fixture

A1 выполнил 13 существующих owner tests успешно; setUpClass нового класса завершился ошибкой до всех 12 новых методов (12 not-run). `git archive HEAD Scripts` в намеренно частичной Root-проекции запросил посторонний отсутствующий `.cursor/rules` blob через обработку archive/attributes. Это ошибка подготовки fixture, не результат canonical producer. Production owner/canonical не изменены. A2 fixture читает только `ls-tree -r -z HEAD -- Scripts` и соответствующие blobs одним `cat-file --batch` с GIT_NO_LAZY_FETCH=1; проверяет path/mode/OID, framing, byte lengths, Git blob hashes, сохраняет exact bytes и executable modes. Вне-Scripts blobs не гидратируются. Те же 25 IDs должны быть выполнены заново сервером; локально только AST/Git metadata.
