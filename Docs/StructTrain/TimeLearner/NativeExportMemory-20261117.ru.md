# Память при экспорте: исправление и адресная приёмка 17 ноября

Потоковое вычисление канонического hash принято на реальных сохранённых
моделях. Последний OOM свежего длительного Train пока не закрыт: успешный
импорт готовой истории не воспроизводит пиковую память её создания.
[Исходная попытка и raw данные](FastN1GroupWall600OOM-20261116.ru.md).

## Изменения

PulseLib подаёт прежнее каноническое кодирование непосредственно в
QCryptographicHash, устраняя полный дополнительный QByteArray. UTF16-порядок
ключей, UTF8 framing, теги, binary64 и нормализация −0 сохранены.
Семантические hashes и формат пакетов не изменились. Сам JSON, наблюдения и
decoded proofs всё ещё находятся в памяти. Физика, lifecycle и математическая
цель обучения не менялись.

Uniform study принимает явные native memory/tasks; compatibility defaults
4 ГиБ/64 сохранены. Внутренний family reservation учитывает сумму ресурсов
Python-контроллера и native unit. Общий admission на сервере должен учитывать
эту сумму тоже: локальный registry этого не гарантирует. Новый длительный
Train требует закрыть этот ресурсный разрыв.

## Исполненные проверки

| Проверка на M40 | Результат и границы |
|---|---|
| SDK identity/revision/export | 20/20 без skip; пять независимых Python golden digests внутри native golden-case; штатные Build/Init и независимый replay export |
| Реальный package317475838 байт | Native hash1/1 при4ГиБ; прежний semantic digest, bytes/SHA входа до и после совпали; fixture проверена в actual request environment |
| Retained Classic | Import → Build/Init → export → свежий import; raw source175521654 байт; параметры, ledger и stimulus/Soma samples совпали |
| Retained Branch | Тот же путь, raw source192607805 байт; параметры, ledger и stimulus/Soma samples совпали |
| Декларации ресурсов | 2/2: разные Python/native caps, сумма, ошибочные и переполненные декларации |
| Controller/DATA join | 4/4 контрактных проверки плюс аудит реального native2: исходные JUnit, child bindings и три закрытые kernel groups |

Оба полных roundtrip сохранили первоначальный native лимит **8 ГиБ**. Большой
hash-control использовал **4 ГиБ**. Это воспроизведение остановленных состояний,
без нового Train, сертификата Exact и checkpoint поиска. Совпадение отклика
проверено до1e−12.

Первый SDK a1 не собрался из-за пропущенного старого вызова Canonical в
VerifyModelIdentity. Исправленный PulseLib9883f9493d0672e603dfb4a03dc572955469ccdf
собран в root9b7fb0eac7107093d2fd87748b85c532c4f2ad9e. Python actor большого
control и native2 — 2ede5702ca9e7dde7b18a5dea4667cbd99f75d52.
Большой control a1 остановился **до native исполнения**: reservation требовал
дерево, а не отдельный файл. Исправление резервирует parent, сохраняя точную
привязку fixture по bytes/SHA. Оба отказа сохранены в provenance.

Recorded hash-case закрыт существующим opt-in NMSDK_RECORDED_MODEL_INPUT_TESTS.
Для root536776b6d24f97b4b4b31ed360aab5dc3614133c выполнен GCC preprocessing
полного production C++ файла с ON/OFF: обычный golden-case есть в обоих режимах,
recorded-case отсутствует при OFF. Тело принятого native-case не менялось.
Это **не новая default-mode сборка** и не побайтовое сравнение preprocessed
output: метаданные GTest содержат изменившиеся номера строк.

## Исправление анализатора доказательств

Реальное native2 задание выполнило Branch перед Classic. Старый
audit_roundtrip_controller требовал список Classic→Branch и отвергал
корректный результат с roundtrip_controller_cases. Исправление
c62fe6e8e066b5d1be4a95bb15a61e02270ae2a2 проверяет точные пары name/test_id
без зависимости от порядка. Дубли, пропуски, посторонние ID, изменённые DATA
и чужие child bindings запрещены. Production auditor повторно связал тот же
исходный native2 набор с собственным контроллером. DATA replay намеренно
не выдаётся за новое native исполнение.

## Материалы и ограничения

[Компактная квитанция](NativeExportMemoryAcceptance-20261117.json)
содержит commit closure, результаты, времена фаз и внешние refs.
Каталог M40: `experiments/2026-11-17/native-export-memory/acceptance-a1.json`.
Primary93746136 байт:403 файла,221032776 байт после распаковки,
SHA256 `195c81cacbdda3c9170f2e1c2f080eb4fd698e482c372c0f5e746076dc143be5`.
Bundle `c4911d10b92a8c465176692ffb2df6e7a714110b74b4d5bfde8cf3f845957d6c`.
Provenance5612188 байт,
`baa771269004eac631b69658155dc5764cdefc152387e59f6f30d48b741ff420`.
Исходный317-МБ файл сохранён в отдельно указанном dependency archive.
Все группы закрыты до упаковки, regular files сверены по bytes/SHA;
symlink descriptors сохранены отдельно без обхода целей. Тяжёлые файлы в Git
не добавлялись.

Не заявляются ускорение, измеренный peak свежего Train или устранение OOM
попытки с759 raw probe pairs. До дорогого обучения нужны общий учёт
owner+sibling native ресурсов и сохранение конечной модели на репрезентативной
свежей истории. Разделение физической модели, истории и checkpoint остаётся
частью плана. Шаблонный Test и неполный TrainingCertificate запрещены.
