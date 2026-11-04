# Очередь normal-приёмки общего lifecycle dispatcher

Это запись задания, не PASS. Worker2014816/start336763946 и supervisor2014804 на Elder ожидают исходный gate133, supervisor2006257. Проверены фактический queue.json и отсутствие исключения после запуска.

После успеха baseline133, полного закрытия его группы и освобождения operational lease worker создаст полный независимый SDK через Git objects, проверит все7 child gitlinks, отсутствие alternates и точное совпадение деревьев Tests/App/CMake с baseline802. Затем отдельная Release-сборка Test_PulseLib_StorageComponents и NeuroModelerConsole с parallel1 и native gate133. Исходный SDK802 не изменяется.

Фикстуры interruption controls восстановятся из опубликованного Git primary; skips не считаются PASS. Перед сборкой нужны12GiB свободно; reserve8GiB disk/8GiB RAM; весь worker ограничен8GiB/tasks128/24h. Очередь ожидает не более6h; native gate имеет собственный6h бюджет.

`job.json` содержит точные commits и readback. `orchestration.json.xz` сохраняет полную постановку без учётных данных. Полный304, A/B по реальным CSV/typed states, ASan и остальные режимы lifecycle остаются отдельными обязательными проверками. Не объединять Pulse candidate в develop на основании этой очереди.
