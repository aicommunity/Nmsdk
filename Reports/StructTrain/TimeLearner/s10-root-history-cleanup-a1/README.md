# Очистка истории корневого репозитория

Выполнена разрешённая замена origin и всех 14 корневых Git-копий на Windows,
Elder и M40, включая /home/user/Nmsdk и обе /home/user/tl-agent/Nmsdk.
Сохранены 253 рабочих дерева, восемь stash, приватные ветки и файлы на дисках.
Истории и gitlinks семи сабмодулей не переписывались.

Из исходной истории удалены 32 512 путей PNG/SVG/PDF под
Reports/StructTrain/TimeLearner, кроме primary-bundle/selected. Сохранены все
3413 исходных коммитов и исходные 315 публичных ссылок; у 175 коммитов изменился
SHA. Проверка каждого изменённого дерева подтверждает равенство всех оставшихся
blob/mode/gitlink; parent topology, author/committer и сообщения сохранены.
Код, конфиги, модели и первичные данные сохранены. Новые коммиты документации
и resolver являются обычным продолжением этой истории.

Origin заменён атомарно с force-with-lease. Его develop после первой публикации:
a67b1323a449255081c81ed47d4ccc1a368fc985. Дальнейший отчёт добавлен обычным
feature → develop merge commit. Полный старый mirror и verified bundle находятся
на M40, локальная и серверные metadata/bundle backups сохранены отдельно.

Свежий рекурсивный checkout из origin восстановил семь точных gitlinks и чистые
tracked trees. Приняты 25/25 проверок без skips/errors/failures; оба compact
primary bundles проверены, данные M40 извлечены losslessly. Первая попытка без
fixture environment дала три пропуска и не принята. C++ и научные прогоны здесь
не повторялись. scientific_verdict остаётся null.

Основной Windows object pack после проверки всех 70 349 live objects занимает
227.31 MiB вместо прежних 1.07 GiB плюс 248 MiB мусорных индексов. Worker caches
занимают примерно 223–241 MiB; рабочие изображения намеренно оставлены как
игнорируемый кэш. Это размеры объектов Git, не размеры рабочих каталогов.

Исторические SHA в scientific provenance не заменены. Разрешение старого root:
`python3 -m Scripts.StructTrain.TimeLearner history resolve OLD_FULL_SHA --root REPO`.
Карта находится в Docs/StructTrain/TimeLearner/History. Для исторического файла
сначала разрешить root SHA, затем читать его путь в соответствующем Git tree.
Старые исходные bundle доступны для точного исследования прежних commit objects.

Очистка не отменяет августовские визуальные 4/8–6/8 и не означает завершения
этапов 1–12 плана. PostTune/calibration, полный перенос режимов и научная
матрица остаются открытыми в текущем статусе рефакторинга.
