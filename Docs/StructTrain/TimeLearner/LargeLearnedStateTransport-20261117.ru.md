# Полная модель в отдельном файле native задания

Длинный cold Classic17 ноября сохранил полный stopped-state761851830 байт,
SHA256697861b86ffb0e265279e302c2548b1df4e13ae2073ac19bc6cdaefcce01373d.
Потоковая проверка неизменённого файла обнаружила792 Base64 значения суммарно
412386436 байт. Уже этот объём превышает прежний лимит ReadDocument256MiB
(268435456 байт). Удаление отступов оставляет499882681 байт. Поэтому одна
пересериализация не решает фактическую проблему переноса этой модели в Test.

## Формат и границы

Новый явный транспорт `checked-file-source-v1` не меняет learned-state schema,
математическую задачу или граф нейрона. Небольшой JSON envelope содержит
проекцию исходного задания и ссылку на полный локальный source-файл:

```text
kind = timelearner_checked_file_source_job
schema_version = 1
job = исходное signed задание без одного source-поля
source = field, relative path, bytes, raw SHA256, package SHA256
sha256 = канонический digest envelope
```

Разрешены только source_solo для export, source_recognition для evaluate,
source_stopped для diagnostic-evaluate. Обычный decoder получает прежний
полностью восстановленный объект задания и проверяет прежний resolved job
digest. История, первичные Base64 traces, metadata, storage definitions и
все прежние проверки learned-state сохраняются. Это не сокращённая модель,
не controller checkpoint и не способ получить сертификат завершённого Train.

Native reader сохраняет прежний лимит256MiB для обычного документа задания.
Отдельный source имеет объявленные точные bytes/SHA и верхнюю границу1GiB.
Неизвестные поля, роль источника, выход пути из input-каталога, symlink,
неверный размер, повреждённые bytes, package digest и resolved job digest
отвергаются до расчёта. Public text parsers learned/recognition state здесь
не расширяются; их согласование остаётся отдельной работой этапа5.

## Runner и provenance

Новый runtime объявляет поддержку в Console help. Новый worker обязан
проверить её перед чтением дорогого source; старый runtime не получает
неподдерживаемое задание. Без явного job_source_transport остаётся прежний
inline путь. Нет автоматического fallback после неудачной передачи.

Run manifest schema5 включает точный transport binding. Сохраняются обычный
input/job.json, исходный source snapshot, envelope и реальная аргументация
native процесса. Повторный audit связывает их с тем же resolved job SHA,
реальными input bytes и owned process binding.

Для recorded diagnostic case свыше512MiB требуются явные
maximum_source_raw_bytes≤1GiB и checked-file-source-v1. Default256MiB
сохраняется, legacy case ceiling остаётся512MiB. Такой большой case допускается
только с объявленными owner≥16GiB и native≥16GiB; общий reservation учитывает
их сумму. Это ограниченный ресурсный режим, не обещание отсутствия OOM.
Результат превышения лимитов сохраняется как execution failure.

## Проверка и ограничения

Восемь переносимых файловых/декларативных Python contracts прошли локально.
Полный прежний declaration suite использует Linux paths и требует запуска
на Linux: его попытка на Windows завершилась native_data_binding до проверки
case, не является приёмкой suite. Native C++ reader cases,
реальный Console capability gate, inline/file A/B обеих топологий и Test
фактической большой модели ещё не приняты. Модель Classic имеет outcome
budget_exhausted и не получает положительный TrainingCertificate из-за
успешной передачи. Его диагностическое распознавание оценивается отдельно.

Текущие работающие SDK/runtime не изменяются. Исправление границы бюджета
Pulse5dabcb1b и этот transport готовятся в новом изолированном runtime.
Разделение физической модели, истории и checkpoint по исходному плану
остаётся обязательным: этот совместимый путь снимает конкретный I/O барьер,
но не устраняет повторную загрузку больших историй и стоимость их аудита.

## Сверка после первой серверной сборки

Console собран на Elder из Root52ea097b/Pulse5dabcb1b. Файловые/declaration
и реальные capability проверки прошли26/26, включая отказ прежнему Console
без checked-file-source-v1. C++ выполнены86/86:85 прошли, один boundary test
содержал неверное ожидание domain action для исходного графа. Исправлен
только тест в Root0efbf25b; новая независимая SDK сборка и повтор86 ещё идут.
Нельзя объявлять исходный cohort86/86 успешно пройденным.

Сквозная проверка выявила отдельную несовместимость упаковки: новый run
manifest5 отвергался verify_packaged_run_inventory, допускавшим1…4.
Упаковщик теперь принимает5 только для трёх source-операций, с явным
transport binding и включёнными original job, envelope и полным source.
Его четыре переносимых integrity-контракта пройдены; это не native replay
и не подтверждение большого model roundtrip. Реальный архив должен дополнительно
пройти прежний production audit_run_manifest до проверки байтовой включённости.
