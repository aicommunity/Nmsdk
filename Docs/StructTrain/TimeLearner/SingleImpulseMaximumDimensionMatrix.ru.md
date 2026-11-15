# Размерная матрица SingleImpulseMaximum

Normal gate на Elder принят:9 native IDs,16 физических условий и10 readers.
ASan повтор на M40 также принят:9 native IDs,16 физических условий и10 readers.

Добавлены четыре native test groups: Classic/Branch ×2000/20000Гц. Каждый
проверяет N=1,4,6; прежние четыре N=2 cases сохранены отдельно. Это16
положительных физических условий и16 A/B пар, а не16 новых gtest IDs.
Пятая прежняя fault-группа проверяет три границы отказа для обеих топологий.
Адресный gate содержит9 gtest IDs и10 Python reader tests (прежние6+новые4).

C++ вызывает production native executor на настоящем storage/Environment
графе. Сравниваются все stimulus/soma samples между схемами4/5, часы с
прежним roundoff1e-12, физическая размерность, выбранный input, raw maximum
и запрет выдачи training certificate. Для Classic записываются все N сом,
для Branch — одна физическая сома с сохранением physical_input_count=N.
Выбран input0 при N=1 и input2 при N=4/6. Фиксированный training threshold100
объявлен до построения. Нормализация fixture — N1; N0 и другие профили этим
расширением не проверяются. CapturedPerInput и остальные defaults не меняются.

Четыре новых independent readers проверяют фактическое множество12 новых
условий, raw argmax, сохранность всех каналов/revisions в A/B и отказ при
потере физического канала. Прежний reader явно оставляет новые четыре
именных группы отдельному reader, сохраняя собственный ожидаемый набор
четырёх полных N2 captures и шести fault captures. Лишние неизвестные схемы
и неполный состав не считаются PASS.

Постановка серверной приёмки: normal9/readers10 на Elder, затем ASan9/readers10
на M40 после завершения и свежей closure/release прежнего ASan38. Нельзя менять
source/build активного задания. До фактических receipts это только новый
проверяемый код, не принятое расширение матрицы. Локально выполнен только AST
и source review; численные проверки выполняются на серверах.

Предыдущий ASan38 относится к Root038/Pulse217 и исходному N2 helper. Его
результат не переносится на новые N1/4/6 assertions автоматически. Полная
mandatory physics/mode matrix, full-burst assignment, convergence и научная
классификация остаются открытыми.


## Принятая normal-проверка

Compiled Root `e91b64cb2340ef1df01897db8dad81fc29bd1cf1`, PulseLib
`217dc53c4b1cc010ad6938852a91ee6d2df09e3c`. Evidence
`9f1557858d6f1b20485aefa439d194407d47f090`:
149 primary members/335060 compressed bytes, SHA256
`89888252aec28ef9312d47ef91913e373eb10a281e93be78d76fbfbe0db4def9`.
Native9 занял124.1s, без failures/errors/skips. Прежний fast observer unit
не перезапускался: слова unit34 в message evidence commit остались от шаблона
publisher и не описывают фактический scope. Это явно учтено в receipt;
исходный commit не переписан. Реальные counts подтверждаются JUnit и первичными
данными, а не текстом сообщения commit.

[Независимая сверка](SingleImpulseMaximumDimensionNormalVerification.json)
проверила149 members,499 Root/265 Pulse source hashes,9 original JUnit IDs,
10 reader outcomes,16 complete schema5 и6 fault captures. Полное множество
условий ровно Classic/Branch ×N1/2/4/6 ×2000/20000. Проверены model revisions
каждой schema4/5 пары,26 actual loaded-file records и125 bindings пяти прежних
runtime. Численные A/B/argmax проверки выполнены C++ и Python на Elder;
локально — только Git/archive/hash/JUnit/shape metadata.

Первая попытка остановилась до reserve/build из-за resource preflight.
[Обе неудачные подготовки и точная очистка двух code caches](ObsoleteSourceCacheCleanup-20261107.ru.md)
сохранены, пороги8GiB available memory/3GiB disk не снижены. Successful retry
имеет новую process binding; sources/runtime не менялись во время расчёта.

Дальнейшая ASan9/readers10 проверка использует этот же CPP/Pulse snapshot
и новые runtime/output paths на M40. Прежний ASan38 относится к исходным N2
cases и не выдаётся за новое подтверждение N1/4/6. Full-burst attribution,
N0/прочие physics profiles и полная научная матрица остаются отдельными.


## Принятая ASan-проверка на M40

Тот же compiled Root `e91b64cb2340ef1df01897db8dad81fc29bd1cf1` и PulseLib
`217dc53c4b1cc010ad6938852a91ee6d2df09e3c`, evidence
`3ebe18aab850a180d58f67a1e2cd2257551c07cc`. Native9:833.809s, readers10,
без failures/errors/skips. Повторено ровно16 положительных условий
Classic/Branch ×N1/2/4/6 ×2000/20000 и6 fault captures; unit34 не запускался.

[Независимая сверка](SingleImpulseMaximumDimensionASanVerification.json)
подтвердила149 primary members,340524 compressed bytes, SHA256
`e3266a18d5e6c0a9ea6c34a92d17d188d0df7319a7588e1e95a6c4b5bd57168d`,
499 Root/265 Pulse source hashes, JUnit и все16 условий. Инструментация
подтверждена compiler/link flags и фактически загруженной libasan среди73
loaded-file records. Проверены82 неизменённых bindings прежних runtime,
closure предыдущей группы до обновления source и свежая whole-group closure
с release текущего lease. Requested ASAN_OPTIONS=detect_leaks=0; live readback
этих options отсутствует, проверка утечек не заявляется. Поле ASan_verified=false
первичного terminal — оставшаяся константа producer, а не проверка flags/maps;
исходник сохранён, отдельная publication verification подтверждает ASan=true.

Это завершает адресную размерную проверку SingleImpulseMaximum. Не завершены
full-burst assignment и обучение штатной пачкой, N0/все физические профили,
Console под ASan, convergence и полная научная матрица. Никакой classification
PASS из этих инженерных проверок не выводится. Численные A/B/argmax выполнялись
на сервере; локальная независимая сверка читала только metadata/hash/schema.
