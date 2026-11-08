# Native declared-window basin diagnostic artifact, schema1

`declared-window-basin-diagnostic.json` сохраняет параметры фактического вызова
bridge, его outcome и hash-bound ссылки на primary group. Это diagnostic-only
запись, не training proof и не независимая аттестация исполнения native scheduler.
Schema1 до первого release дополнена без изменения selector/physics/outcomes.

Обязательные параметры `specification`: schema_version, method_id, group_id,
input_id, assigned_input, channel, window_begin_offset, window_end_offset.
`geometry_policy`: schema_version, maximum_inputs, maximum_samples,
maximum_total_samples, repeatability_absolute. Minimum amplitude записан явно.
Дублирующие flat method/group/input/channel/window поля должны совпадать с ними.

`status` имеет canonical string rejected/completed/causality_rejected;
status_enum соответственно0/1/2. `geometry` содержит validity/reasons, каждый
полный candidate с actual maximum, measured valley anchors, control presences,
necessary ordinals, candidate status/reasons, selected_candidate и measured_maximum.
Для отсутствующего geometry/measured результата используется null. Flat outcome
и measured maximum должны совпасть с вложенными значениями.

`witness_binding` связывает group_id, source_pattern_sha256, base/effective model
revisions, protocol_revision и:

- `group`: relative_path=group.json, exact bytes и SHA256 записанных JSON bytes;
- `portable`: relative_path=matched-witness.json, bytes/SHA256 либо null;
- `source_specification_sha256`: CanonicalModelDataSha256 portable specification
  с length-framed-utf8-binary64-v1 либо null;
- `complete_group`: true только при наличии законченного portable envelope.

Полный matched-witness связывает source/policy/context, все N+2 native packets
и canonical CSV hashes. Не нужно восстанавливать параметры из C++ fixture или
предполагать intended ISI равными actual generator timestamps. Writer сначала
записывает/flush group и portable, затем diagnostic record с их точными digest.

Предобъявленный native14 inventory даёт10 complete records (8 ordinary и2 merged)
и4 partial rejection records (stop/edit). Partial имеет portable=null,
source_specification_sha256=null, complete_group=false, rejected status и null
geometry/measurement. Он никогда не выдаётся за replayable полный N+2 witness.
Проверка Python reader будет отдельно фиксировать полноту replay, а не просто
успешное чтение JSON. Scientific verdict остаётся null, eligibility=false.
