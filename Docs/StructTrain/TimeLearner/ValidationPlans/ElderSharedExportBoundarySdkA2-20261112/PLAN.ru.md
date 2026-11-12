# Elder SDK102 A2: измеренный дисковый резерв

[A1](../ElderSharedExportBoundarySdkA1-20261112/STATUS.ru.md) прошёл canonical DATA, но native launch отвергнут до создания controller и lease: owned_native_capacity_preflight. C++ build/tests не запускались. Попытка сохраняется отдельно.

A2 использует тот же неизменный code subject Root c73575fe545b00cc7c9bf170c81c185c30b7026a / Pulse dfb9a98244f91b4f4029d8470465fd40116436ca, ту же Git namespace4160 и тот же список102 cases из A1; отдельные build/runtime/output/control names. Только disk reservation уточнён12→4GiB. M40 full build+runtime+частичный output после15 cases занимали589213696bytes; резерв4GiB даёт запас для оставшихся артефактов. Physical floor2GiB, memory8GiB, Release/O3/parallel2, whole21600s и все numerical/search/case conditions сохранены. Никаких изменений production runner/algorithms для обхода preflight нет.

Перед launch обязателен фактический свободный объём≥6GiB и закрытый canonical actor с released lease. Дополнительное место освобождается только удалением проверенных побайтно одинаковых XML materializations из двух уже выведенных из работы source-копий; каждая сохраняет исходник по явному keeper path. Уникальные данные и Git-история сохраняются. Если места недостаточно, launch запрещён. До build, фактического JUnit и closure/provenance checks A2 не принят.
