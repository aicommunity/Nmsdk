# Revision provider в native fixtures

Read-only аудит выявил отличие тестов от production: обычные schema2/3
fixtures передавали полный IdentifyModel в readModelRevision, который executor
вызывает до и после children на каждом тике. Полный путь создаёт JSON дерева,
повторно InspectModel(Structure) и canonical SHA. Production bindings и schema6
уже используют ModelRevisionObserver: фактические semantic inputs проверяются
каждый тик, полный hash повторяется при изменении. Независимые полные captures
на физических границах остаются обязательными.

Новый срез меняет только Test_PulseLib_NativeExecution.cpp. Typed provider
становится обычным путём; explicit fullRevisionProvider сохраняет дорогой
контроль. Injection RevisionFailure действует в обоих callback. Есть отдельный
readFullModelRevision и проверка минимум6 boundary calls завершённой пробы.
Нет проверки через каждый N-й тик, edit counter или доверия старому hash.

Full/Typed используют одинаковый storage profileName. Только artifact/run ID
Full-контроля получает `_full_revision`, чтобы не столкнуться в общем output.
Companion `.revision_reads.json` сохраняет tick reads, boundary reads,
observer full reads/cache hits, ticks, samples и wall time **первой** пробы.
Весь testcase может включать дополнительные reference/final probes; его
время нельзя делить только на число ticks первой пробы.

Добавлены4 Full-контроля Classic/Branch N2 на2000/20000 Гц. Приёмка ещё не
выполнена: нужна серверная A/B сверка всех stimulus/soma arrays, model hashes,
наблюдений и исходов с учётом явно различающихся trial IDs; чувствительные
контроли source/pattern/physics/lifecycle/reader failure; N6/2000 и ASan.
Ранее сохранённые Full-runtime и primary следует использовать как контроль,
не повторяя дорогую исходную матрицу без необходимости.

Таймаут прежнего Classic N6 ASan1200s не объявляется доказанным следствием
IdentifyModel. Подтверждён избыточный путь fixture; его вклад требует измерения.
Не меняются алгоритмы Train, допуски, окна, частота, routing, длительность или
размер научной матрицы. Активная серверная ASan-проверка использует прежний
неизменяемый снимок и этим локальным изменением не обновляется.
