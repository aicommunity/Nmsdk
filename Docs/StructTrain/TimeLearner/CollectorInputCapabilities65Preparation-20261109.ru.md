# Подготовка отдельного metadata65 gate

Статус: source 2caf доставлен на M40 и проверен read-only; подготовка PLAN A1
отказала до test dispatch. Новый PLAN A2 подготовлен только как Git/JSON/AST;
его server preflight и все 65 tests ещё не выполнялись.
Исполнение — только штатный `owned_python_job` / validation,
без нового launcher/orchestrator. Dispatch требует source/request review и
свежего readback подготовки.

Первый metadata-only pin `110f016a71daf835419272c03d384a1f11fe6d9a`
не использовался на сервере: локальная проверка выявила, что вложенные хэши
suite/request/source-manifest/dependencies были рассчитаны по Windows CRLF,
а Git сохраняет LF. Он сохранён в истории. Текущие привязки рассчитаны по
точным LF bytes; request ссылается на canonical Git suite. Код 2caf и все 65 IDs
не меняются. Перед передачей проверяется равенство staged Git blob bytes и
записанных привязок; материализация берёт только эти Git bytes.

Validation source frozen: `2caf3ad467b7f8b82c7f1b42c4680cbe0061bdae`.
635 tracked Scripts, 444 package Python files,
FP `295a7335089c7cab55f4efb9fefbd0952d2598a478d561a2d7535fd5258f8317`.
Отдельный controller ToolCEC
`cec33f2fcceb8c8f815e3494173bf48dcd39ed6c` остаётся в принятом
`source-channel-lt-overview-tool-m40-a2` (632 Scripts / 441 package Python).

Canonical paths под `/media/user/Data/TimeLearnerRefactor`:

- `source-collector-input-capabilities-m40-a1`: уже доставленная immutable Git-only projection;
- `plan-collector-input-capabilities65-m40-a2`: новый отдельный docs-only plan donor;
- `readbacks/s10-collector-input-capabilities65-m40-a1`: fresh owned job output.

Source materialization: все 635 Scripts и ТРИ original Git control files
`.gitattributes`, `.gitignore`, `.gitmodules` — 638 tracked files. В manifest
`records` перечислены и Scripts, и controls; сравнение с production
`_source_snapshot.files` берёт ТОЛЬКО prefix `Scripts/` (635), controls проверяет
отдельно по Git bytes. Полные root trees/gitlinks доступны как metadata; SDK,
сабмодули, Bin/Configs и пользовательские worktrees не материализуются.
Без alternates, lazy fetch и замены source commit текущим main.

Plan donor содержит пять JSON этого preparation stem, этот MD и controls из
своего docs-only commit. Flat `suite.json` и `request.json` создаются new-only из
EXACT соответствующих Git blobs после всех read-only checks и prep reservation.
Source commit остаётся 2caf; plan commit связывается отдельно после его фиксации.

Неуспешный server PLAN A1 `ac4c22203c9dced37631bef07308f24e61d7df40`
и `plan-collector-input-capabilities65-m40-a1/prepared-metadata.json`
сохраняются без перезаписи. Его producer `8c69f08f…` сравнил фактически
доставленный упорядоченный список patterns с порядком ключей `plan_files`:
`sort_keys=True` изменил порядок вложенного map. Read-only audit подтвердил
неизменные 635 Scripts / 444 Python / FP295a, все controls и шесть Docs;
других расхождений не обнаружено. Lease `6b942305-f599-43a7-a964-89820d972cbf`
released; flat `suite.json`/`request.json` и test job не создавались.
Полные SHA ошибки и квитанции записаны в JSON `preparation_history`.

В A2 `dependencies.projection.source_patterns` и `plan_patterns` — явные
массивы. Их порядок сравнивается буквально, без генерации из map, сортировки
и замены сравнением множеств. Сериализация с `sort_keys=True` может менять
порядок полей объекта, но обязана сохранять порядок каждого массива.
Новый namespace и новый preparation job сохраняют отрицательную A1 историю;
код 2caf, все 65 IDs и ограничения тестового job остаются прежними.
Адресная server regression этого operator-контракта будет отдельной от 65:
сохранение массива при sorted-key serialization, отказ при перестановке
patterns и проверка фактических Git controls. Она пока не запускалась и не
засчитывается в metadata65.

External fixtures отсутствуют: прежние 39 tests используют committed
`tests/fixtures/collector_provenance/actual-metadata.json.gz` и
`source-git-objects.pack` внутри source projection. Новые 26 tests создают только
own temporary text/Git metadata fixtures. Никаких actual CSV/model inputs нет.
`TIMELEARNER_REPORT_TEST_DIR`/TMPDIR не объявляются immutable fixture bindings;
штатный worker задаёт свой owned TMPDIR.

Kernel budget: 512 MiB, tasks32, wall240s; output cap128 MiB, physical free floor
512 MiB. Prep cap128 MiB incremental; перед подготовкой требуется минимум
768 MiB disk free и 768 MiB available RAM, новый plan/output отсутствуют,
повторно используемый source совпадает с immutable 2caf,
ToolCEC совпадает с original source и нет пересекающей updater lease. Если
capacity registry настроен, reservation отражает declared memory/disk/slot;
capacity=null сохраняется как факт. После Git materialization выделенный размер
проверяется по факту, лимит не понижается и не заменяется предположением.

Expected literal inventory: 39 `CollectorProvenanceTest` + 26
`CollectorInputCapabilitiesTest`, total65. Exact IDs в suite; success требует
совпадения actual result/log/IDs, zero failure/error/skip, source before/after,
whole owned group closure и exact reservation release. Metadata PASS не даёт
kernel/native/Train/scientific authority новым API.

После принятия65: reanalysis EXISTING closed53 через общий helper, затем
публикация EXISTING negative73 с сохранением72/1. Здесь эти tests не
перезапускаются; old53/73 источники, logs, runtime и primary не изменяются.
