# Independent6 A2: бюджет полного восстановления

A1 остановлен owned_job_output_budget при распаковке568983084bytes в принадлежащий job TMP;128MiB ограничение не соответствовало размеру fixture. Итог A1 process_error, worker terminal отсутствует; завершённых test assertions нет. Source/fixture/шесть test IDs неизменны.

Здесь новый output и suite identity; maximum_output_bytes1GiB учитывает полный portable restore и отдельные corruption copies. Memory2GiB и1800s сохранены; physical free floor1GiB остаётся. Slot освобождён только после наблюдения closure старой группы. Это исправление эксплуатационного бюджета, не алгоритма/критерия/модели.
