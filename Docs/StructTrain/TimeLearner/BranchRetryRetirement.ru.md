# Удаление исторических Branch br480 retry entrypoints

Два самостоятельных Python launcher удаляются из Bin без wrappers и копий:

- `SelectivityBranch/scripts/phase9_br480_mid_retry.py` — P4 silent-soma midpoint retry.
- `SelectivityBranch/scripts/phase10_br480_tipr_retry.py` — Phase10 Done/partial/Rmin TipR retry.

Полный старый путь каждого файла начинается с `Configs/SpikeSamples/StructTrain/`.
Точный retrieval snapshot Bin — `4af17aa240a7da0e30655a62c07cc4832e7253b9`.
SHA последнего изменения, blob SHA1, content SHA256, размер и `git show` command
зафиксированы в [source records](BranchRetryRetirement.sources.json) и общем
[migration manifest](script_migration.json). Это snapshot для извлечения кода,
а не заявление о том, какой commit исполнялся в историческом эксперименте.

## Почему эти файлы не переносятся как действующие инструменты

Оба entrypoints привязаны к старому `/home/user/Nmsdk/Bin/Platform/Linux`,
четырём входам и конкретной br480 кампании. Они меняют XML и порог вручную,
считают target первой строкой CSV и не проверяют полноту наблюдений. Phase9
не проверяет return code native процесса. Phase10 заменяет повреждённые
амплитуды нулём и при выборе midpoint исключает foil amplitudes выше target;
поэтому положительный локальный gap не является доказательством разделимости.
Это source findings; старые первичные данные здесь не пересчитываются.

Новый production путь использует immutable runtime, полный model transfer,
versioned observations и реальные calibration/evaluation probes. Исторический
same-matrix подбор остаётся явно отличным от независимого frozen Test.
Удаление старого launcher не означает эквивалентности всех старых CLI опций
новому контуру и не отменяет наблюдений исходного протокола.

## Потребители и сохранность

В точном Bin snapshot проверен поиск обоих module stems по всем tracked Python
и shell файлам: действующих вызовов/импортов не найдено. Две markdown references
Phase10 находятся в PHASE7_BRANCH_QUALITY и README конкретного Phase10 case;
к ним добавлена historical/retrieval пометка, исходный текст сохранён.
Конфиги, CSV, модели и журналы не меняются. Связанный `phase8_tiprmin_gate.py`
не удаляется: его вызывают другие оставшиеся legacy инструменты. Их миграция
остаётся отдельным открытым требованием полного этапа9.

## Проверка и приёмка

Manifest содержит107 records:105 retired и2 moved, `complete=false`.
До develop merge требуются production `history verify-migration` на обоих workers:
проверка всех107 records по Git trees/bytes и отрицательный fixture, который
возвращает один из удалённых Python paths при неизменённом manifest. Отказ
должен иметь `migration_old_path_still_present`, без положительного receipt.
Исторические скрипты не исполняются. Численные/ASan прогоны для этого удаления
не требуются; текущие научные jobs и их source/runtime каталоги не меняются.

Серверная приёмка завершена: Elder proof
`16aed3d1c348c067345f615156b8c4e8b9c91bab`, M40 proof
`08724250a23dcc03ab1181924d6eda1e4d1d9143`. На обоих workers прошли все107
records и restored-Python negative fixture. Независимо сверены все10 members
каждого архива, outer/member SHA256 и380 точных Git source hashes каждого.
Фактический scope-verification JSON подтверждает5 root paths/4 Bin paths,
два удаления и неизменность остальных blobs. Positive receipts byte-identical.

Исправление описания evidence: строка `bundle.scope` у обоих первичных пакетов
ошибочно сохранила числа17/14 от предыдущего шаблона публикации. Исполняемые
проверки использовали точные множества5/4; их actual scope-verification JSON
проверен отдельно. Нормативны эти первичные множества и данное исправление,
а не ошибочная строка. Исходные evidence blobs и их hashes не переписываются.
Ошибка текстовой сводки не объявляется проверкой более широкого изменения.

Полный перенос scripts, исходные этапы1–12 и весь план этим пакетом не закрываются.
