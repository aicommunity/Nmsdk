# Адресное редактирование конфигов Rdk

Рабочий подэтап 9, ветка `stage09/lossless-config-adapter`. Реализация и fixtures
прошли семь Python tests на каждом worker, включая корпус настоящих Project.ini.
Native baseline на M40 ASan воспроизвёл отказ BOM + declaration; исправление Rdk
прошло адресные проверки ниже. Runner/preflight и полная миграция старых
config generators этим документом не объявляются завершёнными.

`USerStorageXML::Load` использует native XMLNode parser. Он принимает числовые
имена узлов, например Project/Channels/00; обычный XML parser такое имя отвергает.
Новый `Scripts/StructTrain/TimeLearner/config_document.py` сохраняет исходные
UTF-8 bytes, включая BOM, CRLF, comments, attribute formatting и невыбранные
свойства. Повторная сериализация всего дерева не применяется.

`ConfigDocument` индексирует границы узлов; `TextEdit` требует полного пути от
корня, точного старого текста и нового текста. Для каждого сегмента пути требуется
ровно один match: дублирующийся sibling не выбирается по позиции. Изменяется
только содержимое существующего простого text leaf, со штатным escaping пяти
основных entities/числовых references при чтении и escaping `&`, `<`, `>` при
записи. Edits готовятся на неизменяемом source, применяются в обратном порядке
offsets, затем результат повторно читается и сверяется. Объект source не меняется.

Неизвестный путь, stale expected value, повторный edit, nonleaf, self-closing
leaf, mixed content/comment/CDATA выбранного leaf отклоняются. Остальные CDATA
и comments сохраняются без изменения. DTD, нестандартные PI, не-UTF8 кодировки,
неизвестные entities, некорректные tags/attributes, unclosed/multiple roots и
превышение лимитов документа/дерева дают явный отказ. Это консервативный адаптер
поддерживаемого диалекта, не замена всех возможностей XMLNode. Новые элементы,
storage-образы, insertion и замена структуры создаются штатными механизмами Rdk.

Текстовая запись `NaN` или имени несуществующего свойства сама по себе не
доказывает допустимость параметра. Следующий обязательный уровень preflight —
native load, проверка класса/capabilities, typed effective readback и применимости
фактора. Python text readback не считается effective component readback.

## Проверки

Подготовлены семь Python tests: byte-exact no-op, numeric names, адресность,
escaping/несколько edits, stale/missing/duplicate/nonleaf, повреждённые структуры
и entities, отказ для неподдерживаемого leaf markup. Корпус настоящих Project.ini
из Bin обязателен, не скрывается skip при отсутствии конфигов.

Отдельная native helper role `RdkConfigDialect.ExternalPatchedLeavesReadBackThroughNativeStorage`
читает созданные адаптером файлы через настоящий `USerStorageXML`, проходит
точные пути, проверяет match counts и декодированные значения. Без внешнего
request этот helper явно skipped; положительная приёмка требует запуска роли
с настоящим request. Это тест native serialization, не Train/Build/Reset и не
проверка уже применённой физики нейрона. Численные полные gates прежнего source
продолжаются в своих изолированных runtime и не покрывают этот новый source.

## Native baseline и исправление владельца

Root 7db4d9737 / Rdk 1812624f: первоначальный combined native readback завершился
failure. Отдельные диагностические вызовы того же binary подтверждают успех
трёх реальных patched Project.ini и отказ только synthetic BOM + declaration.
У synthetic сохранены Unicode/escaped values: удаление только BOM, только
declaration или обоих даёт успех. Исходные файлы и неудачная попытка сохранены.

Исправление в ветке Rdk `stage04/xml-utf8-bom` удаляет только начальную UTF-8
signature перед XMLNode::parseString. Обычный вход не копируется; исходный string
не меняется. Изменения Build/Reset/Calculate или learner-specific подготовки нет.
Две Rdk regression cases проверяют четыре сочетания BOM/declaration и отсутствие
корня/контента. Root `ccbf453f1d51638369c6b0afcf89cc1cbad166f4` / Rdk
`8ebf64dd39571cb6f95f23cfc2b55f30972c591c` прошёл на M40 ASan четыре выбранные
Rdk CTest groups и native readback четырёх файлов / одиннадцати значений.
Python source 7db4d9737 (Elder) и ccbf453f1 (M40) прошёл по 7 tests; все 1599
Project.ini корпуса StructTrain сохранены byte-exact. Их число также совпадает
с tracked files точного Bin gitlink. Native Elder/wide-platform проверка нового
serialization source здесь не заявлена; старый full gate root912/Rdk181 её не
подменяет.

Артефакты [M40](../../../Reports/StructTrain/TimeLearner/s09-config-m40/README.md)
commit `6210f02353cf2b3956a8a4ee93201607d870541a` (92 stored / 90 raw hashes) и
[Elder](../../../Reports/StructTrain/TimeLearner/s09-config-elder1/README.md)
`13c4328116f284d17b09d4af758b38e67e39a6fd` (6 / 4) опубликованы и сверены
локально. A1 сохраняет исходный parser failure; A2 — launcher syntax failure,
A3 — build disk exhaustion. A4 успешен после удаления воспроизводимых архивов
неудачных сборок и чистого временного clone уже опубликованного relocation.
Первичные данные не удалены; cleanup manifests включены в пакет. Low-disk событие
не позволяет принимать параллельный full run без независимой проверки полноты
каждого первичного наблюдения.
