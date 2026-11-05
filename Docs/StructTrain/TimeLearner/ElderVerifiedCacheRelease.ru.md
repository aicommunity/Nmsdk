# Освобождение подтверждённых дубликатов и кэшей Elder

06.11.2026 удалены5159 файлов,1788657942 logical bytes:

- 3907 распакованных native файлов,1489206406 bytes, побайтно соответствующих
  опубликованному архиву завершённого normal304;
- 1252 промежуточных объекта компиляции,299451536 bytes, из старых
  `build-august-phasea-de02-a1`, `build-initial-threshold-normal-a4` и
  `build-n1-measured-refinement-normal-a1`.

Исходники, бинарники, библиотеки и CMakeCache не удалялись. Все19 файлов
текущего runtime `runtime-integrated-acceptance-normal-a1` сохранили hashes.
Объекты текущей integrated сборки не затрагивались.

## Доказательство дублирования

Канонические исходные данные остаются в Git commit
`25bbda5529caea24e8847973cd603d50b1b45826`, раздел
`Reports/StructTrain/TimeLearner/s10-elder-completed-gates-20261104/s07-csearch-threshold-joint-full-normal-a1`.
Архив11693180 bytes с SHA256
`e0b4dbc2ba7f34f1f0579b19309240842c7d31c0a1624656f61010d1fae2f94c`
сохранён также непосредственно в исходном readback на Elder.

Перед удалением проверены все3932 archive members, exact bundle hash,
каждый из3907 распакованных файлов и каждый объектный файл. Перед каждым
unlink повторно сверялись canonical path, regular-file type, inode, mtime,
размер и SHA256. Рекурсивного удаления каталогов не было. Полные file lists
и журнал каждого удаления сохранены в
[компактном primary](../../../Reports/StructTrain/TimeLearner/s02-elder-verified-cache-release-a3/bundle.json),
data commit `f8ef0f2187f30cf18eed12af8ae3a0de98aee1e9`:
24 members/330652 bytes, SHA256
`da937cfeebc2987e3b695e969afddc664e1d36fc25b835bf1906369c4d56bac7`.
[Независимая сверка](ElderVerifiedCacheReleaseVerification.json) сопоставляет
все удалённые дубликаты с каноническим Git manifest.

Исходный native process group был закрыт, его lease released; удаление
выполнялось под отдельной reservation. Две первые попытки остановились
на чтении защищённых proc paths до первого удаления. В окончательном проходе
явно идентифицированы и исключены только PAM/SSH helpers; это исключение
записано, их cwd/fd не объявляются проверенными. Прочие пользовательские
процессы проверялись отдельно; исходная экспериментальная группа закрыта
независимой kernel-проверкой.

## Восстановление и место

Каталог `readbacks/s07-csearch-threshold-joint-full-normal-a1/native-result/native`
теперь является освобождённым expanded cache. Перед использованием этого
старого пути как fixture восстановить соответствующие `native-result/native/`
members из сохранённого `primary.tar.xz` либо из указанного Git archive.
`CACHE_RESTORATION.md` в каталоге указывает источник. Первичные измерения,
модели и научные наблюдения доступны полностью; их содержание не менялось.

Свободное место сразу после операции:1394626560→3194073088 bytes.
Это замер на момент очистки: следующий normal304 уже записывает новые
артефакты. Его output budget1.75GiB, исходный запас не менее1GiB; monitor
запрашивает отмену только принадлежащего заданию native процесса при падении
свободного места ниже1GiB. Это не общий filesystem quota и не разрешение
очищать работающие задания.

## Следующий полный normal gate

В `s07-integrated-native304-normal-a1` на Elder запущен исходный304-case
набор на неизменённой SDK root `2e0618110a9abb48b94f6edc6b63c51f829ec810`,
Pulse `12d8c8a41c998ae1516496f716a0ae0f3d312b3e`, tool
`10d45ed93f08928a9992a3cf569c6a4938cdcd64`. Binary SHA256
`bcc51673ce59f1605567e7d8c998e6785ab978e0ff33c82aa116af39f52c9291`.
Source/build/runtime не обновлялись; native wall budget82800s и3600s на
завершение/архив, whole group86400s, cap8GiB/128 tasks.
Объявленный набор и численные допуски не сокращены. Результат неизвестен.
Это normal batch новой SDK; исходный normal304/ASan304 SDK802 его не заменяет.

Очистка не запускала модели. Она не завершает этап2 или общий план;
этапы1–12 остаются частичными.
