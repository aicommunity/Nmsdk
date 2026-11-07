# Windows: владение процессами и подготовка третьего worker

Статус: 12/12 адресных проверок production `windows_process.py` пройдены
на 10.245.1.14. Полный научный pipeline Windows ещё не принят.
Эти проверки запускают процессные Python fixtures, не модели Nmsdk.
Пользовательский `C:/Projects/Nmsdk` не изменялся.

## Контракт

Процесс создаётся приостановленным. До первого исполнения ему назначаются
отдельный Windows Job Object, лимит суммарной committed virtual memory,
лимит числа процессов и KillOnJobClose; настройки читаются обратно.
Владение связано с PID, creation FILETIME и фактическим executable.
Остановка затрагивает только этот Job. Лимит процессов не ограничивает
число потоков. Один byte-range lock сериализует наши задания на worker,
но не резервирует память против других приложений пользователя.

Wall budget включает подготовку. Исчерпание бюджета до старта и заранее
созданный cancel не возобновляют ребёнка. Неполученная карта DLL остаётся
`provenance_missing`, даже если остановка процесса выполнена правильно.
Наблюдатель сохраняет реально обнаруженные модули основного процесса,
проверяет их файлы и неизменность source/runtime после исполнения.
Это дискретное наблюдение, не полная история загрузчика всех потомков.

## Проверки и исправления

Исходный запуск A3: 7/10, три ошибки сохранены в evidence
`1d704e42bd402bdf6b1d3ff3c59f9ed0ba904a13` (103 members, 11660 bytes).
Исправлены проверка бюджета до создания процесса, явное отсутствие
provenance при ранней остановке и некорректное ожидание теста о peak counter.

A4 на root `8d54506e6fabb140cf89ed128272110943f7b50f`: 12/12,
23.459 s, без skips/errors. Проверены Unicode/аргументы, exit259,
повреждение runtime, повторное занятие lock, отмена до/после запуска,
timeout до запуска/после capture, удаление оставшегося потомка,
некорректные лимиты и парный контроль памяти. Выделение 512 MiB отклонено
при 128 MiB и успешно при 768 MiB. Сырой peak counter сохранён;
из его значения не выводится недокументированная причина или граница.
Семантика лимита: [Microsoft Job Object limits](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information),
[committed memory и counters](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information).

Все десять созданных A4 Job Objects после закрытия независимо проверены
через OpenJobObject: отсутствуют либо пусты. Task Scheduler завершился
с кодом0, активных экземпляров нет. Исходное полное C++ дерево неизменно.
Однократный S4U task использован, поскольку первый запуск с отделением
от SSH не создал каталог задания; пароль в task не сохранялся.
Неудачные A1/A2 launchers также сохранены как данные, вне active Scripts.

Evidence A4: `87bb988fe406300885651bb8b9d53187e83130ff`,
134 members / 12800 bytes, SHA256
`7b472d551e6917ce50a52781970c5748e939796d728cbb9f036b61ddd7d6c468`.
[Независимая metadata-проверка](WindowsExecutionVerification.json)
подтверждает hashes каждого archive member, точные результаты тестов,
production backend против Git, source closure before/after и закрытие Jobs.
Никаких локальных численных тестов не выполнялось.

## Оставшаяся подготовка

В root `8314e98f7dbd93441d81de32e7c7174f0fafac24` добавлены C++ Windows
ready/ack schema2 с creation FILETIME и явная Windows schema4 native gate:
отдельные process limits/worker lock, обязательный capture и закрытие Job.
Linux schemas1–3 сохраняют свои контракты. Граница capture не вызывает
Calculate/Reset и находится после вычислений, до выхода процесса.

A5: 16/16 процессных/protocol controls, 28.503 s, без skips/errors.
Дополнительные проверки: корректный обмен, отказ при подменённом PID,
неполученная граница не является provenance, строгая форма Windows spec.
13 созданных Jobs независимо проверены после закрытия. Обмен в этом наборе
проверялся Python protocol fixture; проверка настоящего C++ ещё требуется.
Evidence `1b780a4ce74c92a6bd74da5690ce7e94429e9dcf`:174 members /15460 bytes,
SHA256 `e6e16fe725a15296f52b5b399f3483f0e02c75fd9d86b92ee8c04dff20037e7f`.
[Metadata-проверка A5](WindowsCooperativeVerification.json).

Подготовлен отдельный build/native job `windows-assigned-sdk-a1` на .14:
тот же root8314/PulseLib9e064, переиспользование закрытого build cache,
новый runtime, compiler parallelism1, build Job4GiB/32processes,
native Job3GiB/1process, unit23 и physical21. Прежний runtime-a6 проверяется
до и после; исходники обновляются только после закрытия предыдущих задач.
Сборка и C++ regression этого job ещё не приняты.

Нужны успешная сборка актуального согласованного SDK с guard исправлением и
повтор native regression набора. Затем — полноценный Train/export/frozen Test,
provenance и публикация. До этих проверок Windows не получает научные jobs.
Отдельные базовые процессные controls не закрывают этапы2/10/11 плана.
