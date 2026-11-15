# Шесть реальных Console процессов: контроль пройден

Задание s07-burst-readback-console-six-m40-a4 завершено:1/1 integration test passed, внутри него6/6 Console процессов — Classic/Branch replay, matched no-op, changed Rs×0.75. Собственно тест210.264s, failures/errors/skipped отсутствуют. Внешняя группа и шесть дочерних групп закрыты; внешний и внутренний leases released. Raw records — completed-readback; замороженные controls — controls.

Console Root49689590cbdc0bbe5abccfb91374ad716f0ff977 / PulseLibdfb9a98244f91b4f4029d8470465fd40116436ca; Python actor Rootda64c4c7e3988289d6fc2fc314645ed3634ff8f1. Runtime fingerprint381d28bdf1e32674f9ad6698a095be29c89620cbdbf949952e624c72762cd019. Предшествующие A1/A2/A3 остаются отказами своих попыток.

Проверены полный native import, idle controller history, source references, semantic graph, свежие Rs domains, applied parameters, source/model immutability и целые окна фактических наблюдений. Для matched/changed совпали абсолютные timestamps, окна и actual input rows/events; warm baselines побайтно совпали, исходный replay равен warm baseline. L не изменились, изменённый Rs изменил model hash и потенциал. Максимальная абсолютная разность потенциала в обоих малых случаях составила0.0012052388484419252 native units; совпадение этого числа не доказывает эквивалентность двух топологий.

Это6 процессов и10 native observations: replay даёт одно, каждая intervention — baseline и main. Исторически названное поле result.native_probes=6 в acceptance schema1 считает процессы, не физические наблюдения. Указанное число нельзя переносить в training measurement counters.

Оба реальных случая N=2, physical bank owners=[0]. Совпадающие точки подключения Branch и N>2 этим runtime-набором не проверены. Обучение и назначение пика не выполнялись, certificate/classification verdict отсутствуют. Приёмка относится к этому readback контуру, не ко всему этапу7.

На основании этого контроля запущена [фактическая N4 серия L22](../M40L22BurstResistanceStudyA1-20261113/STATUS.ru.md). [Полные первичные данные контрольной группы сохранены в Git](../M40BurstReadbackA4PrimaryA1-20261113/RESULT.ru.md):712 members/179.89MB в1.07MB XZ, все6 процессов и10 observations.
