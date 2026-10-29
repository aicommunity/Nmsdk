# Адресное редактирование конфигов Rdk

Рабочий подэтап 9, ветка `stage09/lossless-config-adapter`. Реализация и fixtures
пока ожидают серверного выполнения. Runner/preflight и полная миграция старых
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
