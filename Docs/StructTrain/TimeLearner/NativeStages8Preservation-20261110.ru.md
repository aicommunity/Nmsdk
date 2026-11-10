# Полное сохранение stages8 — 10.11.2026

SDK Root `24fd3778a793f2fdb57bc09ef3c7a4b4f70da9f9` / Pulse608 / Bin8cb /
Rdkd6 завершён **7 executed / 3 PASS / 4 fixture FAIL / 1 not-run**.
Stage trace и Fresh Load на 2000/20000 Гц прошли. Connected/Detached
случаи ошибочно добавляли generator child в мембрану и завершались до Load.
Это сохранённый отрицательный результат постановки, не доказательство
неисправности Rdk. Последующая исправленная диагностика описана в
[NativeLoadXmlPreimage](NativeLoadXmlPreimage-20261110.ru.md).

[Полный compact primary](../../../Reports/StructTrain/TimeLearner/s04-native-stages8-preservation-m40-a1/packed/primary.tar.xz)
содержит 129 originals / 132 members: исходные JUnit, stage trace,
configure/build logs, source/runtime inventories и controller/process records.
Исходные файлы 21920781 bytes, expanded 22682165 bytes, архив 1472420 bytes,
SHA256 `c0e777b5d460db306c0502bb13c11f756be84ad2964fee937dd7dab9c9ddb010`.
Бинарники и build objects не добавлены дублями. Источники M40 сохранены.

[Независимый reader](../../../Reports/StructTrain/TimeLearner/s04-native-stages8-preservation-root-observation/independent-schema3.json)
проверил все members/hashes, 4073 SDK blobs, 651 collector files, семь
реальных JUnit IDs и исходный отрицательный итог.
[Kernel/lease readback](../../../Reports/StructTrain/TimeLearner/s04-native-stages8-preservation-root-observation/fresh-closure-and-lease.json.gz)
подтверждает отсутствие supervisor, закрытие outer/двух children и released
original/collection leases. External cgroup коллектора отдельно не аттестован.

Evidence `a7c8a595fe779a6bf132547c5675e961640626f7` опубликован, exact origin
ref проверен и принят через `merge --no-ff`; maintained Pulse4a не заменён
непринятым candidate608 ради публикации отчёта. Measured closure определяется
первичными manifest. Никакой новый научный PASS этим сохранением не заявляется.
