# Полная модель в отдельном файле native задания

**Последняя проверка:** actual inline/file native A/B обеих топологий пройден,
2/2 full-wave comparisons и17/17 последующих archive/contracts без skips.
[Сводка с refs и ограничениями](CurrentStatus-20261117.ru.md).
Ниже промежуточные записи сохраняют хронологию; их «ещё не принят» заменяется
этой сверкой только для названного объёма. Большие761/678MB модели ещё
не прошли actual Test, разделение модели и истории остаётся открытым.

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

## Промежуточная сверка после первой серверной сборки

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

## Подтверждение на14:54 UTC

Повторная независимая сборка SDK Root0efbf25b/Pulse5dabcb1b завершилась:
86/86 выбранных production C++ случаев пройдены без skips/failures.
Объединённый Root685f2d2e Python набор прошёл39/39 на Elder, включая прежние26,
девять common-window DATA и четыре archive-inclusion контракта. Все группы
проверок закрыты, leases освобождены.133 файла metadata сохранены в M40 archive,
затем все133 восстановлены с побайтовыми hash-проверками.
Квитанции: Reports/StructTrain/TimeLearner/NativeSourceTransport-20261117.
Это проверка metadata архива, не roundtrip физической модели.

Реальный native inline/file A/B двух полных сохранённых short cold N4 моделей
запущен на Elder как s05-file-source-ab-native-elder-a1:32 полных предъявления,
заранее фиксированные прежние diagnostic пороги и один SDK0ef для всех cases.
До завершения и сравнения всех фактических waveform/spike/model данных его
приёмки нет. Большие модели длинной пары ещё не проходили этот Test.

## Найденная на фактическом A/B граница string/Path

Первый inline Classic выполнил все8 проб валидно, TP1/FP6/FN0/TN1, как прежний
short-cold readout. Затем file-case отказал до расчёта: native DATA передаёт
runtime path строкой из JSON, а ранний load ожидал Path. Общая попытка a1
не принята; результаты Branch/file в ней отсутствуют. В run_case добавлена
нормализация Path до capability gate. Новая регрессия вызывает production
run_case со строкой и реальным legacy Console: он должен получить штатный
отказ отсутствующей возможности до чтения source, без создания output.
Прежний39-test PASS не покрывал эту границу. Новый40-test набор Roote31ff3043
прошёл на Elder без skips/failures. Оставшиеся24 A/B наблюдения запущены отдельно
как s05-file-source-ab-native-elder-a2, controls
54b66a14089982903b2df78811ac98d13dea195f. Валидный Classic-inline8 сохраняется.
Новый запуск использует исправленный tool, прежний immutable native SDK0ef и
тот же runtime fingerprintd480a889…; результаты всех условий ещё не сравнены.
Первый launcher этой подготовки не прошёл capacity preflight до создания
процессной группы. Допущенный controls54b ограничивает оставшийся output1ГиБ
по измеренному baseline264347648 байт, сохраняя floor2ГиБ. Это изменение
ресурсного допуска; при переполнении лимита результат не может стать PASS.
