Проверено06.11: corrected A2 —36/36 через production validation.run_suite на Elder и M40, без skips/failures/errors. Проверены все11+15 archive members каждого worker и340 source/fixture hashes каждой попытки. Production projection между A1/A2 побайтно неизменна: исправлен только неверный контроль порядка и временный runner. [Независимая сверка](PipelineConditionBindingVerification.json). [Elder A2 primary](../../../Reports/StructTrain/TimeLearner/s10-pipeline-condition-readers-elder-a2/bundle.json), data `fab049d705d6b8387c8fb5712c9163f47e9c775b`; [M40 A2 primary](../../../Reports/StructTrain/TimeLearner/s10-pipeline-condition-readers-m40-a2/bundle.json), data `791220378928fab9fa6e26bcd537941db4dab403`. Оба неуспешных A1 сохранены в тех же data commits. Fresh closure/released подтверждены. Это приёмка декларативной projection/reader части, не реальных новых schema2 native runs, не effective-factor attestation и не всей production integration. Ветка содержит pending C++ slice и не объединяется в develop по одним Python проверкам.

# ConditionSpec из фактической декларации managed pipeline

Постановка этапа10; реализация в отдельной pending ветке, runtime-приёмка ещё не выполнена.
Это не доказательство выполнения всех условий эксперимента или готовности всей очереди.

Новая `timelearner_managed_pipeline_job` schema2 сохраняет набор полей schema1:
kind/schema_version/attempt_id/phases. Она требует `condition-binding.json` до
первого Train. Schema1 остаётся историческим operational workflow и не получает
нового attestation задним числом. ControllerVersion, native training job schema,
ModelSpec и observation schema этим не меняются.

`pipeline_condition.build_binding` валидирует полную декларацию через production
preflight, затем строит все11 role artifacts существующего ConditionSpec.
Сохраняются полные model/profile declarations, начальная физика, protocol/windows,
search/tolerances/budgets, transformation/PostTune/calibration/evaluation requests,
порядок и критерии. Полная semantic declaration дополнительно остаётся в
training_plan artifact, чтобы непроецированное научное поле не исчезло.

Operational attempt/run/trial IDs исключаются по существующему явному набору
PROVENANCE_KEYS; каждый исключённый путь записывается. Удаляется только signing
digest верхнего Train job, содержащий run_id; referenced model/profile digests
не удаляются. Kind/schema самого coordinator envelope также не являются научным
фактором. Sample IDs, labels, pattern hashes, ISI и порядок проб сохраняются.

Algorithm artifact включает implementation/owner и native runtime content
identity: executable/libraries/compiler/config/semantic build flags, без deploy paths.
Перенос идентичных файлов не меняет condition; иной binary content меняет.
Полные исходные Git closure и analysis code остаются в runtime/phase manifests:
content identity не является доказательством исполнения произвольного процесса.
Разная сборка с изменившимися bytes может дать другую condition даже при том же
исходном коде; эквивалентность таких runtime автоматически не выводится.

Journal created связывает condition fingerprint и весь binding hash с полными
operational specification/runtime hashes. Scan/audit/continue/reconciliation
заново строят projection из сохранённой декларации; вручную подставленный,
повреждённый либо отсутствующий binding отклоняется для schema2. Downgrade к
schema1 не получает condition_declaration_bound или научной attestation.

Новый audit выдаёт condition_declaration_bound=true и fingerprint, но сохраняет
condition_identity_attested=false. Сам binding явно declaration_only=true,
effective_model_verified=false/native_execution_verified=false. Actual phase
workers по-прежнему проверяют собственные job/model/observation связи; полное
semantic сопоставление всех effective факторов и внешняя execution attestation
остаются открытыми. Наличие fingerprint не разрешает Test после stopped Train.

Тестовый corpus содержит ровно четыре исходные coordinator declarations и один
общий побайтно идентичный runtime из опубликованного data26a602e84adef89056021a671055d8272330d810.
Сохранены source member/raw/gzip hashes, всего125343 compressed bytes. Это только
metadata fixtures существующих прогонов, не новые эксперименты или случайные повторы.
Проверки запускаются на Elder/M40; реальные новые schema2 coordinator runs и их
закрытие/публикация необходимы отдельно до приёмки production integration.

## Совмещение pending ветки с принятым develop

Перед реализацией выполнен merge develop990361d44a24ea6a2a541ccf0fc7d15a98504abf
в pending Root86118630da6fed4763715209e4405980cad59f0d. Merge
8d4916940a6830df152ecaa5c6bfbbfef7a0070e сохраняет оба набора CLI formats
и обе секции README; два конфликта разрешены объединением. Все package Python
файлы прошли локальный AST parse, без выполнения тестов или расчётов.
Pulse остаётся pending12d, Bin обновлён на принятыйf12. Серверные source/runtime
работающих заданий не менялись. Merge не включён в принятый develop; его
native code всё ещё требует оставшейся ASan приёмки и полного плана.

Первая серверная попытка A1:36 tests на каждом worker, один неверный контроль
требовал смены identity после разворота palindromic target/foil/foil/target.
Fingerprint правильно остался прежним. Контроль теперь сохраняет это равенство
и отдельно проверяет реальный циклический сдвиг порядка. Production projection
не ослаблен. Временный worker дополнительно отказал при JSON сериализации
объекта failed TestCase; следующий использует production validation.run_suite.
Оба A1 outputs сохраняются целиком; моделей эти проверки не запускали.
