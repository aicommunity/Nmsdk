# Python integration холодного composite Train: подготовка контракта

Рабочая область — root Python adapters/tests; Pulse/C++ service/codecs и
Console принадлежат отдельному этапу. Исходная точка root99534a29d8e4892ece1b4e13b4827a9ecc0103c6,
reader fix f71c16b46d3c8150eb860be2aeb6949e57247642 объединён merge commit.
Это code preparation, не подтверждённое выполнение новых моделей.

## Зафиксированная декларация

Cold schema6 явно содержит base_schema_version1–4 и composite_measurement.
Это отдельная плоская оболочка, а не вложение candidate-recovery schema5.
Проекция base сохраняет исходные значения и используется только при проверке;
нативному процессу, manifest и hashing передаётся исходный полный cold6.
Legacy cold1–5 не получает нового поведения при отсутствующем selector;
поле composite_measurement в этих версиях запрещено.

Method — declared-window-basin-necessity-v1. Точные поля policy и budgets
проверяются в composite_configuration.py; неизвестные поля не игнорируются.
Нужны как минимум два входа, N объявленных windows, неизменённая native частота
и шаг1/f, record_spikes=false, peak_selection=isolated_window. Context time
comparison tolerance строго меньше половины шага; поисковые допуски при этом
не заменяются timestep или процентом амплитуды. Attempt limits и group limits
имеют разные области действия. Малый положительный attempt budget может
завершить поиск честным budget_exhausted; его нельзя называть сходимостью.

Protocol4 связывается с исходными model/source/protocol IDs, pattern hash,
порядком stimulus/input IDs, объявленными окнами и теми же policies.
wave_assignment=window_only. Смена окна после наблюдения не допускается.
Нельзя подставлять schema3 peak packet вместо полного native N+2 group.
Declaration preflight не создаёт measurement, training certificate или PASS.

Новые JSON counts/schema IDs следуют native codec: конечное целочисленное
числовое значение, не bool, не больше2^53−1, с проверкой требуемой положительности.
1 и1.0 после JSON decoding имеют одинаковый математический смысл; byte SHA
документа и semantic identity остаются разными понятиями. Старые wire schemas
сохраняют прежние правила своих readers.

## Роли параметров

В новом Train comparison_radius_ticks, influence_absolute и influence_relative
из context_policy сохраняются для дополнительного прежнего v1 diagnostic/
witness codec и проверки допустимого диапазона. Они diagnostic_only: не являются
новыми Train geometry factors и не требуют sensitivity positive control как
изменение измерителя обучения. Geometry repeatability, declared windows, source,
common-context integrity и соответствующие budgets имеют отдельные роли.
Preflight возвращает эту классификацию; метод не использует v1 influenceExclusive
как решение нового Train. Legacy schemas1–3 сохраняют прежнюю v1 семантику.

Для cold6 condition binding имеет собственную schema2 (это не schema2 managed
pipeline). Только после полной проверки исходного cold6 из operative condition
исключаются ровно эти три diagnostic-only поля. Их значения и semantic digest
сохранены отдельно в supplementary_diagnostics; полный pipeline/job SHA также
сохраняется. Invalid radius/NaN не получают scientific identity через strip.
Geometry/source/model, context baseline/time/repeatability/native probe budgets
остаются в condition. Для cold1–5 прежний binding schema1 не меняется; перенос
идентичного binary в другой каталог по-прежнему не меняет condition fingerprint.

## Следующая интеграция и проверка

Пока не реализованы и не приняты learned package5/certificate2/full group
writer/readers, cold6 не имеет статуса рекомендованного научного контура.
Нужны versioned dispatch learned/stopped, полный перенос N+2 primary через
load_case/snapshot/native artifact closure и source/storage/model bindings.
Diagnostic schema1 record не становится TrainingCertificate2 из-за успешного
чтения или geometry recomputation. Portable import не восстанавливает livelease.

Semantic proof ID сохраняет declared run/trial/group/attempt identity против
replay; переименование filesystem paths при сохранении bytes/packet IDs не
должно менять его. Model semantic hash относится к фактическому полному graph,
SourceOrigin отдельно хранит initial target-family lineage. Ни один из них не
подменяется document SHA или выводится из одного scalar результата.

Frozen Test сохраняет свою whole-response/global maximum и actual spikes
семантику; Train assigned-window criterion туда не переносится. Перед отдельным
Test должны быть зафиксированы полный model hash и реальный проверенный порог.
Partial/stopped результаты diagnostic-only, без научного PASS.

Cold6/protocol4 declaration и condition projection проверены на M40: production
validation CLI,39/39 методов, failures/errors/skips0. Проверенный source root
`241159242f7c90d46c426c1009e04c103e560822`, evidence
`28f90a67a4bcc39df43f8f78235b088f5f65b960`.
416 исходных Python blobs совпадают с Git до/после; каждый member32-file
compact archive проверен отдельно (31096 bytes, SHA256
`bfa74259822e88d8a7b7ee372e8d300839059c5e1554a7637322794536287b9f`).
Worker owner PID/start совпадает с kernel binding, unit закрыт, leasereleased
штатным release(note). Зарегистрированный managed child graph не заявляется.
[Независимая metadata-сверка](CompositeTrainingPythonDeclarationVerification-20261108.json).

Это проверка деклараций/регрессий, не новых native measurements или обучения.
Все новые unit/native/pipeline проверки выполняются на серверах из Git-pushed
source; локально только AST/static review. Общий runtime должен собираться из объединённого C++service+
Python closure: старый compiled runtime не подтверждает поддержку cold6.


## Подготовка полного primary transport

Отдельный composite_primary проверяет embedded primary_blobs[SHA]={bytes,base64}
и каждый primary_ref={relative_path,bytes,sha256}. Embedded bytes обязательны;
если задан external resolver, каждая ссылка должна дополнительно дать те же
bytes: отсутствие или mismatch не заменяются fallback из другого источника.
Только точное множество referenced hashes, без скрытых/потерянных blobs;
канонический base64, полный SHA и размер. Повтор одинаковых bytes в разных
logical paths сохраняется. primary_bytes/materialized budget считает все
logical primary_ref, включая одинаковый SHA в разных paths; unique stored bytes
проверяются отдельно. Это согласовано с NativeCompositeRecordPrimaryBytes.

Файлы переносятся в новый snapshot byte-for-byte. Traversal, альтернативные
написания пути, case-collisions, file/directory conflicts и symlink ancestors
не допускаются. Некорректный inventory не создаёт output; существующий каталог
не переписывается. Helper и прежние regressions проверены на M40:51/51,
failures/errors/skips0, source root`bb489c3b3bb69b0d0aeda485350ce8a81ce42c5b`,
evidence`df9531926815565e7c5c1bc1e890c2dde34b5ccb`.
32 archive members/31816 bytes, SHA256
`2efa318d0d1974bcf6799e523c3c3db6b55e979eb8672a88af841e4bf83f5c61`;
418 точных Git source hashes, все outer/member hashes и owner/kernel closure
проверены отдельно. Операционный worker и supervisor byte-for-byte те же,
что в принятой39-suite; менялся только declarative specification.
[Metadata-сверка](CompositeTrainingPythonPrimaryVerification-20261108.json).
Storage integrity сама по себе не подтверждает геометрию, native execution, consumed event, source
lineage или certificate2. Archive/index/record reader и package5 dispatch
должны проверять их отдельно; helper не wired как готовый learned auditor.

## Подготовленный полный portable reader (следующий source chunk)

Новые composite_source/raw/measurement/certificate/package/summary auditors
проверяют immutable initial source, actual trained graph/storage, полные N+2
records, свежую геометрию объявленного окна и semantic proof/certificate IDs.
Standalone package5 самодостаточен: embedded primary обязательны, summary6
необязателен и не синтезируется. Legacy flat trial globs не используются для
новой версии. Явно переданный внешний mirror обязан совпасть byte-for-byte.
При native execution3 настоящий summary6 обязателен вместе с архивом, каждым
sidecar и полной рекурсивной artifact closure. Пути primary должны также
переноситься на Windows: запрещены control characters, trailing dot/space и
зарезервированные device names; переименование автоматически не выполняется.

Runtime search plan отделён от immutable cold declaration. Warm может менять
bounds/tolerances/budgets, но N0/N1 остаётся политикой исходного model family.
Partial records без native group context не подтверждают причину отказа или
полноту native closure и никогда не становятся reference/final/certificate.
End wall timestamp после mint не доказывает момент live deadline check.

Это source preparation. Полная native package5 → portable replay → import →
frozen evaluation приёмка требует общего runtime из согласованных C++/Python
commits и фактических артефактов producer. Hash-format fixtures и отдельная
проверка wire-ошибок не заменяют этот gate. Frozen Test продолжает использовать
общий максимум реакции и реальные spikes, не Train assigned-window criterion.

Wire/hash/dispatch и прежние декларационные проверки выполнены на M40:
62/62, failures/errors/skips0; source
`cdce8575f0467d0f173f83ab1ce3e9531fc3594b`, evidence
`4f4d40561750cee71f9cbf9a349a605d1084b819`.
428 Python blobs совпадают с Git до/после; все32 members компактного архива
проверены отдельно (32464 bytes, SHA256
`2389001756e3606ed0a568c04e17cf6fb2801c1bc55433734b78aa577c230856`).
Exact worker/kernel owner совпадает, unit закрыт, lease released штатно.
[Metadata-проверка](CompositeTrainingPythonPortableVerification-20261108.json).
Первый collector вызов отказал до записи из-за отсутствующего declarative
expected_source_files; повторная сборка evidence использовала то же завершённое
задание, тесты не запускались повторно. Native package5 позитивная приёмка,
реальные C0 fixtures и полная warm/pipeline проверка остаются открытыми.

Следующий warm/number/snapshot source
`29182db1fd8641e5cfef10ad0a9eebf219b1f7ed` проверен на M40:63/63,
failures/errors/skips0; evidence
`57f30ef87512f2f7052b2873d5d2ee91198069e5`. Все428 Python blobs и32 archive
members проверены независимо;32608 bytes, SHA256
`5d88a39333b90798f8704155427ff46b6f4dd48d3bd50ed43d3dffe498a65994`.
Worker PID2901337/start321349983, exact unit закрыт, lease released.
[Metadata-проверка](CompositeTrainingPythonWarmVerification-20261108.json).
Тест warm boundary проверяет consistency binding, не выдаёт native training
certificate. Полный positive native producer/import gate по-прежнему открыт.

Проверка initial dataset/readback и purpose-specific namespace добавлена в
source`b277540126acc74e8425d88865a6499ee515aa8b`; M40:65/65,
failures/errors/skips0. Evidence`c6c0abb1a81a6083a7a898c5ae27f50bac8e2173`:
все429 source blobs и32 archive members проверены;32672 bytes, SHA256
`525940acbc25396dc648b769011e40d7351b6a52b58437902bf3aae8e8af14c6`.
Exact worker PID2921881/start321394325 закрыт, lease released.
[Metadata-проверка](CompositeTrainingPythonDatasetVerification-20261108.json).
Отдельный test_composite_native_archive содержит7 проверок фактических шести
production exports; они не включены в эти65 и не выполнялись без native
fixtures. Для их отдельной приёмки нужны реальные Classic/Branch complete,
partial, ambiguous, existing-C0 и warm bundles с Git-bound fixture manifest.

Для package5 current dataset дополнительно должен semantic-совпадать с
initial source dataset после полного mask restore. Retarget либо сохранённый
omission mask не разрешены внутри этого family. Сравнивается identity.model;
raw XML может различаться из-за incidental dynamic serialization. Этот guard
подготовлен отдельно после65 source и требует фактической package5 приёмки.
