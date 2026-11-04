# C-search ASan K1:34/262/119,04.11.2026

Завершён старый неизменяемый SDK root `69789b8cb93dbc2ce44fe7a8d90aed758cf93f76` / Pulse `84e456d6fb551021e0222ebaf51fa313df2623b4` / Rdk `acc3de8d1af2480d61ddb723c3288f7e81003049` / Bin `4af17aa240a7da0e30655a62c07cc4832e7253b9`.34 адресных C++ tests и262 полного набора прошли без failures/errors/skips;119 production Python readers прошли на фактических outputs. Набор включает чистые controller/math cases и реальные Rdk/Pulse fixtures; это не262 независимых физических эксперимента. Targeted cases повторяются внутри full inventory, не считаются независимыми seeds.

Full native wall time41 770,98s (11ч36м11с), targeted4 450,62s. Все29 сохранённых process handles свежо проверены закрытыми; прежний operational lease уже освобождён. Legacy launcher удостоверял только launched executable/сохранённые handles и прямых children, не полный descendant cgroup. Его SDK использовал shared Git object handles; это не standalone/no-alternates приёмка нового контура.

## Полные первичные данные

[Bundle](../../../Reports/StructTrain/TimeLearner/s07-capacitance-full-asan-k1/bundle.json), [verification](CapacitanceFullAsanK1Verification.json), evidence commit `f3912fb5713020d6098847070378208d9d03d58d`. Все3293 исходных regular files сохранены в archive вместе с7 metadata records:3300 members,1 374 329 159 uncompressed bytes,8 942 492 compressed bytes. SHA256 `5aa0b90de9486a1215406abbe39bda618b74bf9cc209c8f714af38cc28bc2f34`.

Archive создавался отдельно с ограничением512MiB, чтением завершённых outputs и без запуска/остановки нейронных моделей. Архиватор подтвердил input hashes до и после упаковки; его kernel group закрыта, отдельный metadata lease освобождён. Runtime/source действующих заданий не менялись. Первичные JSON/CSV, models, native XML/results и119-reader report доступны из чистого Git checkout; крупные производные изображения не добавлялись.

Локально выполнены только metadata/hash/archive проверки:28 published checksums,3300 members, точные native IDs classname/name и counts34/262, reader119,306 Root Python/C++ и263 Pulse source blobs по соответствующим commits. Первая локальная попытка использовала неверный разделитель ID и слишком раннее чтение metadata cache; это исправлено после завершения extraction. Ни серверные тесты, ни их артефакты не менялись. Локальные численные тесты не выполнялись.

## Границы результата

ASAN_OPTIONS=detect_leaks=0. Проверка не доказывает отсутствие утечек. Прежний launcher не сохранил окончательный native RSS/cgroup peak; исторические наблюдения около31GiB RSS — нижние границы, не итоговый максимум. Причина большого расхода памяти не установлена. Не уменьшать число tests, model/search budgets или tolerances, чтобы скрыть расход ресурсов.

Это отдельный code snapshot: его PASS не принимает автоматически совместный root802/Pulsecc с initial-threshold/Rdk изменениями, общий lifecycle8644 или весь алгоритмический release. Научная классификация, stock4-input/8-pattern матрица, order/ITI, независимый Test и влияние LT-мембраны этим не доказаны. Августовские4/8–6/8 сохраняются в исходном протоколе.

## Следующая совместная ASan проверка

Native44 реально работает на SDK root `8021301e894368aefd045f9d77274fcce9f60245` / Pulse `cc97149c90ce98ff24ca688452f4a40d54e0e63d`; supervisor3836828/start286684788, отдельный native process3979458/start288797241. Прежний K1 не перезапускался.

[Поставлен полный304](../../../Reports/StructTrain/TimeLearner/s07-joint-asan304-queued-a1/job.json): queue owner3991393/start288960902 ждёт фактических44 PASS, свежего whole-group closure и registry release через принятый worker_dependency API. Ожидание идёт до старта bounded native unit. Runtime/source повторно используются read-only, compilation/update отсутствуют; каждый из304 прежних IDs и native timeout86400s сохраняется.

Для полной unit выбран hard memory cap42GiB при физической памяти M40 около47GiB: вне cap остаётся около5GiB системы. Перед стартом требуется MemAvailable≥42GiB и disk free≥14GiB. Это ограничение по ресурсам сервера и прежнему наблюдённому RSS lower bound, а не якобы измеренный final peak K1. Monitor будет сохранять memory.current/peak/swap/events; после native завершения читаются точный lifetime cgroup peak при живом owner и largest reaped child rusage. OOM/timeout не может превратиться в PASS. Общий24h computational envelope начинается после очереди и включает подготовку/архивирование; отдельный native declared limit остаётся24h.

После фактического304 нужны публикация полного primary, fresh ModelSpec2 owner replay8, readers128 и приёмка общего code slice. Эти gates ещё не выполнены; очередь не означает PASS. Остальные modes/profiles/lifecycle/storage, production ConditionSpec/queue/publish и научная матрица остаются открытыми. Полностью принят только этап0 исходного плана.
