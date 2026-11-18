# Межплатформенное сравнение storage-образов

18 ноября: причина исходного `recognition_images_changed` установлена по
сохранённым файлам Elder/Linux и Windows, без повторного Train или Test.
Исправление DATA-аудитора проверено:11/11 серверных regression tests PASS,
без failures/errors/skips. Полный повторный аудит исходного Test выполняется.

Исходный stopped source958170225 bytes имеет SHA
`57a8934db33b34ec819440f677a4cd1af6109df2813068356cec3ea55357cccd`;
выданный Windows recognition model1024210756 bytes —
`77df76219c87a8fcf868d09d47de359115b40a798db40f8bba7009605de64dfe`.
До/после чтения оба файла неизменны. Все31 образов имеют один проверенный
semantic fingerprint:
`9412aafd8b840e93dc2c0d9c91377a145e667798a378e0701648767f7e71e591`.
Имена/порядок образов и все не-XML поля совпадают. В XML различаются имена
типов RTTI: i/int, b/bool, j/unsigned int, d/double, x/__int64,
MDMatrix и MVector с теми же элементами, а также compiler-dependent
elemType/elemVecType.77 полей DebugSysEventsMask меняются4294967295→2147483647.
Это диагностическое поле явно исключено из физической identity в
PulseLib Core/TimeLearner/ModelIdentity.cpp, Excluded. Оно не маскируется под
равенство численных значений.

## Исправление

recognition_evidence, auditor version3 сравнивает storage по тому же
семантическому контракту, что native ModelImageDefinitionsFingerprint:
полный набор имён, kind/base, зависимости, все typed параметры/связи/частоты
эффективных snapshot models. Обе стороны сначала проходят общий `_images`:
проверки XML SHA, identity SHA, derived dependency sets и closure. Дополнительно
сохраняется равенство остальных snapshot fields, включая component_class/name
и полный identity envelope. Порядок перечисления зависимостей не физический
параметр. Изменение C, R, классов, частоты, связей или class selectors остаётся
отказом, даже если атакуемый/повреждённый DATA документ переподписан своим hash.

Это проверка деклараций DATA, не доказательство исполнения или native XML.
Отчёт явно содержит `native_xml_reconstruction_verified=false`, а общий
recognition reader сохраняет `native_import_verified=false`. Нельзя выводить
фактическую динамику из одних совпавших JSON identity. Native PrepareModelArchive
по-прежнему загружает **каждый** переданный XML образ через LoadSnapshot и
проверяет эффективную identity; эта production проверка не изменяется.
Подтверждённый native roundtrip исходного Elder source остаётся отдельным
свидетельством, его нельзя приписывать arbitrary DATA-файлу.

## Проверка

Подготовлены11 серверных проверок на фактической31-image паре:
Linux→Windows, same-wire, independent order, изменённые C/frequency/binding с
новым digest, lost/duplicate image, потерянная dependency, подменённый root
class, неверный XML SHA, неизвестное snapshot поле. Никакие native fixtures
не создаются искусственно и не заменяются тестовыми телами функций.

Полный повторный аудит восьми уже рассчитанных наблюдений выполняется только
после этих проверок. Исходный отказ auditor version2 и его traceback сохраняются.
Новый Train не нужен; успешная классификация заранее не предполагается.
Изменение не закрывает этапы3/5/8 или весь план и не исправляет отдельный
terminal best-state restoration этапа7.

## Серверный результат

Windows `windows-recognition-image-portability11-a2`, controls
`9a07113b8c7336433757ad8c0edea129328eb7cb`, Python source Root
`72071842c9abcb65d9e177d92c675106ef4e41dd`:11/11 PASS,0 failures/errors/skips.
Все source/recognition fixture fingerprints до/после совпали. Owned Job
завершён exit0/valid, все процессы закрыты;32 загруженных файла зафиксированы.
[Квитанция](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/storage-image-portability11-observed.json).
Исходный A1 завершился до тестов: строгий object-reader был ошибочно применён
к JSON массиву. Fixture переведена на штатный строгий JSON value-reader;
production алгоритм между A1/A2 не менялся.
[Сохранённый A1](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/storage-image-portability11-a1-rejected.json).

Полный read-only audit всех исходных8 наблюдений выполняется в отдельном
`windows-elder-baseline8-audit-recovery-a1`, controls
`baaddde3fe0fe38d4cdeb40ca9f2f57d08627826`. Подтверждён live native Windows
Job `Local\TimeLearner-ce42dd6b-a70b-4b8b-9eb8-69858eb5024a`, PID13468,
creation_filetime134394930757956066, Python3.14.2, лимит20GiB/32 processes/3600s.
Это повторный DATA-аудит, не повторный native Test и не новое обучение.
[Наблюдение процесса](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/baseline8-audit-recovery-running.json).
