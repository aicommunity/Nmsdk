# Межплатформенное сравнение storage-образов

18 ноября: причина исходного `recognition_images_changed` установлена по
сохранённым файлам Elder/Linux и Windows, без повторного Train или Test.
Исправление DATA-аудитора подготовлено; серверные regression tests и повторный
полный аудит исходного Test ещё не приняты.

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
